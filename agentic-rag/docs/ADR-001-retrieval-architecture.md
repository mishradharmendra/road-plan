# ADR-001: Retrieval architecture for enterprise agentic RAG at 10M documents

- **Status:** Proposed
- **Date:** 2026-09-02
- **Deciders:** Platform / Search Engineering
- **Supersedes:** —

## Context

We must serve natural-language search and question answering over **10M source
documents** (PDF/Office/HTML, mixed digital and scanned).

Confirmed requirements:

| Requirement | Value |
|---|---|
| Corpus | 10M raw documents, parsed and chunked |
| Accuracy | "95%", measured as end-to-end answer correctness by human / LLM judge |
| Latency | p95 < 2–3 s |
| Access control | None initially — all users see all documents |
| Freshness | Hourly micro-batch is acceptable |
| Platform | AWS (ECS) for serving, Databricks for model inference |
| Constraint | **Must not be vendor-locked** |

### Scale consequence

10M documents is **not** 10M vectors. At ~15 pages and ~8,000 tokens per document,
with 500-token chunks:

```
10M docs x (8,000 tokens / 500 tokens per chunk) ~= 160-200M chunks
```

Planning number: **200M chunks** (range 100–500M). Every decision below follows from
this number, not from the 10M headline.

Memory footprint for 200M chunks at 1024 dimensions:

| Representation | Bytes/vector | Total |
|---|---|---|
| fp32 | 4,096 | 819 GB |
| int8 | 1,024 | 205 GB |
| Matryoshka 256d + int8 | 256 | 51 GB |
| **binary (Hamming)** | **128** | **25.6 GB** |
| HNSW graph, M=32 | ~256 | 51 GB |

### Accuracy consequence

End-to-end accuracy is multiplicative across pipeline stages:

```
A_e2e = A_parse x A_chunk x A_retrieve x A_rerank x A_generate
```

At a strong 98% per stage, `0.98^5 = 90.4%`. A flat 95% end-to-end correctness target
is **not achievable** on an open-domain enterprise corpus and must not be accepted as a
release gate in that form.

## Decision

### D1. Redefine the accuracy target as precision-with-abstention

We commit to the following instead of "95% accuracy":

| Metric | Target | Gate frequency |
|---|---|---|
| Recall@50 (retrieval) | >= 98% | every PR |
| Answer **precision** (of answers given, % correct) | >= 95% | nightly |
| Coverage (% answered vs. abstained) | 80–90% | nightly |
| Citation groundedness | >= 98% | nightly |

Abstention converts wrong answers into refusals. A system answering 85% of queries at
96% precision is shippable; 100% coverage at 88% precision destroys user trust and will
fail enterprise sign-off. **This redefinition is the single most important decision in
this ADR** and must be agreed with stakeholders before build starts.

### D2. Split into an offline plane and an online plane

- **Offline (Databricks + S3/Delta):** parse, chunk, enrich, embed, build index
  segments, run evals. Hourly micro-batch driven by Delta Change Data Feed.
- **Online (AWS ECS):** query planning, hybrid retrieval, reranking, generation.

Rationale: Databricks is the best available tool for distributed parsing of 10M
documents and GPU batch embedding of ~80B tokens. It is the wrong tool for a 2-second
p95 online path, and it is our primary lock-in risk.

### D3. Delta Lake on our own S3 is the system of record

All chunks, vectors, and metadata are materialised to Delta on S3 in an open format.
Every serving index is a **derived, disposable artefact** rebuildable from Delta.

This is what makes the "no vendor lock-in" requirement real rather than aspirational.

### D4. OpenSearch is the primary online retrieval engine

Selected over pgvector, Databricks Vector Search, Vespa, and Qdrant. See Alternatives.

Configuration: binary quantization (`mode: on_disk`, `compression_level: 32x`) with
full-precision rescoring, HNSW/Faiss, sharded across data nodes with local NVMe.

### D5. Two-stage retrieval with quantization, then a cross-encoder

1. Binary ANN over ~77 GB resident index -> top 1,000 (~40 ms)
2. Rescore against full-precision vectors -> top 100 (~15 ms)
3. Cross-encoder rerank on GPU -> top 15 (~100 ms)

Binary quantization with rescoring recovers 95–99% of fp32 recall at 32x less memory.
This is what makes 200M vectors simultaneously fast and accurate.

### D6. Hybrid lexical + dense retrieval, fused client-side with RRF

BM25 is mandatory, not optional. Enterprise queries contain part numbers, error codes,
policy IDs, and acronyms where dense embeddings routinely fail.

Fusion is performed **client-side** in `ragkit.fusion` rather than via the OpenSearch
`normalization-processor` search pipeline. This costs a few milliseconds and buys
identical ranking semantics across every provider implementation, which is a
precondition for D8 being testable.

### D7. Hierarchical storage — search small, read large

| Tier | Count | Purpose | Store |
|---|---|---|---|
| Doc summary vectors | 10M | Coarse routing, "which document?" | Postgres + pgvector |
| Parent chunks (~2k tok) | ~30M | What the LLM reads | S3 / Delta |
| Child chunks (~400 tok) | ~200M | What we search | OpenSearch |
| Metadata catalog | 10M rows | Filters, facets, lineage, job state | Postgres |

Also decided:

- **Content-addressed dedup** on SHA-256 of normalised text. Enterprise corpora are
  20–40% near-duplicate; dedup shrinks the index and stops the LLM reading five copies
  of a passage and treating repetition as corroboration.
- **Filterable metadata is denormalised into the search index** so filtering happens
  as an ANN pre-filter. Post-filtering after ANN silently destroys recall.
