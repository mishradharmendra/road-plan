"""ragkit CLI.

    python -m ragkit search --config eval/configs/retrieval.json --query "AUTH-5031"
    python -m ragkit search --config eval/configs/retrieval.json          # REPL
    python -m ragkit retrieval-eval --config eval/configs/retrieval.json
    python -m ragkit retrieval-eval --config eval/configs/retrieval.pgvector.json
    python -m ragkit index --config eval/configs/retrieval.pgvector.json
    python -m ragkit schema --dim 1024 --table chunks
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .embeddings import build_embedder
from .evaluate import (
    EvalReport,
    check_gates,
    export_evalkit_dataset,
    load_corpus,
    prepare,
    run_eval,
)
from .provider import build_provider
from .types import Filter, FilterError, FilterOp, SearchMode, SearchRequest


def _load_config(path: str) -> tuple[dict[str, Any], Path]:
    cfg_path = Path(path).resolve()
    with open(cfg_path, "r", encoding="utf-8") as fh:
        config = json.load(fh)
    return config, cfg_path.parent


def _fmt(value: float) -> str:
    return "  n/a " if value != value else f"{value:6.4f}"


def _print_report(report: EvalReport) -> None:
    print()
    print(f"  {report.name}  |  provider={report.provider}  mode={report.mode}  "
          f"match_on={report.match_on}  n={report.n_queries}")
    print("  " + "-" * 66)
    print(f"  {'k':>5}  {'recall':>8}  {'precision':>10}  {'ndcg':>8}  {'hit_rate':>9}  {'95% CI':>16}")
    for k in report.k_values:
        lo, hi = report.intervals[f"hit_rate@{k}"]
        print(
            f"  {k:>5}  {_fmt(report.metrics[f'recall@{k}']):>8}"
            f"  {_fmt(report.metrics[f'precision@{k}']):>10}"
            f"  {_fmt(report.metrics[f'ndcg@{k}']):>8}"
            f"  {_fmt(report.metrics[f'hit_rate@{k}']):>9}"
            f"   [{lo:.3f}, {hi:.3f}]"
        )
    print("  " + "-" * 66)
    print(f"  MRR {report.metrics['mrr']:.4f}   "
          f"latency p50 {report.metrics['latency_p50_ms']:.1f} ms   "
          f"p95 {report.metrics['latency_p95_ms']:.1f} ms")

    if report.slices:
        print("\n  slices")
        for name, values in sorted(report.slices.items()):
            recall_key = next(k for k in values if k not in ("n", "scored"))
            scored = int(values["scored"])
            suffix = "" if scored == int(values["n"]) else f" (scored {scored})"
            print(
                f"    {name:<28} n={int(values['n']):<4} "
                f"{recall_key} {_fmt(values[recall_key])}{suffix}"
            )

    if report.misses:
        shown = ", ".join(report.misses[:12])
        more = f" (+{len(report.misses) - 12} more)" if len(report.misses) > 12 else ""
        print(f"\n  total misses ({len(report.misses)}): {shown}{more}")
        print("  -> a miss is unrecoverable downstream; no reranker or LLM can fix it.")


def cmd_retrieval_eval(args: argparse.Namespace) -> int:
    config, base = _load_config(args.config)
    if args.mode:
        config["mode"] = args.mode
    if args.provider:
        config.setdefault("provider", {})["type"] = args.provider

    report, retrieved = run_eval(config, base, limit=args.limit)
    _print_report(report)

    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report.to_dict(), fh, indent=2)
        print(f"\n  wrote {args.json}")

    if args.export_evalkit:
        n = export_evalkit_dataset(retrieved, Path(args.export_evalkit), top_n=args.context_size)
        print(f"  wrote {n} evalkit samples to {args.export_evalkit}")

    failures = [] if args.no_gates else check_gates(report, config.get("gates") or {})
    if failures:
        print("\n  GATES FAILED")
        for f in failures:
            print(f"    x {f}")
        return 1
    print("\n  gates passed" if config.get("gates") and not args.no_gates else "")
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    config, base = _load_config(args.config)
    embedder = build_embedder(config.get("embedder") or {"type": "hashing", "dim": 256})
    provider = build_provider(config["provider"])
    if hasattr(provider, "create_schema") and args.create_schema:
        provider.create_schema()
        print("  schema created")
    corpus = load_corpus(base / config["corpus"])
    vectors = embedder.embed([c.text for c in corpus], kind="document")
    for chunk, vec in zip(corpus, vectors):
        chunk.embedding = vec
    n = provider.index(corpus)
    provider.close()
    print(f"  indexed {n} chunks into {config['provider']['type']}")
    return 0


def cmd_schema(args: argparse.Namespace) -> int:
    from .providers.pgvector import SCHEMA_SQL

    print(SCHEMA_SQL.format(table=f'"{args.table}"', table_base=args.table, dim=args.dim))
    return 0


def _parse_filters(raw: list[str]) -> list[Filter]:
    filters: list[Filter] = []
    for item in raw:
        if "=" not in item:
            raise SystemExit(f"--filter expects field=value, got {item!r}")
        field, value = item.split("=", 1)
        filters.append(Filter(field.strip(), FilterOp.EQ, value.strip()))
    return filters


def _run_one(provider, embedder, query: str, args: argparse.Namespace) -> None:
    mode = SearchMode(args.mode)
    vector = None if mode is SearchMode.LEXICAL else embedder.embed_one(query, kind="query")
    try:
        response = provider.search(
            SearchRequest(
                query=query,
                k=args.k,
                mode=mode,
                filters=_parse_filters(args.filter or []),
                query_vector=vector,
            )
        )
    except FilterError as exc:
        print(f"  filter rejected: {exc}")
        return

    print(f"\n  {len(response.hits)} hits in {response.took_ms:.1f} ms  ({response.debug})")
    for hit in response.hits:
        snippet = " ".join(hit.text.split())[:110]
        print(f"\n  {hit.rank:>2}. {hit.score:.4f}  {hit.doc_id}  [{hit.retriever}]")
        print(f"      {hit.chunk_id}")
        if snippet:
            print(f"      {snippet}...")


def cmd_search(args: argparse.Namespace) -> int:
    config, base = _load_config(args.config)
    args.mode = args.mode or config.get("mode", "hybrid")
    embedder, provider = prepare(config, base)

    if args.query:
        _run_one(provider, embedder, args.query, args)
        provider.close()
        return 0

    print(f"  {config.get('name')}  provider={config['provider']['type']}  mode={args.mode}")
    print("  type a query, or ctrl-d to quit")
    try:
        while True:
            try:
                query = input("\n  > ").strip()
            except EOFError:
                break
            if not query:
                continue
            if query in ("quit", "exit"):
                break
            _run_one(provider, embedder, query, args)
    finally:
        provider.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ragkit")
    sub = parser.add_subparsers(dest="command", required=True)

    se = sub.add_parser("search", help="run a query; omit --query for a REPL")
    se.add_argument("--config", required=True)
    se.add_argument("--query")
    se.add_argument("-k", type=int, default=5)
    se.add_argument("--mode", choices=["lexical", "dense", "hybrid"])
    se.add_argument("--filter", action="append", metavar="field=value")
    se.set_defaults(func=cmd_search)

    ev = sub.add_parser("retrieval-eval", help="score a provider against the golden set")
    ev.add_argument("--config", required=True)
    ev.add_argument("--provider", help="override provider type (portability check)")
    ev.add_argument("--mode", choices=["lexical", "dense", "hybrid"])
    ev.add_argument("--limit", type=int)
    ev.add_argument("--json", help="write the aggregate report here")
    ev.add_argument("--export-evalkit", help="write retrieved context as an evalkit dataset")
    ev.add_argument("--context-size", type=int, default=8)
    ev.add_argument("--no-gates", action="store_true")
    ev.set_defaults(func=cmd_retrieval_eval)

    ix = sub.add_parser("index", help="embed and load the corpus into the configured provider")
    ix.add_argument("--config", required=True)
    ix.add_argument("--create-schema", action="store_true")
    ix.set_defaults(func=cmd_index)

    sc = sub.add_parser("schema", help="print the pgvector DDL")
    sc.add_argument("--table", default="chunks")
    sc.add_argument("--dim", type=int, default=1024)
    sc.set_defaults(func=cmd_schema)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
