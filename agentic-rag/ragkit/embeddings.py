"""Embedding contract + implementations.

The provider never owns model choice (ADR-001 / D8): callers embed and pass vectors in.
That keeps the Databricks/Bedrock/self-hosted decision independent of the index.
"""

from __future__ import annotations

import abc
import hashlib
import json
import math
import os
import urllib.error
import urllib.request
from typing import Any, Sequence

from .text import tokenize


class EmbeddingProvider(abc.ABC):
    type_name: str = "embedder"
    dim: int = 0

    @abc.abstractmethod
    def embed(self, texts: Sequence[str], kind: str = "document") -> list[list[float]]: ...

    def embed_one(self, text: str, kind: str = "query") -> list[float]:
        return self.embed([text], kind=kind)[0]


def l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


class HashingEmbedder(EmbeddingProvider):
    """Deterministic feature-hashing embedder.

    Not a semantic model. It hashes tokens (and token bigrams) into `dim` buckets with
    signed weights, so cosine similarity tracks *lexical* overlap only. Its purpose is
    to make the retrieval eval and the portability test run offline and reproducibly on
    any machine with no GPU, no network, and no model download.

    Never benchmark retrieval quality with this — benchmark the *pipeline* with it, and
    swap in `HttpEmbedder` for real numbers.
    """

    type_name = "hashing"

    def __init__(self, dim: int = 256, bigrams: bool = True, **_: Any):
        if dim < 8:
            raise ValueError("dim must be >= 8")
        self.dim = dim
        self.bigrams = bigrams

    def _features(self, text: str) -> list[str]:
        toks = tokenize(text)
        feats = list(toks)
        if self.bigrams:
            feats += [f"{a}_{b}" for a, b in zip(toks, toks[1:])]
        return feats

    def embed(self, texts: Sequence[str], kind: str = "document") -> list[list[float]]:
        out: list[list[float]] = []
        for text in texts:
            vec = [0.0] * self.dim
            for feat in self._features(text):
                digest = hashlib.blake2b(feat.encode("utf-8"), digest_size=8).digest()
                idx = int.from_bytes(digest[:4], "big") % self.dim
                sign = 1.0 if digest[4] & 1 else -1.0
                vec[idx] += sign
            out.append(l2_normalize(vec))
        return out


class HttpEmbedder(EmbeddingProvider):
    """OpenAI-compatible `/v1/embeddings` client.

    One implementation covers Databricks Model Serving, Bedrock via a gateway, vLLM, and
    HuggingFace TEI — which is the point: the embedding vendor is a URL, not a rewrite.
    """

    type_name = "http"

    def __init__(
        self,
        url: str,
        model: str,
        dim: int,
        api_key_env: str = "EMBEDDINGS_API_KEY",
        batch_size: int = 64,
        timeout: float = 30.0,
        query_prefix: str = "",
        document_prefix: str = "",
        **_: Any,
    ):
        self.url = url.rstrip("/")
        self.model = model
        self.dim = dim
        self.api_key_env = api_key_env
        self.batch_size = batch_size
        self.timeout = timeout
        self.query_prefix = query_prefix
        self.document_prefix = document_prefix

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        token = os.environ.get(self.api_key_env)
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def embed(self, texts: Sequence[str], kind: str = "document") -> list[list[float]]:
        prefix = self.query_prefix if kind == "query" else self.document_prefix
        out: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = [prefix + t for t in texts[start : start + self.batch_size]]
            payload = json.dumps({"model": self.model, "input": batch}).encode("utf-8")
            req = urllib.request.Request(
                f"{self.url}/v1/embeddings", data=payload, headers=self._headers()
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                raise RuntimeError(
                    f"embedding endpoint {self.url} returned {exc.code}"
                ) from exc
            for row in sorted(body["data"], key=lambda d: d["index"]):
                out.append(l2_normalize([float(v) for v in row["embedding"]]))
        return out


REGISTRY: dict[str, type[EmbeddingProvider]] = {
    HashingEmbedder.type_name: HashingEmbedder,
    HttpEmbedder.type_name: HttpEmbedder,
}


def build_embedder(spec: dict[str, Any]) -> EmbeddingProvider:
    spec = dict(spec)
    kind = spec.pop("type", "hashing")
    if kind not in REGISTRY:
        raise ValueError(f"unknown embedder {kind!r}; have {sorted(REGISTRY)}")
    return REGISTRY[kind](**spec)
