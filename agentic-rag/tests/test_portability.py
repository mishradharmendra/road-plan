"""Provider contract + portability suite (ADR-001 / D8).

The same assertions run against every provider. `memory` always runs; `pgvector` and
`opensearch` run when their env vars are present and skip otherwise, so CI proves
portability on every PR without requiring a cluster for a docstring change.

    python -m unittest discover -s tests -t .
    PG_DSN=postgresql://... python -m unittest discover -s tests -t .
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ragkit.embeddings import HashingEmbedder  # noqa: E402
from ragkit.evaluate import load_corpus  # noqa: E402
from ragkit.fusion import dedupe_by_doc, reciprocal_rank_fusion  # noqa: E402
from ragkit.provider import build_provider  # noqa: E402
from ragkit.types import (  # noqa: E402
    Filter,
    FilterError,
    FilterOp,
    SearchHit,
    SearchMode,
    SearchRequest,
)

CORPUS = Path(__file__).resolve().parents[1] / "eval" / "corpus" / "sample_corpus.jsonl"
FILTER_FIELDS = ["doc_type", "source_system", "language", "created_at", "version_status"]
DIM = 256


class FusionTests(unittest.TestCase):
    def test_rrf_prefers_agreement(self) -> None:
        lex = [SearchHit("c1", "d1", 9.0, 1, retriever="lexical"),
               SearchHit("c2", "d2", 8.0, 2, retriever="lexical")]
        dense = [SearchHit("c2", "d2", 0.9, 1, retriever="dense"),
                 SearchHit("c3", "d3", 0.8, 2, retriever="dense")]
        fused = reciprocal_rank_fusion([lex, dense])
        # c2 is ranked by both retrievers and must outrank either single-list leader.
        self.assertEqual(fused[0].chunk_id, "c2")
        self.assertEqual(fused[0].retriever, "dense+lexical")
        self.assertEqual([h.rank for h in fused], [1, 2, 3])

    def test_rrf_rejects_mismatched_weights(self) -> None:
        with self.assertRaises(ValueError):
            reciprocal_rank_fusion([[], []], weights=[1.0])

    def test_dedupe_caps_per_document(self) -> None:
        hits = [SearchHit(f"c{i}", "d1", 1.0 / i, i) for i in range(1, 5)]
        hits.append(SearchHit("c9", "d2", 0.1, 5))
        capped = dedupe_by_doc(hits, per_doc=2)
        self.assertEqual([h.chunk_id for h in capped], ["c1", "c2", "c9"])
        self.assertEqual([h.rank for h in capped], [1, 2, 3])


class FilterValidationTests(unittest.TestCase):
    def test_unlisted_field_is_rejected(self) -> None:
        with self.assertRaises(FilterError):
            Filter("secret_column", FilterOp.EQ, "x").validate(frozenset(FILTER_FIELDS))

    def test_injection_shaped_field_is_rejected(self) -> None:
        with self.assertRaises(FilterError):
            Filter("doc_type; DROP TABLE chunks--", FilterOp.EQ, "x").validate(frozenset())

    def test_malformed_range_is_rejected(self) -> None:
        with self.assertRaises(FilterError):
            Filter("created_at", FilterOp.RANGE, {"between": 1}).validate(frozenset(FILTER_FIELDS))

    def test_dense_mode_requires_a_vector(self) -> None:
        with self.assertRaises(ValueError):
            SearchRequest(query="x", mode=SearchMode.DENSE)


class ProviderContract:
    """Assertions every provider must satisfy identically."""

    provider_spec: dict = {}
    bootstrap = False

    @classmethod
    def build(cls):
        return build_provider(cls.provider_spec)

    def setUp(self) -> None:
        self.embedder = HashingEmbedder(dim=DIM)
        self.chunks = load_corpus(CORPUS)
        for chunk, vec in zip(self.chunks, self.embedder.embed([c.text for c in self.chunks])):
            chunk.embedding = vec
        self.provider = self.build()
        if self.bootstrap:
            self.provider.index(self.chunks)

    def tearDown(self) -> None:
        self.provider.close()

    def _search(self, query: str, **kwargs):
        mode = kwargs.pop("mode", SearchMode.HYBRID)
        vector = None if mode is SearchMode.LEXICAL else self.embedder.embed_one(query)
        return self.provider.search(
            SearchRequest(query=query, mode=mode, query_vector=vector, **kwargs)
        )

    def test_health(self) -> None:
        self.assertTrue(self.provider.health())

    def test_exact_id_query_is_found(self) -> None:
        # The canonical case dense-only retrieval fails and BM25 saves: a bare error code.
        response = self._search("AUTH-5031", k=10)
        self.assertIn("RUN-AUTH-503", response.doc_ids())

    def test_hybrid_beats_or_matches_single_retriever_on_ids(self) -> None:
        hybrid = self._search("AUTH-5031", k=5).doc_ids()
        lexical = self._search("AUTH-5031", k=5, mode=SearchMode.LEXICAL).doc_ids()
        self.assertIn("RUN-AUTH-503", hybrid)
        self.assertIn("RUN-AUTH-503", lexical)

    def test_filter_is_applied_as_a_prefilter(self) -> None:
        response = self._search(
            "daily meal allowance international travel",
            k=20,
            filters=[Filter("version_status", FilterOp.EQ, "current")],
        )
        self.assertIn("POL-EXPENSE-2026", response.doc_ids())
        self.assertNotIn("POL-EXPENSE-2024", response.doc_ids())

    def test_unlisted_filter_field_raises(self) -> None:
        with self.assertRaises(FilterError):
            self._search("anything", filters=[Filter("acl_hash", FilterOp.EQ, "x")])

    def test_k_is_respected(self) -> None:
        self.assertLessEqual(len(self._search("policy", k=3).hits), 3)

    def test_ranks_are_dense_and_ordered(self) -> None:
        hits = self._search("expense policy receipts", k=10).hits
        self.assertEqual([h.rank for h in hits], list(range(1, len(hits) + 1)))

    def test_include_text_false_omits_payload(self) -> None:
        hits = self._search("encryption standard", k=5, include_text=False).hits
        self.assertTrue(all(h.text == "" for h in hits))


class MemoryProviderTests(ProviderContract, unittest.TestCase):
    provider_spec = {"type": "memory", "filter_fields": FILTER_FIELDS}
    bootstrap = True


@unittest.skipUnless(os.environ.get("PG_DSN"), "PG_DSN not set")
class PgVectorProviderTests(ProviderContract, unittest.TestCase):
    provider_spec = {
        "type": "pgvector",
        "table": "chunks_test",
        "dim": DIM,
        "filter_fields": FILTER_FIELDS,
    }
    bootstrap = True

    def setUp(self) -> None:
        self.embedder = HashingEmbedder(dim=DIM)
        self.chunks = load_corpus(CORPUS)
        for chunk, vec in zip(self.chunks, self.embedder.embed([c.text for c in self.chunks])):
            chunk.embedding = vec
        self.provider = self.build()
        self.provider.create_schema()
        self.provider.delete_by_doc({c.doc_id for c in self.chunks})
        self.provider.index(self.chunks)


@unittest.skipUnless(os.environ.get("OPENSEARCH_ENDPOINT"), "OPENSEARCH_ENDPOINT not set")
class OpenSearchProviderTests(ProviderContract, unittest.TestCase):
    bootstrap = True

    @classmethod
    def build(cls):
        return build_provider(
            {
                "type": "opensearch",
                "endpoint": os.environ["OPENSEARCH_ENDPOINT"],
                "index": os.environ.get("OPENSEARCH_INDEX", "chunks-test"),
                "dim": DIM,
                "filter_fields": FILTER_FIELDS,
                "source_fields": FILTER_FIELDS + ["title", "parent_id"],
                "auth": {"type": os.environ.get("OPENSEARCH_AUTH", "none"), "region": os.environ.get("AWS_REGION", "us-west-2")},
            }
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
