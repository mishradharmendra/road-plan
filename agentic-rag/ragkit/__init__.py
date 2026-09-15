"""ragkit — provider-agnostic retrieval for the enterprise agentic RAG platform.

See docs/ADR-001-retrieval-architecture.md. The one rule: application code depends on
`RetrievalProvider`, never on a vendor SDK.
"""

from __future__ import annotations

from .embeddings import EmbeddingProvider, build_embedder
from .fusion import dedupe_by_doc, reciprocal_rank_fusion
from .provider import RetrievalProvider, build_provider
from .types import (
    Chunk,
    Filter,
    FilterOp,
    SearchHit,
    SearchMode,
    SearchRequest,
    SearchResponse,
)

__all__ = [
    "Chunk",
    "EmbeddingProvider",
    "Filter",
    "FilterOp",
    "RetrievalProvider",
    "SearchHit",
    "SearchMode",
    "SearchRequest",
    "SearchResponse",
    "build_embedder",
    "build_provider",
    "dedupe_by_doc",
    "reciprocal_rank_fusion",
]