- **`acl_hash` and `security_labels` columns exist from day one**, unused. Retrofitting
  ACLs into a 200M-row index later is a full rebuild.
- **`superseded_by` pointer** on every document. Answering from an obsolete policy
  version is the most common enterprise trust failure and it is a metadata problem,
  not a retrieval problem.

### D8. All retrieval goes through one provider-agnostic interface

```
search(SearchRequest) -> SearchResponse
```

No OpenSearch DSL, SQL, or vendor type may cross this boundary. A pgvector
implementation runs against a corpus sample **in CI on every PR**, so portability is
continuously proven rather than assumed. Same pattern for embeddings and generation.

### D9. Two-tier latency SLA

True agentic loops cost 1.5–3 s per iteration and cannot fit a 2–3 s p95.

- **Fast path** (~80% of queries): single-hop hybrid -> rerank -> generate. p95 2.5 s.
- **Deep path** (multi-hop, comparative, aggregate): bounded agent loop, max 2 extra
  retrieval rounds, hard 12 s wall-clock budget, streamed with visible progress.

A classifier routes between them. We do not promise 2 s p95 on multi-hop questions.

### D10. Tiered document parsing

Cheap text extraction for digital documents; OCR/layout models only for scanned pages.
Blanket commercial OCR over ~150M pages costs six figures. Parsing is both the largest
cost line and the largest accuracy lever — bad parsing is invisible in demos and is the
top cause of enterprise RAG failure.

## Alternatives considered

### Postgres + pgvector — rejected as primary, adopted as catalog

Pros: zero lock-in, team already operates it, transactional consistency with metadata,
joins to business tables, RLS available free when ACLs arrive, `pgvectorscale`
StreamingDiskANN removes the RAM ceiling, `pgvector` 0.8 adds `halfvec` and better
filtered-scan planning, ParadeDB `pg_search` provides real BM25 in-database.

Cons at 200M chunks:

- **No native sharding.** Needs 10–20 shards; we would be hand-building routing,
  fan-out, merge, rebalancing and failover — i.e. writing a distributed vector DB.
- **Index build cost.** HNSW over 200M vectors takes many hours; hourly incremental
  inserts degrade graph quality and force periodic full rebuilds.
- **Filtered recall** still trails true pre-filtering engines at low selectivity.
- **Write amplification.** Hourly multi-million-row upserts create vacuum/bloat
  pressure on the same instance serving a 2 s p95 read path.

Adopted for: document catalog, metadata, job state, feedback, 10M doc-summary vectors
(comfortably in range), and the CI portability implementation.

### Databricks Vector Search — rejected for serving, adopted for the offline plane

Pros: managed Delta Sync indexes, no ops, built-in hybrid, tight Unity Catalog
governance and lineage.

Cons: p95/p99 under concurrency is not tunable by us and would consume 30–40% of the
latency budget inside a black box; per-endpoint pricing at hundreds of millions of
vectors is typically the largest line item in the design; no control over `ef_search`,
quantization strategy, BM25 analyzers, or reranker placement — all of which we need to
reach the precision target; a Delta Sync Index has no drop-in replacement, so it is
precisely the lock-in D3 exists to prevent; plus a cross-VPC hop per query.

Adopted for: parsing, chunking, batch embedding, MLflow evaluation, batch inference.

### Vespa — rejected on operability

Best-in-class for this exact workload: true pre-filtering, phased ranking inside the
engine, native late-interaction/ColBERT, tensor rerank on the node (removes a network
hop), proven at billions of documents. Rejected because the learning curve and hiring
pool make it a staffing risk. **Revisit if retrieval quality becomes existential.**

### Qdrant — viable runner-up

Excellent binary quantization, true pre-filtering, clean sharding, low footprint.
Rejected only because it lacks real BM25 (sparse/SPLADE only), so hybrid would require
a second system anyway — at which point OpenSearch does both.

### Pinecone / Turbopuffer — not evaluated further

Pinecone conflicts with D3. Turbopuffer/LanceDB are attractive on cost via
object-storage-native indexes and should be revisited at Phase 4 if OpenSearch cost
becomes the binding constraint.

## Consequences

**Positive**

- Index is disposable; the system of record is an open format on our own S3.
- Portability is enforced by a CI test, not a promise in a slide.
- Binary quantization keeps 200M vectors inside a modest cluster footprint.
- Hourly refresh is an atomic OpenSearch alias swap — instant rollback.

**Negative**

- We own OpenSearch operations: JVM heap tuning, shard sizing, kNN circuit breakers.
  Mitigation: separate node roles so BM25 and kNN do not contend.
- Client-side RRF forgoes the server-side normalization pipeline. Accepted for D8.
- Two SLA tiers add routing complexity and a second latency budget to defend.
- A GPU reranker fleet is a new production dependency.

**Risks**

| Risk | Mitigation |
|---|---|
| Parsing quality caps accuracy below target | Phase 0 audit of 1,000 sampled docs **before** building the index |
| 95% is held as a contractual number | D1 renegotiation, with the error-budget arithmetic in writing |
| Chunk count lands at 500M not 200M | Sample the page-count distribution in Phase 0; shard budget scales linearly |
| ACLs arrive later and force a rebuild | Schema carries ACL columns from day one (D7) |

## Validation

- `python -m ragkit retrieval-eval --config eval/configs/retrieval.json` gates
  Recall@50 on every PR.
- `tests/test_portability.py` asserts identical ranking across all providers.
- End-to-end answer quality runs nightly on the existing `evalkit` harness.
