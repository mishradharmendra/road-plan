"""In-memory reference provider.

This is not a toy. It is the executable definition of correct behaviour: BM25 + cosine +
RRF with no network, no daemon, and no dependencies. `tests/test_portability.py` asserts
that OpenSearch and pgvector agree with it, which is how ADR-001 / D8 stays honest
instead of aspirational.

Suitable for CI and for corpora up to ~100k chunks. Not for production serving.
"""

from __future__ import annotations

import math
import time
from typing import Any, Iterable

from ..fusion import reciprocal_rank_fusion
from ..provider import RetrievalProvider, register
from ..text import tokenize
from ..types import Chunk, FilterOp, SearchHit, SearchMode, SearchRequest, SearchResponse


def _lookup(metadata: dict[str, Any], path: str) -> Any:
    cur: Any = metadata
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _matches(metadata: dict[str, Any], filters: list[Any]) -> bool:
    for f in filters:
        actual = _lookup(metadata, f.field)
        if f.op is FilterOp.EXISTS:
            if (actual is not None) != bool(f.value):
                return False
        elif f.op is FilterOp.EQ:
            if actual != f.value:
                return False
        elif f.op is FilterOp.IN:
            if actual not in f.value:
                return False
        elif f.op is FilterOp.PREFIX:
            if not isinstance(actual, str) or not actual.startswith(f.value):
                return False
        elif f.op is FilterOp.RANGE:
            if actual is None:
                return False
            bounds = f.value
            if "gte" in bounds and actual < bounds["gte"]:
                return False
            if "gt" in bounds and actual <= bounds["gt"]:
                return False
            if "lte" in bounds and actual > bounds["lte"]:
                return False
            if "lt" in bounds and actual >= bounds["lt"]:
                return False
    return True


@register
class InMemoryProvider(RetrievalProvider):
    type_name = "memory"

    def __init__(
        self,
        filter_fields: Iterable[str] = (),
        bm25_k1: float = 1.2,
        bm25_b: float = 0.75,
        rrf_k: int = 60,
        weights: tuple[float, float] = (1.0, 1.0),
        **_: Any,
    ):
        self.filter_fields = frozenset(filter_fields)
        self.k1 = bm25_k1
        self.b = bm25_b
        self.rrf_k = rrf_k
        self.weights = list(weights)
        self._chunks: dict[str, Chunk] = {}
        self._tokens: dict[str, list[str]] = {}
        self._tf: dict[str, dict[str, int]] = {}
        self._df: dict[str, int] = {}
        self._avgdl = 0.0

    # ---------------------------------------------------------------- write path

    def index(self, chunks: Iterable[Chunk]) -> int:
        n = 0
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = chunk
            toks = tokenize(chunk.text)
            self._tokens[chunk.chunk_id] = toks
            tf: dict[str, int] = {}
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
            self._tf[chunk.chunk_id] = tf
            n += 1
        self._rebuild_stats()
        return n

    def delete_by_doc(self, doc_ids: Iterable[str]) -> int:
        targets = set(doc_ids)
        victims = [cid for cid, c in self._chunks.items() if c.doc_id in targets]
        for cid in victims:
            self._chunks.pop(cid, None)
            self._tokens.pop(cid, None)
            self._tf.pop(cid, None)
        self._rebuild_stats()
        return len(victims)

    def _rebuild_stats(self) -> None:
        self._df = {}
        for tf in self._tf.values():
            for term in tf:
                self._df[term] = self._df.get(term, 0) + 1
        lengths = [len(t) for t in self._tokens.values()]
        self._avgdl = (sum(lengths) / len(lengths)) if lengths else 0.0

    # ----------------------------------------------------------------- read path

    def health(self) -> bool:
        return True

    def _candidates(self, filters: list[Any]) -> list[str]:
        if not filters:
            return list(self._chunks)
        return [
            cid for cid, c in self._chunks.items() if _matches(c.metadata, filters)
        ]

    def _bm25(self, query: str, cids: list[str], depth: int) -> list[SearchHit]:
        terms = tokenize(query)
        if not terms or not cids:
            return []
        n_docs = len(self._chunks)
        scored: list[tuple[float, str]] = []
        for cid in cids:
            tf = self._tf[cid]
            dl = len(self._tokens[cid]) or 1
            score = 0.0
            for term in terms:
                f = tf.get(term, 0)
                if not f:
                    continue
                df = self._df.get(term, 0)
                idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
                denom = f + self.k1 * (1.0 - self.b + self.b * dl / (self._avgdl or 1.0))
                score += idf * (f * (self.k1 + 1.0)) / denom
            if score > 0.0:
                scored.append((score, cid))
        scored.sort(key=lambda s: (-s[0], s[1]))
        return [self._hit(cid, sc, i, "lexical") for i, (sc, cid) in enumerate(scored[:depth], 1)]

    def _dense(self, vector: list[float], cids: list[str], depth: int) -> list[SearchHit]:
        qn = math.sqrt(sum(v * v for v in vector)) or 1.0
        scored: list[tuple[float, str]] = []
        for cid in cids:
            emb = self._chunks[cid].embedding
            if not emb:
                continue
            dot = sum(a * b for a, b in zip(vector, emb))
            dn = math.sqrt(sum(v * v for v in emb)) or 1.0
            scored.append((dot / (qn * dn), cid))
        scored.sort(key=lambda s: (-s[0], s[1]))
        return [self._hit(cid, sc, i, "dense") for i, (sc, cid) in enumerate(scored[:depth], 1)]

    def _hit(self, cid: str, score: float, rank: int, retriever: str) -> SearchHit:
        chunk = self._chunks[cid]
        return SearchHit(
            chunk_id=cid,
            doc_id=chunk.doc_id,
            score=float(score),
            rank=rank,
            text=chunk.text,
            metadata=chunk.metadata,
            retriever=retriever,
        )

    def search(self, request: SearchRequest) -> SearchResponse:
        self._validate(request.filters)
        started = time.perf_counter()
        cids = self._candidates(request.filters)
        depth = request.candidate_depth

        lexical: list[SearchHit] = []
        dense: list[SearchHit] = []
        if request.mode in (SearchMode.LEXICAL, SearchMode.HYBRID):
            lexical = self._bm25(request.query, cids, depth)
        if request.mode in (SearchMode.DENSE, SearchMode.HYBRID):
            dense = self._dense(request.query_vector or [], cids, depth)

        if request.mode is SearchMode.HYBRID:
            hits = reciprocal_rank_fusion(
                [lexical, dense], weights=self.weights, k_rrf=self.rrf_k, limit=request.k
            )
        else:
            hits = (lexical or dense)[: request.k]

        if not request.include_text:
            for h in hits:
                h.text = ""

        return SearchResponse(
            hits=hits,
            took_ms=(time.perf_counter() - started) * 1000.0,
            provider=self.type_name,
            mode=request.mode,
            debug={
                "filtered_candidates": len(cids),
                "lexical": len(lexical),
                "dense": len(dense),
            },
        )
