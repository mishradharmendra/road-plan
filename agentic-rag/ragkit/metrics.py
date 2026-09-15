"""Retrieval metrics.

Retrieval quality is measured separately from answer quality on purpose (ADR-001 / D1):
it is deterministic, needs no LLM, runs in seconds, and localises the fault. When
end-to-end correctness drops, the first question is always "did we retrieve it at all?"
and only this file can answer that.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class QueryScores:
    query_id: str
    recall: dict[int, float]
    precision: dict[int, float]
    ndcg: dict[int, float]
    mrr: float
    first_relevant_rank: int | None
    n_relevant: int
    latency_ms: float


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return float("nan")
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        return 0.0
    return len(set(retrieved[:k]) & relevant) / k


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> tuple[float, int | None]:
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank, rank
    return 0.0, None


def ndcg_at_k(retrieved: list[str], gains: dict[str, float], k: int) -> float:
    """Graded nDCG with the standard 2^g - 1 gain function.

    Falls back to binary relevance when the dataset has no grades, which is the common
    case for a hand-labelled seed set.
    """
    if not gains:
        return float("nan")
    dcg = 0.0
    for i, item in enumerate(retrieved[:k], start=1):
        g = gains.get(item, 0.0)
        if g:
            dcg += (2**g - 1) / math.log2(i + 1)
    ideal = sorted(gains.values(), reverse=True)[:k]
    idcg = sum((2**g - 1) / math.log2(i + 1) for i, g in enumerate(ideal, start=1))
    return dcg / idcg if idcg > 0 else 0.0


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval.

    Reported alongside every rate because a 40-query seed set produces intervals wide
    enough that "recall went from 0.92 to 0.95" is usually noise, and shipping on that
    delta is how eval suites lose credibility.
    """
    if total == 0:
        return (0.0, 0.0)
    p = successes / total
    denom = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denom
    margin = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, math.ceil(pct / 100 * len(ordered)) - 1))
    return ordered[idx]


def score_query(
    query_id: str,
    retrieved: list[str],
    relevant: set[str],
    gains: dict[str, float],
    k_values: list[int],
    latency_ms: float,
) -> QueryScores:
    rr, first = reciprocal_rank(retrieved, relevant)
    return QueryScores(
        query_id=query_id,
        recall={k: recall_at_k(retrieved, relevant, k) for k in k_values},
        precision={k: precision_at_k(retrieved, relevant, k) for k in k_values},
        ndcg={k: ndcg_at_k(retrieved, gains, k) for k in k_values},
        mrr=rr,
        first_relevant_rank=first,
        n_relevant=len(relevant),
        latency_ms=latency_ms,
    )
