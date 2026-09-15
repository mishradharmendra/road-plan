# OpenSearch retrieval cluster

Terraform for the online retrieval tier in [ADR-001](../../../docs/ADR-001-retrieval-architecture.md).
Index bodies are **not** managed by Terraform — index mappings change on a different
cadence than infrastructure, and encoding them in state turns a mapping tweak into a
plan/apply on a production domain.

## Apply

```bash
terraform init
terraform apply \
  -var environment=dev \
  -var vpc_id=vpc-xxxx \
  -var 'subnet_ids=["subnet-a","subnet-b","subnet-c"]' \
  -var 'ingress_security_group_ids=["sg-ecs-rag"]' \
  -var 'allowed_principal_arns=["arn:aws:iam::ACCOUNT:role/rag-api-task"]' \
  -var master_user_arn=arn:aws:iam::ACCOUNT:role/rag-search-admin
```

The domain is VPC-attached and reachable only from the listed security groups, so all
commands below run from inside the VPC or over VPN.

## Bootstrap the index template

```bash
export OS=$(terraform output -raw endpoint)
awscurl --service es --region us-west-2 -X PUT "$OS/_index_template/chunks" \
  -H 'Content-Type: application/json' \
  -d @index/chunks-index-template.json
```

## Hourly rebuild and blue/green swap

The read alias is what the application talks to. Builds are immutable and swapped
atomically, which makes rollback a single API call rather than a re-index.

```bash
BUILD=chunks-$(date -u +%Y%m%d%H)

# 1. create the build index (picks up the template)
awscurl --service es -X PUT "$OS/$BUILD"

# 2. bulk load from the Delta batch job, then make it searchable
awscurl --service es -X POST "$OS/$BUILD/_refresh"
awscurl --service es -X POST "$OS/$BUILD/_forcemerge?max_num_segments=1"

# 3. gate on retrieval quality BEFORE the swap
python -m ragkit retrieval-eval \
  --config eval/configs/retrieval.opensearch.json \
  --provider opensearch

# 4. atomic swap - old and new never both serve
awscurl --service es -X POST "$OS/_aliases" -H 'Content-Type: application/json' -d "{
  \"actions\": [
    {\"remove\": {\"index\": \"chunks-*\", \"alias\": \"chunks-read\"}},
    {\"add\": {\"index\": \"$BUILD\", \"alias\": \"chunks-read\"}}
  ]
}"
```

Rollback is the same call with the previous build id. Keep the last two builds; delete
older ones once `KNNGraphMemoryUsage` has settled.

## Operational notes

- **`KNNGraphMemoryUsage` is the alarm that matters.** When graphs are evicted the
  cluster stays green, nothing is logged as an error, and p99 latency quietly triples.
- **`force_merge` before the swap**, never after. Merging while serving doubles graph
  memory transiently and is the usual cause of a mid-day latency cliff.
- **Do not enable `_source` exclusion on `text`.** Reranking and citation display both
  read it, and re-fetching from S3 costs more than it saves.
- `refresh_interval` is 60 s and translog durability is `async` because the index is a
  derived artefact — the system of record is Delta on S3 (ADR-001 / D3).
- Verify quantization actually took effect after a mapping change:
  `GET $OS/chunks-read/_stats/segments` and confirm the on-disk vector size is ~1/32 of
  `count x dimension x 4` bytes. A silently-ignored `mode` field is an easy miss.
