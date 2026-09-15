"""Postgres + pgvector provider.

Two roles in this architecture (ADR-001):

1. **Portability insurance.** This runs against a corpus sample in CI on every PR, so
   the claim "we are not locked into OpenSearch" is continuously executed rather than
   asserted in a slide.
2. **Doc-summary tier.** 10M document-level vectors sit comfortably in pgvector and give
   coarse "which document?" routing next to the metadata catalog, with a plain SQL join.

It is deliberately *not* the 200M-chunk serving path — see the ADR's Alternatives section
for why (no native sharding, HNSW rebuild cost, vacuum pressure on the read path).

Requires pgvector >= 0.7 for `halfvec` and `binary_quantize`; 0.8 recommended.
Optional runtime dependency: `psycopg[binary]` >= 3.1.
"""

from __future__ import annotations

import os
import time
from typing import Any, Iterable

from ..fusion import reciprocal_rank_fusion
from ..provider import RetrievalProvider, register
from ..types import (
    Chunk,
    Filter,
    FilterError,
    FilterOp,
    SearchHit,
    SearchMode,
    SearchRequest,
    SearchResponse,
    _IDENT,
)

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS {table} (
    chunk_id        text PRIMARY KEY,
    doc_id          text NOT NULL,
    parent_id       text,
    title           text,
    text            text NOT NULL,
    embedding       halfvec({dim}) NOT NULL,
    -- Stage 1 of the two-stage search: 32x smaller, Hamming-ordered.
    embedding_bit   bit({dim}) GENERATED ALWAYS AS
                        (binary_quantize(embedding::vector)::bit({dim})) STORED,
    tsv             tsvector GENERATED ALWAYS AS
                        (to_tsvector('english', coalesce(title,'') || ' ' || text)) STORED,
    -- Promoted filter columns. Filtering must be a pre-filter, never applied to ANN output.
    doc_type        text,
    source_system   text,
    language        text,
    created_at      timestamptz,
    version_status  text,
    superseded_by   text,
    -- Unused until ACLs arrive; present from day one so that is not a full rebuild.
    acl_hash        text,
    security_labels text[],
    metadata        jsonb NOT NULL DEFAULT '{{}}'::jsonb
);

CREATE INDEX IF NOT EXISTS {table_base}_bit_hnsw
    ON {table} USING hnsw (embedding_bit bit_hamming_ops);
