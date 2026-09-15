"""The retrieval contract (ADR-001 / D8).

Every call site in the system depends on `RetrievalProvider` and nothing else. Swapping
OpenSearch for pgvector, Qdrant, or Vespa must be a config change plus one new module in
`ragkit/providers/`, never an edit to application code.
"""

from __future__ import annotations

import abc
from typing import Any, Iterable

from .types import Chunk, Filter, SearchRequest, SearchResponse


class RetrievalProvider(abc.ABC):
    """Read path is mandatory; write path is optional so read-only replicas and
    managed indexes can implement the interface without pretending to be writable."""

    type_name: str = "provider"

    #: Fields callers are permitted to filter on. Empty frozenset disables filtering.
    filter_fields: frozenset[str] = frozenset()

    @abc.abstractmethod
    def search(self, request: SearchRequest) -> SearchResponse: ...

    @abc.abstractmethod
    def health(self) -> bool: ...

    def index(self, chunks: Iterable[Chunk]) -> int:
        raise NotImplementedError(f"{self.type_name} is read-only")

    def delete_by_doc(self, doc_ids: Iterable[str]) -> int:
        raise NotImplementedError(f"{self.type_name} is read-only")

    def close(self) -> None:
        return None

    def _validate(self, filters: list[Filter]) -> None:
        for f in filters:
            f.validate(self.filter_fields)

    def __enter__(self) -> RetrievalProvider:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


REGISTRY: dict[str, type[RetrievalProvider]] = {}


def register(cls: type[RetrievalProvider]) -> type[RetrievalProvider]:
    REGISTRY[cls.type_name] = cls
    return cls


def build_provider(spec: dict[str, Any]) -> RetrievalProvider:
    spec = dict(spec)
    kind = spec.pop("type", None)
    if kind is None:
        raise ValueError("provider spec needs a 'type'")
    if kind not in REGISTRY:
        raise ValueError(f"unknown provider {kind!r}; have {sorted(REGISTRY)}")
    return REGISTRY[kind](**spec)


from .providers import memory, opensearch, pgvector  # noqa: E402,F401  (populates REGISTRY)

__all__ = ["RetrievalProvider", "REGISTRY", "register", "build_provider"]
