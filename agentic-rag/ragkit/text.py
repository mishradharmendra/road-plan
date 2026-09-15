"""Shared text utilities. Deliberately dependency-free."""

from __future__ import annotations

import re
import unicodedata

_TOKEN = re.compile(r"[a-z0-9]+(?:[-_./][a-z0-9]+)*")

# Kept small on purpose: aggressive stoplists delete the exact tokens enterprise
# queries hinge on ("not", "before", "under").
_STOP = frozenset(
    "a an the of for to in on at by is are was were be been and or as it its this that".split()
)


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold().strip()


def tokenize(text: str, drop_stopwords: bool = True) -> list[str]:
    """Lowercase word tokens, keeping intra-token `-_./`.

    Part numbers, error codes and policy IDs (`SKU-1023/A`, `err.timeout_ms`) must stay
    single tokens — splitting them is a direct hit to lexical recall, which is the whole
    reason BM25 is in the pipeline.
    """
    toks = _TOKEN.findall(normalize(text))
    if drop_stopwords:
        toks = [t for t in toks if t not in _STOP]
    return toks