CREATE INDEX IF NOT EXISTS {table_base}_tsv_gin ON {table} USING gin (tsv);
CREATE INDEX IF NOT EXISTS {table_base}_doc_id  ON {table} (doc_id);
CREATE INDEX IF NOT EXISTS {table_base}_doctype ON {table} (doc_type);
"""


def _vec_literal(vec: Iterable[float]) -> str:
    return "[" + ",".join(f"{v:.6g}" for v in vec) + "]"


@register
class PgVectorProvider(RetrievalProvider):
    type_name = "pgvector"

    def __init__(
        self,
        table: str = "chunks",
        dim: int = 1024,
        dsn_env: str = "PG_DSN",
        dsn: str | None = None,
        filter_fields: Iterable[str] = (),
        rrf_k: int = 60,
        weights: tuple[float, float] = (1.0, 1.0),
        text_search_config: str = "english",
        ef_search: int | None = None,
        statement_timeout_ms: int = 5000,
        **_: Any,
    ):
        if not _IDENT.match(table):
            raise ValueError(f"illegal table name {table!r}")
        if text_search_config not in ("english", "simple"):
            raise ValueError("text_search_config must be 'english' or 'simple'")
        self.table = table
        self.dim = dim
        self.dsn_env = dsn_env
        self._dsn = dsn
        self.filter_fields = frozenset(filter_fields)
        self.rrf_k = rrf_k
        self.weights = list(weights)
        self.ts_config = text_search_config
        self.ef_search = ef_search
        self.statement_timeout_ms = statement_timeout_ms
        self._conn: Any = None

    # ------------------------------------------------------------------ transport

    @property
    def dsn(self) -> str:
        dsn = self._dsn or os.environ.get(self.dsn_env)
        if not dsn:
            raise RuntimeError(f"no DSN: set ${self.dsn_env} or pass dsn=")
        return dsn

    def _connect(self) -> Any:
        if self._conn is not None and not self._conn.closed:
            return self._conn
        try:
            import psycopg
        except ImportError as exc:  # pragma: no cover - env dependent
            raise RuntimeError(
                "pgvector provider needs psycopg: pip install 'psycopg[binary]'"
            ) from exc
        self._conn = psycopg.connect(self.dsn, autocommit=True)
        with self._conn.cursor() as cur:
            cur.execute(f"SET statement_timeout = {int(self.statement_timeout_ms)}")
            if self.ef_search is not None:
                cur.execute(f"SET hnsw.ef_search = {int(self.ef_search)}")
        return self._conn

    def close(self) -> None:
        if self._conn is not None and not self._conn.closed:
            self._conn.close()
        self._conn = None

    def _ident(self, name: str) -> Any:
        from psycopg import sql

        return sql.Identifier(*name.split("."))

    # ------------------------------------------------------------------ filtering

    def _where(self, filters: list[Filter]) -> tuple[Any, list[Any]]:
        """Build a parameterised WHERE fragment.

        Field names are allowlisted by `_validate` *and* emitted through
        `sql.Identifier`; every value is a bound parameter. No user text is ever
        concatenated into SQL.
        """
        from psycopg import sql

        clauses: list[Any] = []
        params: list[Any] = []
        for f in filters:
            col = self._ident(f.field)
            if f.op is FilterOp.EQ:
                clauses.append(sql.SQL("{} = %s").format(col))
                params.append(f.value)
            elif f.op is FilterOp.IN:
                clauses.append(sql.SQL("{} = ANY(%s)").format(col))
                params.append(list(f.value))
            elif f.op is FilterOp.PREFIX:
                clauses.append(sql.SQL("{} LIKE %s").format(col))
                params.append(f.value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%")
            elif f.op is FilterOp.EXISTS:
                clauses.append(sql.SQL("{} IS {} NULL").format(col, sql.SQL("NOT" if f.value else "")))
            elif f.op is FilterOp.RANGE:
                for key, op in (("gte", ">="), ("gt", ">"), ("lte", "<="), ("lt", "<")):
                    if key in f.value:
                        clauses.append(sql.SQL("{} " + op + " %s").format(col))
                        params.append(f.value[key])
            else:
                raise FilterError(f"unsupported op {f.op}")
        if not clauses:
            return sql.SQL("TRUE"), params
        return sql.SQL(" AND ").join(clauses), params

    # ------------------------------------------------------------------ read path

    def health(self) -> bool:
        try:
            with self._connect().cursor() as cur:
                cur.execute("SELECT 1")
                return cur.fetchone() is not None
        except Exception:
            return False

    def _rows_to_hits(self, rows: list[tuple], retriever: str) -> list[SearchHit]:
        return [
            SearchHit(
                chunk_id=r[0],
                doc_id=r[1],
                score=float(r[3]),
                rank=i,
                text=r[2] or "",
                metadata=r[4] or {},
                retriever=retriever,
            )
            for i, r in enumerate(rows, start=1)
        ]

    def _lexical(self, request: SearchRequest, depth: int) -> list[SearchHit]:
        from psycopg import sql

        where, params = self._where(request.filters)
        # websearch_to_tsquery parses user input safely; never build a tsquery by hand.
        stmt = sql.SQL(
            """
            SELECT chunk_id, doc_id, text,
                   ts_rank_cd(tsv, websearch_to_tsquery({cfg}, %s)) AS score,
                   metadata
            FROM {table}
            WHERE {where} AND tsv @@ websearch_to_tsquery({cfg}, %s)
            ORDER BY score DESC, chunk_id
            LIMIT %s
            """
        ).format(table=self._ident(self.table), where=where, cfg=sql.Literal(self.ts_config))
        args = [request.query, *params, request.query, depth]
        with self._connect().cursor() as cur:
            cur.execute(stmt, args)
            return self._rows_to_hits(cur.fetchall(), "lexical")

    def _dense(self, request: SearchRequest, depth: int) -> list[SearchHit]:
        from psycopg import sql

        where, params = self._where(request.filters)
        literal = _vec_literal(request.query_vector or [])
        # Stage 1: Hamming over bit(dim) via HNSW. Stage 2: cosine rescore on halfvec.
        stage1_depth = max(depth, int(depth * request.rescore_factor))
        stmt = sql.SQL(
            """
            WITH candidates AS (
                SELECT chunk_id, doc_id, text, metadata, embedding
                FROM {table}
                WHERE {where}
                ORDER BY embedding_bit <~> binary_quantize(%s::vector)::bit({dim})
                LIMIT %s
            )
            SELECT chunk_id, doc_id, text,
                   1 - (embedding <=> %s::halfvec) AS score,
                   metadata
            FROM candidates
            ORDER BY score DESC, chunk_id
            LIMIT %s
            """
        ).format(
            table=self._ident(self.table),
            where=where,
            dim=sql.SQL(str(int(self.dim))),
        )
        args = [*params, literal, stage1_depth, literal, depth]
        with self._connect().cursor() as cur:
            cur.execute(stmt, args)
            return self._rows_to_hits(cur.fetchall(), "dense")

    def search(self, request: SearchRequest) -> SearchResponse:
        self._validate(request.filters)
        started = time.perf_counter()
        depth = request.candidate_depth

        lexical: list[SearchHit] = []
        dense: list[SearchHit] = []
        if request.mode in (SearchMode.LEXICAL, SearchMode.HYBRID):
            lexical = self._lexical(request, depth)
        if request.mode in (SearchMode.DENSE, SearchMode.HYBRID):
            dense = self._dense(request, depth)

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
            debug={"lexical": len(lexical), "dense": len(dense)},
        )

    # ----------------------------------------------------------------- write path

    def create_schema(self) -> None:
        ddl = SCHEMA_SQL.format(
            table=f'"{self.table}"', table_base=self.table, dim=int(self.dim)
        )
        with self._connect().cursor() as cur:
            cur.execute(ddl)

    _PROMOTED = (
        "title",
        "doc_type",
        "source_system",
        "language",
        "created_at",
        "version_status",
        "superseded_by",
        "acl_hash",
    )

    def index(self, chunks: Iterable[Chunk]) -> int:
        import json

        from psycopg import sql

        cols = ["chunk_id", "doc_id", "parent_id", "text", "embedding", *self._PROMOTED, "metadata"]
        stmt = sql.SQL(
            "INSERT INTO {table} ({cols}) VALUES ({ph}) "
            "ON CONFLICT (chunk_id) DO UPDATE SET "
            "text = EXCLUDED.text, embedding = EXCLUDED.embedding, metadata = EXCLUDED.metadata"
        ).format(
            table=self._ident(self.table),
            cols=sql.SQL(", ").join(sql.Identifier(c) for c in cols),
            ph=sql.SQL(", ").join(sql.Placeholder() * len(cols)),
        )
        rows = []
        for chunk in chunks:
            md = dict(chunk.metadata)
            promoted = [md.pop(c, None) for c in self._PROMOTED]
            rows.append(
                [
                    chunk.chunk_id,
                    chunk.doc_id,
                    chunk.parent_id,
                    chunk.text,
                    _vec_literal(chunk.embedding or []),
                    *promoted,
                    json.dumps(md),
                ]
            )
        if not rows:
            return 0
        with self._connect().cursor() as cur:
            cur.executemany(stmt, rows)
        return len(rows)

    def delete_by_doc(self, doc_ids: Iterable[str]) -> int:
        from psycopg import sql

        stmt = sql.SQL("DELETE FROM {table} WHERE doc_id = ANY(%s)").format(
            table=self._ident(self.table)
        )
        with self._connect().cursor() as cur:
            cur.execute(stmt, [list(doc_ids)])
            return cur.rowcount
