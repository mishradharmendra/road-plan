# agentic-rag

Retrieval platform for NLP search and question answering over ~10M enterprise documents
(~200M chunks). Design and rationale: [docs/ADR-001-retrieval-architecture.md](docs/ADR-001-retrieval-architecture.md).

The one rule: **application code depends on `RetrievalProvider`, never on a vendor SDK.**
That is what makes "not vendor-locked" a property of the codebase instead of a slide.

```
ragkit/
  types.py               SearchRequest / SearchHit / Filter — no vendor types, ever
  provider.py            the RetrievalProvider contract + registry
  fusion.py              client-side RRF, identical across providers
  embeddings.py          HashingEmbedder (offline CI) + HttpEmbedder (OpenAI-compatible)
  metrics.py             recall@k, precision@k, nDCG, MRR, Wilson intervals
  evaluate.py            Phase-0 retrieval eval + the bridge into evalkit
  providers/
    memory.py            BM25 + cosine reference implementation, zero deps
    opensearch.py        production read path: binary quantization, single _msearch
    pgvector.py          portability insurance + the 10M doc-summary tier
eval/
  corpus/                sample corpus
  datasets/              golden retrieval queries
  configs/               memory / pgvector / opensearch
infra/terraform/opensearch/
  main.tf variables.tf outputs.tf versions.tf
  index/chunks-index-template.json
tests/test_portability.py
```

Python 3.10+. No dependencies for the default path. `psycopg[binary]` only for pgvector,
`botocore` only for SigV4.

## Run it

Nothing to install and nothing to start — the default config uses the in-process
`memory` provider and loads the sample corpus on each invocation.

```bash
cd agentic-rag

# poke at it by hand
python3 -m ragkit search --config eval/configs/retrieval.json --query "AUTH-5031"
python3 -m ragkit search --config eval/configs/retrieval.json          # REPL
python3 -m ragkit search --config eval/configs/retrieval.json \
  --query "daily meal allowance" --filter version_status=current --mode lexical

# Phase-0 retrieval eval — this is the per-PR gate
python3 -m ragkit retrieval-eval --config eval/configs/retrieval.json

# provider contract + portability suite
python3 -m unittest discover -s tests -t . -v

# feed real retrieved context into the existing LLM eval harness
python3 -m ragkit retrieval-eval --config eval/configs/retrieval.json \
  --export-evalkit eval/datasets/e2e_from_retrieval.jsonl
```

Current baseline on the seed set (22 queries, 24 chunks, offline hashing embedder):

```
    k    recall   precision      ndcg   hit_rate            95% CI
    1    0.6750      0.6364    0.7071     0.6364   [0.430, 0.803]
    5    1.0000      0.1909    0.8745     0.9091   [0.722, 0.975]
   50    1.0000      0.0191    0.8745     0.9091   [0.722, 0.975]
  MRR 0.7515
```

Those numbers measure the **pipeline**, not retrieval quality — `HashingEmbedder` models
lexical overlap only, and 22 queries produce a 95% CI wide enough to swallow most real
regressions. Point the config at a real embedding endpoint and grow the golden set to
500–1000 queries before quoting anything.

The one result that already means something:

```bash
python3 -m ragkit retrieval-eval --config eval/configs/retrieval.json --mode lexical
#   query_type=reasoning  recall@50 0.5000
#   total misses (1): q-008
```

Lexical-only retrieval loses `q-008` ("Who signs off an invoice for 80000 dollars?")
because the answer document never says "80000" — it says "above 50000 USD". Hybrid
recovers it. That single query is the argument for D6 in the ADR.

## Two harnesses, on purpose

| | what it gates | when | where |
|---|---|---|---|
| `ragkit retrieval-eval` | Recall@k, nDCG, MRR, latency | every PR | this package |
| `evalkit` | answer correctness, groundedness, citations, abstention | nightly | [../evals/harness](../evals/harness/README.md) |

Retrieval failures are unrecoverable — no reranker or LLM fixes a document that was
never retrieved — so they are gated first, cheaply, and deterministically. Generation
quality is then judged against **real** retrieved context via `--export-evalkit`;
evaluating a generator on hand-curated context measures a system nobody ships.

## Adding a provider

1. Subclass `RetrievalProvider` in `ragkit/providers/`, `@register` it.
2. Translate `Filter` into the engine's own pre-filter. Never post-filter ANN results —
   it silently destroys recall.
3. Add it to `tests/test_portability.py` with an env-var skip guard.
4. Run `retrieval-eval --provider <name>` and compare against the memory baseline.

Filter fields are allowlisted per provider and every value is a bound parameter; see
`Filter.validate` and `PgVectorProvider._where`.

## Not built yet

This is the retrieval spine, not the whole system. Still to come, in ADR phase order:
document parsing and chunking pipeline (Databricks), the cross-encoder reranker service,
the agent router and its two-tier latency budget, and the abstention/citation gate.
