"""Phase-0 retrieval evaluation.

Runs the golden query set against any `RetrievalProvider` and gates on Recall@k. This is
the per-PR check; end-to-end answer quality runs nightly on the separate `evalkit`
harness, fed by `export_evalkit_dataset` so the judge sees *real* retrieved context
rather than hand-written context that flatters the generator.
"""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .embeddings import build_embedder
from .metrics import QueryScores, percentile, score_query, wilson_interval
from .provider import RetrievalProvider, build_provider
from .types import Chunk, Filter, SearchMode, SearchRequest


@dataclass
class GoldenQuery:
    id: str
    query: str
    relevant_doc_ids: set[str] = field(default_factory=set)
    relevant_chunk_ids: set[str] = field(default_factory=set)
    grades: dict[str, float] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    filters: list[Filter] = field(default_factory=list)
    reference: str | None = None

    def targets(self, match_on: str) -> set[str]:
        return self.relevant_chunk_ids if match_on == "chunk" else self.relevant_doc_ids


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
    if not rows:
        raise ValueError(f"{path}: no records")
    return rows


def load_corpus(path: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for raw in _read_jsonl(path):
        metadata = dict(raw.get("metadata") or {})
        if raw.get("title"):
            metadata.setdefault("title", raw["title"])
        chunks.append(
            Chunk(
                chunk_id=raw["chunk_id"],
                doc_id=raw["doc_id"],
                text=raw["text"],
                parent_id=raw.get("parent_id"),
                metadata=metadata,
            )
        )
    return chunks


def load_queries(path: Path) -> list[GoldenQuery]:
    out: list[GoldenQuery] = []
    seen: set[str] = set()
    for raw in _read_jsonl(path):
        qid = raw["id"]
        if qid in seen:
            raise ValueError(f"{path}: duplicate query id {qid!r}")
        seen.add(qid)
        out.append(
            GoldenQuery(
                id=qid,
                query=raw["query"],
                relevant_doc_ids=set(raw.get("relevant_doc_ids") or []),
                relevant_chunk_ids=set(raw.get("relevant_chunk_ids") or []),
                grades={k: float(v) for k, v in (raw.get("grades") or {}).items()},
                tags=raw.get("tags") or {},
                filters=[Filter.parse(f) for f in (raw.get("filters") or [])],
                reference=raw.get("reference"),
            )
        )
    return out


@dataclass
class EvalReport:
    name: str
    provider: str
    mode: str
    match_on: str
    n_queries: int
    k_values: list[int]
    metrics: dict[str, float]
    intervals: dict[str, tuple[float, float]]
    slices: dict[str, dict[str, float]]
    per_query: list[QueryScores]
    misses: list[str]

    def to_dict(self) -> dict[str, Any]:
        def clean(v: Any) -> Any:
            # NaN is not valid JSON; an undefined metric serialises as null.
            return None if isinstance(v, float) and v != v else v

        return {
            "name": self.name,
            "provider": self.provider,
            "mode": self.mode,
            "match_on": self.match_on,
            "n_queries": self.n_queries,
            "metrics": {k: clean(v) for k, v in self.metrics.items()},
            "intervals": {k: list(v) for k, v in self.intervals.items()},
            "slices": {
                name: {k: clean(v) for k, v in values.items()}
                for name, values in self.slices.items()
            },
            "misses": self.misses,
        }


def _mean(values: list[float]) -> float:
    clean = [v for v in values if v == v]  # drop NaN
    return statistics.fmean(clean) if clean else float("nan")


def prepare(
    config: dict[str, Any], base_dir: Path, provider: RetrievalProvider | None = None
) -> tuple[Any, RetrievalProvider]:
    """Build the embedder and provider, loading the corpus when `bootstrap` is set.

    Only in-process providers need bootstrapping; pgvector and OpenSearch are loaded
    out of band by `ragkit index`.
    """
    embedder = build_embedder(config.get("embedder") or {"type": "hashing", "dim": 256})
    if provider is None:
        provider = build_provider(config["provider"])
    if config.get("bootstrap"):
        corpus = load_corpus(base_dir / config["corpus"])
        vectors = embedder.embed([c.text for c in corpus], kind="document")
        for chunk, vec in zip(corpus, vectors):
            chunk.embedding = vec
        provider.index(corpus)
    return embedder, provider


def run_eval(
    config: dict[str, Any],
    base_dir: Path,
    provider: RetrievalProvider | None = None,
    limit: int | None = None,
) -> tuple[EvalReport, list[tuple[GoldenQuery, list[Any]]]]:
    k_values = [int(k) for k in config.get("k_values", [5, 10, 50])]
    mode = SearchMode(config.get("mode", "hybrid"))
    match_on = config.get("match_on", "doc")
    if match_on not in ("doc", "chunk"):
        raise ValueError("match_on must be 'doc' or 'chunk'")

    owns_provider = provider is None
    embedder, provider = prepare(config, base_dir, provider)

    queries = load_queries(base_dir / config["queries"])
    if limit:
        queries = queries[:limit]

    top_k = max(k_values)
    scored: list[QueryScores] = []
    retrieved_ctx: list[tuple[GoldenQuery, list[Any]]] = []
    misses: list[str] = []

    for q in queries:
        vector = (
            embedder.embed_one(q.query, kind="query") if mode is not SearchMode.LEXICAL else None
        )
        request = SearchRequest(
            query=q.query, k=top_k, mode=mode, filters=q.filters, query_vector=vector
        )
        started = time.perf_counter()
        response = provider.search(request)
        latency = (time.perf_counter() - started) * 1000.0

        ids = [h.chunk_id if match_on == "chunk" else h.doc_id for h in response.hits]
        # De-dup while preserving rank so recall@k counts distinct documents.
        ordered = list(dict.fromkeys(ids))
        targets = q.targets(match_on)
        scored.append(score_query(q.id, ordered, targets, q.grades, k_values, latency))
        retrieved_ctx.append((q, response.hits))
        if targets and not (set(ordered[:top_k]) & targets):
            misses.append(q.id)

    if owns_provider:
        provider.close()

    metrics: dict[str, float] = {}
    intervals: dict[str, tuple[float, float]] = {}
    for k in k_values:
        metrics[f"recall@{k}"] = _mean([s.recall[k] for s in scored])
        metrics[f"precision@{k}"] = _mean([s.precision[k] for s in scored])
        metrics[f"ndcg@{k}"] = _mean([s.ndcg[k] for s in scored])
        hits = sum(1 for s in scored if s.first_relevant_rank and s.first_relevant_rank <= k)
        metrics[f"hit_rate@{k}"] = hits / len(scored) if scored else 0.0
        intervals[f"hit_rate@{k}"] = wilson_interval(hits, len(scored))
    metrics["mrr"] = _mean([s.mrr for s in scored])
    latencies = [s.latency_ms for s in scored]
    metrics["latency_p50_ms"] = percentile(latencies, 50)
    metrics["latency_p95_ms"] = percentile(latencies, 95)

    slices: dict[str, dict[str, float]] = {}
    primary = max(k_values)
    recall_key = f"recall@{primary}"
    for q, s in zip(queries, scored):
        value = s.recall[primary]
        for tag, tag_value in q.tags.items():
            bucket = slices.setdefault(
                f"{tag}={tag_value}", {"n": 0.0, "scored": 0.0, recall_key: 0.0}
            )
            bucket["n"] += 1
            # Unanswerable queries have no relevant documents, so recall is undefined
            # rather than zero. Averaging them in would understate every slice they touch.
            if value == value:
                bucket["scored"] += 1
                bucket[recall_key] += value
    for bucket in slices.values():
        bucket[recall_key] = (
            bucket[recall_key] / bucket["scored"] if bucket["scored"] else float("nan")
        )

    report = EvalReport(
        name=config.get("name", "retrieval"),
        provider=config.get("provider", {}).get("type", "unknown"),
        mode=mode.value,
        match_on=match_on,
        n_queries=len(scored),
        k_values=k_values,
        metrics=metrics,
        intervals=intervals,
        slices=slices,
        per_query=scored,
        misses=misses,
    )
    return report, retrieved_ctx


def check_gates(report: EvalReport, gates: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for name, bound in (gates.get("min") or {}).items():
        actual = report.metrics.get(name)
        if actual is None:
            failures.append(f"gate {name}: metric not produced")
        elif actual < bound:
            failures.append(f"gate {name}: {actual:.4f} < min {bound}")
    for name, bound in (gates.get("max") or {}).items():
        actual = report.metrics.get(name)
        if actual is None:
            failures.append(f"gate {name}: metric not produced")
        elif actual > bound:
            failures.append(f"gate {name}: {actual:.4f} > max {bound}")
    return failures


def export_evalkit_dataset(
    retrieved: list[tuple[GoldenQuery, list[Any]]], path: Path, top_n: int = 8
) -> int:
    """Write an evalkit-format JSONL whose `context` is real retrieval output.

    This is the bridge between the two harnesses. Evaluating generation against
    hand-curated context measures a system nobody ships.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for q, hits in retrieved:
            record = {
                "id": q.id,
                "input": q.query,
                "reference": q.reference,
                "context": [h.text for h in hits[:top_n] if h.text],
                "tags": {**q.tags, "answerable": "yes" if q.relevant_doc_ids else "no"},
                "metadata": {
                    "expect_citations": bool(q.relevant_doc_ids),
                    "retrieved_doc_ids": list(dict.fromkeys(h.doc_id for h in hits[:top_n])),
                },
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(retrieved)
