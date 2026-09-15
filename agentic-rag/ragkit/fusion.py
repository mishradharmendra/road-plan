"""Rank fusion.

Fusion runs client-side (ADR-001 / D6) so lexical+dense ranking semantics are identical
across every provider. That costs a few milliseconds and is what makes the portability
test in `tests/test_portability.py` meaningful.

RRF is used rather than score normalisation because BM25 and cosine scores live on
incomparable scales, and min-max normalisation is unstable when a result set is small or
scores are tightly clustered.
"""

from __future__ import annotations

from .types import SearchHit


def reciprocal_rank_fusion(
    rankings: list[list[SearchHit]],
    weights: list[float] | None = None,
    k_rrf: int = 60,
    limit: int | None = None,
) -> list[SearchHit]:
    """Fuse ranked lists by ``sum(w / (k_rrf + rank))``.

    `k_rrf=60` is the value from the original Cormack et al. result and damps the
    influence of the top ranks enough that one confident-but-wrong retriever cannot
    dominate the fused list.
    """
    if not rankings:
        return []
    if weights is None:
        weights = [1.0] * len(rankings)
    if len(weights) != len(rankings):
        raise ValueError("weights and rankings must be the same length")

    scores: dict[str, float] = {}
    best: dict[str, SearchHit] = {}
    sources: dict[str, set[str]] = {}

    for ranking, weight in zip(rankings, weights):
        for rank, hit in enumerate(ranking, start=1):
            key = hit.key()
            scores[key] = scores.get(key, 0.0) + weight / (k_rrf + rank)
            sources.setdefault(key, set()).add(hit.retriever or "unknown")
            # Keep whichever copy carries text, so a vector-only hit still renders.
            if key not in best or (not best[key].text and hit.text):
                best[key] = hit

    ordered = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    if limit is not None:
        ordered = ordered[:limit]

    fused: list[SearchHit] = []
    for position, (key, score) in enumerate(ordered, start=1):
        hit = best[key]
        fused.append(
            SearchHit(
                chunk_id=hit.chunk_id,
                doc_id=hit.doc_id,
                score=score,
                rank=position,
                text=hit.text,
                metadata=hit.metadata,
                retriever="+".join(sorted(sources[key])),
            )
        )
    return fused


def dedupe_by_doc(hits: list[SearchHit], per_doc: int = 2) -> list[SearchHit]:
    """Cap chunks per document.

    Near-duplicate passages from one document crowd out competing evidence and make an
    LLM read repetition as corroboration (ADR-001 / D7).
    """
    if per_doc < 1:
        raise ValueError("per_doc must be >= 1")
    counts: dict[str, int] = {}
    out: list[SearchHit] = []
    for hit in hits:
        n = counts.get(hit.doc_id, 0)
        if n >= per_doc:
            continue
        counts[hit.doc_id] = n + 1
        out.append(hit)
    for position, hit in enumerate(out, start=1):
        hit.rank = position
    return out
