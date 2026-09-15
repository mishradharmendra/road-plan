"""Provider-agnostic retrieval types.

Nothing vendor-specific may appear in this module or cross the provider boundary
(ADR-001 / D8). If you find yourself wanting to add an OpenSearch DSL fragment or a
SQL snippet here, that is the signal the abstraction is leaking.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# Filter/sort field names are interpolated into query bodies and SQL identifiers, so
# they are validated against this pattern *and* an explicit per-provider allowlist.
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")

_RANGE_KEYS = frozenset({"gt", "gte", "lt", "lte"})


class SearchMode(str, Enum):
    LEXICAL = "lexical"
    DENSE = "dense"
    HYBRID = "hybrid"


class FilterOp(str, Enum):
    EQ = "eq"
    IN = "in"
    RANGE = "range"
    EXISTS = "exists"
    PREFIX = "prefix"


class FilterError(ValueError):
    """A filter referenced an unknown field or carried a malformed value."""


@dataclass(frozen=True)
class Filter:
    """One structured predicate. Providers translate; callers never author DSL."""

    field: str
    op: FilterOp
    value: Any = None

    def validate(self, allowed: frozenset[str]) -> None:
        if not _IDENT.match(self.field):
            raise FilterError(f"illegal filter field name: {self.field!r}")
        if allowed and self.field not in allowed:
            raise FilterError(
                f"field {self.field!r} is not filterable; allowed: {sorted(allowed)}"
            )
        if self.op is FilterOp.IN:
            if not isinstance(self.value, (list, tuple)) or not self.value:
                raise FilterError(f"{self.field}: 'in' needs a non-empty list")
        elif self.op is FilterOp.RANGE:
            if not isinstance(self.value, dict) or not self.value:
                raise FilterError(f"{self.field}: 'range' needs a dict of gt/gte/lt/lte")
            unknown = set(self.value) - _RANGE_KEYS
            if unknown:
                raise FilterError(f"{self.field}: unknown range keys {sorted(unknown)}")
        elif self.op is FilterOp.PREFIX:
            if not isinstance(self.value, str) or not self.value:
                raise FilterError(f"{self.field}: 'prefix' needs a non-empty string")

    @classmethod
    def parse(cls, raw: dict[str, Any]) -> Filter:
        try:
            return cls(field=raw["field"], op=FilterOp(raw["op"]), value=raw.get("value"))
        except KeyError as exc:
            raise FilterError(f"filter missing key {exc}") from exc


@dataclass
class SearchRequest:
    """A retrieval call. `query_vector` is supplied by the caller's embedder so the
    provider never owns model choice."""

    query: str
    k: int = 50
    mode: SearchMode = SearchMode.HYBRID
    filters: list[Filter] = field(default_factory=list)
    query_vector: list[float] | None = None
    # Candidates pulled from each retriever before fusion/rescoring. Higher = better
    # recall, more latency. 4x k is a sane default for binary-quantized indexes.
    oversample: int = 4
    # Full-precision rescore depth multiplier applied inside the ANN engine.
    rescore_factor: float = 2.0
    include_text: bool = True

    def __post_init__(self) -> None:
        if self.k < 1:
            raise ValueError("k must be >= 1")
        if self.oversample < 1:
            raise ValueError("oversample must be >= 1")
        if self.mode is not SearchMode.LEXICAL and self.query_vector is None:
            raise ValueError(f"mode={self.mode.value} requires query_vector")
        if not self.query and self.mode is not SearchMode.DENSE:
            raise ValueError(f"mode={self.mode.value} requires a non-empty query")

    @property
    def candidate_depth(self) -> int:
        return self.k * self.oversample


@dataclass
class SearchHit:
    chunk_id: str
    doc_id: str
    score: float
    rank: int = 0
    text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    # Which retriever produced this hit: lexical, dense, or hybrid after fusion.
    retriever: str = ""

    def key(self) -> str:
        return self.chunk_id


@dataclass
class SearchResponse:
    hits: list[SearchHit]
    took_ms: float
    provider: str
    mode: SearchMode
    # Per-retriever candidate counts and timings; used by the eval CLI, never by callers.
    debug: dict[str, Any] = field(default_factory=dict)

    def doc_ids(self) -> list[str]:
        seen: dict[str, None] = {}
        for h in self.hits:
            seen.setdefault(h.doc_id, None)
        return list(seen)


@dataclass
class Chunk:
    """Indexing unit. `parent_id` implements search-small/read-large (ADR-001 / D7)."""

    chunk_id: str
    doc_id: str
    text: str
    embedding: list[float] | None = None
    parent_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
