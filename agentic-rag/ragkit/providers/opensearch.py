"""OpenSearch provider — the production read path (ADR-001 / D4, D5).

Design notes that matter:

* **One round trip.** Lexical and dense candidate generation go out together in a single
  `_msearch`. Two sequential HTTP calls would add ~15-30 ms to every query for nothing.
* **Binary quantization + rescore.** The index is built with `mode: on_disk` /
  `compression_level: 32x`; queries carry `rescore.oversample_factor` so the engine
  re-ranks Hamming candidates against full-precision vectors. That recovers 95-99% of
  fp32 recall at 32x less memory.
* **Fusion is client-side**, not the `normalization-processor` pipeline, so ranking is
  bit-identical to every other provider.
* **Filters are pre-filters** inside the kNN query. Post-filtering ANN results silently
  destroys recall and is the most common way this pipeline is got wrong.

Requires OpenSearch >= 2.17 for `mode`/`compression_level`/`rescore`.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Iterable

from ..fusion import reciprocal_rank_fusion
from ..provider import RetrievalProvider, register
from ..types import Chunk, Filter, FilterOp, SearchHit, SearchMode, SearchRequest, SearchResponse


def _to_clause(f: Filter) -> dict[str, Any]:
    if f.op is FilterOp.EQ:
        return {"term": {f.field: f.value}}
    if f.op is FilterOp.IN:
        return {"terms": {f.field: list(f.value)}}
    if f.op is FilterOp.RANGE:
        return {"range": {f.field: dict(f.value)}}
    if f.op is FilterOp.PREFIX:
        return {"prefix": {f.field: f.value}}
    if f.op is FilterOp.EXISTS:
        exists = {"exists": {"field": f.field}}
        return exists if f.value else {"bool": {"must_not": exists}}
    raise ValueError(f"unsupported op {f.op}")


def _bool_filter(filters: list[Filter]) -> dict[str, Any] | None:
    if not filters:
        return None
    return {"bool": {"filter": [_to_clause(f) for f in filters]}}


@register
class OpenSearchProvider(RetrievalProvider):
    type_name = "opensearch"

    def __init__(
        self,
        endpoint: str,
        index: str,
        dim: int = 1024,
        filter_fields: Iterable[str] = (),
        vector_field: str = "embedding",
        text_field: str = "text",
        title_field: str = "title",
        doc_id_field: str = "doc_id",
        source_fields: Iterable[str] = (),
        auth: dict[str, Any] | None = None,
        timeout: float = 5.0,
        rrf_k: int = 60,
        weights: tuple[float, float] = (1.0, 1.0),
        ef_search: int | None = None,
        **_: Any,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.index = index
        self.dim = dim
        self.filter_fields = frozenset(filter_fields)
        self.vector_field = vector_field
        self.text_field = text_field
        self.title_field = title_field
        self.doc_id_field = doc_id_field
        self.source_fields = list(source_fields)
        self.auth = auth or {"type": "none"}
        self.timeout = timeout
        self.rrf_k = rrf_k
        self.weights = list(weights)
        self.ef_search = ef_search

    # ------------------------------------------------------------------ transport

    def _sign(self, req: urllib.request.Request, body: bytes) -> None:
        kind = self.auth.get("type", "none")
        if kind == "basic":
            import base64

            user = os.environ.get(self.auth.get("user_env", "OPENSEARCH_USER"), "")
            pwd = os.environ.get(self.auth.get("password_env", "OPENSEARCH_PASSWORD"), "")
            if not user or not pwd:
                raise RuntimeError("basic auth configured but credentials env vars are unset")
            token = base64.b64encode(f"{user}:{pwd}".encode("utf-8")).decode("ascii")
            req.add_header("Authorization", f"Basic {token}")
        elif kind == "sigv4":
            try:
                from botocore.auth import SigV4Auth
                from botocore.awsrequest import AWSRequest
                from botocore.session import Session
            except ImportError as exc:  # pragma: no cover - env dependent
                raise RuntimeError("sigv4 auth needs botocore installed") from exc
            session = Session()
            creds = session.get_credentials()
            if creds is None:
                raise RuntimeError("no AWS credentials resolved for sigv4 auth")
            aws_req = AWSRequest(
                method=req.get_method(),
                url=req.full_url,
                data=body,
                headers={"Content-Type": "application/json"},
            )
            SigV4Auth(
                creds.get_frozen_credentials(),
                self.auth.get("service", "es"),
                self.auth["region"],
            ).add_auth(aws_req)
            for key, value in aws_req.headers.items():
                req.add_header(key, value)

    def _request(self, method: str, path: str, body: str | None = None) -> dict[str, Any]:
        raw = (body or "").encode("utf-8")
        content_type = "application/x-ndjson" if path.endswith(("_msearch", "_bulk")) else "application/json"
        req = urllib.request.Request(
            f"{self.endpoint}{path}",
            data=raw if body is not None else None,
            method=method,
            headers={"Content-Type": content_type},
        )
        self._sign(req, raw)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            raise RuntimeError(f"opensearch {method} {path} -> {exc.code}: {detail}") from exc

    # ------------------------------------------------------------------ read path

    def health(self) -> bool:
        try:
            body = self._request("GET", "/_cluster/health")
        except RuntimeError:
            return False
        return body.get("status") in ("green", "yellow")

    def _source(self) -> list[str]:
        fields = [self.doc_id_field, self.text_field, *self.source_fields]
        return list(dict.fromkeys(fields))

    def _lexical_body(self, request: SearchRequest, depth: int) -> dict[str, Any]:
        query: dict[str, Any] = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": request.query,
                            "fields": [f"{self.text_field}^1.0", f"{self.title_field}^2.0"],
                            "type": "best_fields",
                        }
                    }
                ]
            }
        }
        if request.filters:
            query["bool"]["filter"] = [_to_clause(f) for f in request.filters]
        return {"size": depth, "query": query, "_source": self._source()}

    def _dense_body(self, request: SearchRequest, depth: int) -> dict[str, Any]:
        knn: dict[str, Any] = {
            "vector": request.query_vector,
            "k": depth,
            "rescore": {"oversample_factor": request.rescore_factor},
        }
        clause = _bool_filter(request.filters)
        if clause is not None:
            knn["filter"] = clause
        if self.ef_search is not None:
            knn["method_parameters"] = {"ef_search": self.ef_search}
        return {
            "size": depth,
            "query": {"knn": {self.vector_field: knn}},
            "_source": self._source(),
        }

    def _hits(self, response: dict[str, Any], retriever: str) -> list[SearchHit]:
        out: list[SearchHit] = []
        for rank, raw in enumerate(response.get("hits", {}).get("hits", []), start=1):
            src = raw.get("_source", {})
            metadata = {k: v for k, v in src.items() if k not in (self.text_field,)}
            out.append(
                SearchHit(
                    chunk_id=raw["_id"],
                    doc_id=str(src.get(self.doc_id_field, raw["_id"])),
                    score=float(raw.get("_score") or 0.0),
                    rank=rank,
                    text=src.get(self.text_field, ""),
                    metadata=metadata,
                    retriever=retriever,
                )
            )
        return out

    def search(self, request: SearchRequest) -> SearchResponse:
        self._validate(request.filters)
        started = time.perf_counter()
        depth = request.candidate_depth
        header = json.dumps({"index": self.index})

        bodies: list[tuple[str, dict[str, Any]]] = []
        if request.mode in (SearchMode.LEXICAL, SearchMode.HYBRID):
            bodies.append(("lexical", self._lexical_body(request, depth)))
        if request.mode in (SearchMode.DENSE, SearchMode.HYBRID):
            bodies.append(("dense", self._dense_body(request, depth)))

        ndjson = "".join(f"{header}\n{json.dumps(b)}\n" for _, b in bodies)
        payload = self._request("POST", "/_msearch", ndjson)
        responses = payload.get("responses", [])
        if len(responses) != len(bodies):
            raise RuntimeError(f"_msearch returned {len(responses)} of {len(bodies)} responses")

        ranked: dict[str, list[SearchHit]] = {}
        for (name, _), resp in zip(bodies, responses):
            if "error" in resp:
                raise RuntimeError(f"{name} search failed: {json.dumps(resp['error'])[:400]}")
            ranked[name] = self._hits(resp, name)

        if request.mode is SearchMode.HYBRID:
            hits = reciprocal_rank_fusion(
                [ranked["lexical"], ranked["dense"]],
                weights=self.weights,
                k_rrf=self.rrf_k,
                limit=request.k,
            )
        else:
            hits = next(iter(ranked.values()))[: request.k]

        if not request.include_text:
            for h in hits:
                h.text = ""

        return SearchResponse(
            hits=hits,
            took_ms=(time.perf_counter() - started) * 1000.0,
            provider=self.type_name,
            mode=request.mode,
            debug={
                "took_os_ms": sum(r.get("took", 0) for r in responses),
                **{f"{name}_candidates": len(v) for name, v in ranked.items()},
            },
        )

    # ----------------------------------------------------------------- write path

    def index_chunks(self, chunks: Iterable[Chunk], refresh: bool = False) -> int:
        lines: list[str] = []
        count = 0
        for chunk in chunks:
            lines.append(json.dumps({"index": {"_index": self.index, "_id": chunk.chunk_id}}))
            doc: dict[str, Any] = {
                self.doc_id_field: chunk.doc_id,
                self.text_field: chunk.text,
                "parent_id": chunk.parent_id,
                **chunk.metadata,
            }
            if chunk.embedding is not None:
                doc[self.vector_field] = chunk.embedding
            lines.append(json.dumps(doc))
            count += 1
        if not count:
            return 0
        suffix = "?refresh=true" if refresh else ""
        body = self._request("POST", f"/_bulk{suffix}", "\n".join(lines) + "\n")
        if body.get("errors"):
            first = next(
                (i for i in body.get("items", []) if i.get("index", {}).get("error")), None
            )
            raise RuntimeError(f"bulk index had failures: {json.dumps(first)[:400]}")
        return count

    def index(self, chunks: Iterable[Chunk]) -> int:
        return self.index_chunks(chunks, refresh=True)

    def delete_by_doc(self, doc_ids: Iterable[str]) -> int:
        body = json.dumps({"query": {"terms": {self.doc_id_field: list(doc_ids)}}})
        result = self._request("POST", f"/{self.index}/_delete_by_query?refresh=true", body)
        return int(result.get("deleted", 0))
