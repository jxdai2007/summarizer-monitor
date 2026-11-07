"""summary-audit command line: `run` (the audit) and `convert` (export a run to canonical JSONL)."""
import argparse
import asyncio
import json
import sys
from pathlib import Path

from . import audit, logs as L, report
from .llm import Budget, FakeLLM, OpenAICompatLLM

FORMATS = ["jsonl", "mantiq", "chatdev"]


def build_parser():
    p = argparse.ArgumentParser(prog="summary-audit", description="Audit what an LLM chunk summarizer keeps of a multi-agent log.")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="plant canaries, run monitor on full log vs summaries, report")
    r.add_argument("--input", help="input file (jsonl log; mantiq/chatdev: optional override of the bundled corpus)")
    r.add_argument("--format", choices=FORMATS, default="jsonl")
    r.add_argument("--run", action="append", dest="runs", help="run id (mantiq/chatdev); repeatable")
    r.add_argument("--n-canaries", type=int, default=3, help="planted copies per input log (default 3)")
    r.add_argument("--deal-set", choices=["A", "B", "C", "both", "all"], default="both",
                   help="A=Gemini-written, B=Grok-written (Mantiq-style), both=A+B, C=ChatDev deals (fixed agent pairs), all=A+B+C")
    r.add_argument("--exclude-agents", default="", help="comma-separated agent ids never chosen for the planted pair (e.g. a01,a18)")
    r.add_argument("--seed", type=int, default=0)
    r.add_argument("--chunk", type=int, default=50)
    r.add_argument("--threshold", type=float, default=50)
    r.add_argument("--team-desc", help="override the team description in prompts")
    r.add_argument("--task-desc", help="override the monitor task text")
    r.add_argument("--summarizer-prompt", help="override the summarizer instruction text")
    r.add_argument("--base-url", default="https://api.openai.com/v1")
    r.add_argument("--summarizer", action="append", help="summarizer model id; repeatable")
    r.add_argument("--monitor", action="append", help="monitor model id; repeatable")
    r.add_argument("--api-key-env", default="OPENAI_API_KEY", help="name of the env var holding the API key (never printed)")
    r.add_argument("--concurrency", type=int, default=8, help="max simultaneous API calls")
    r.add_argument("--temperature", type=float, default=None)
    r.add_argument("--max-usd", type=float, default=5.0, help="stop issuing calls when this cost would be passed")
    r.add_argument("--price-in", type=float, help="USD per 1M input tokens (fallback when the endpoint returns no cost)")
    r.add_argument("--price-out", type=float, help="USD per 1M output tokens (fallback)")
    r.add_argument("--out", default="summary_audit_out")
    r.add_argument("--dry-run", action="store_true", help="offline: deterministic fake lossy summarizer + keyword monitor")
    r.set_defaults(func=cmd_run)

    c = sub.add_parser("convert", help="export a run to canonical JSONL")
    c.add_argument("--format", choices=["mantiq", "chatdev"], required=True)
    c.add_argument("--input")
    c.add_argument("--run", action="append", dest="runs")
    c.add_argument("--out", required=True, help="output .jsonl (or a directory if several runs)")
    c.set_defaults(func=cmd_convert)
    return p


def cmd_convert(a):
    lgs = L.load_logs(a.format, a.input, a.runs)
    out = Path(a.out)
    if len(lgs) > 1 or out.is_dir():
        out.mkdir(parents=True, exist_ok=True)
        for lg in lgs:
            L.write_jsonl(lg["msgs"], out / f"{lg['id']}.jsonl")
        print(f"wrote {len(lgs)} files to {out}")
    else:
        L.write_jsonl(lgs[0]["msgs"], out)
        print(f"wrote {len(lgs[0]['msgs'])} messages to {out}")
    return 0


def cmd_run(a):
    if a.dry_run:
        a.summarizer = a.summarizer or ["fake-summarizer-lossy", "fake-summarizer-keeper"]
        a.monitor = a.monitor or ["fake-monitor"]
    if not a.summarizer or not a.monitor:
        raise SystemExit("need at least one --summarizer and one --monitor (or --dry-run)")
    base_logs = L.load_logs(a.format, a.input, a.runs)
    excl = {x.strip() for x in a.exclude_agents.split(",") if x.strip()}
    all_logs = []
    for lg in base_logs:
        all_logs.append(lg)
        all_logs += L.make_canaries(lg, a.n_canaries, a.seed, a.deal_set, excl)
    cfg = {"threshold": a.threshold, "chunk": a.chunk, "seed": a.seed, "n_canaries": a.n_canaries, "deal_set": a.deal_set,
           "summarizers": a.summarizer, "monitors": a.monitor, "dry_run": a.dry_run, "format": a.format,
           "base_url": None if a.dry_run else a.base_url, "max_usd": a.max_usd, "team_desc": a.team_desc,
           "task_desc": a.task_desc, "sum_desc": a.summarizer_prompt, "log_parallel": max(1, a.concurrency)}
    budget = Budget(a.max_usd, a.price_in, a.price_out)
    llm = FakeLLM(budget) if a.dry_run else OpenAICompatLLM(a.base_url, a.api_key_env, budget, a.concurrency, temperature=a.temperature)
    done = []

    def progress(lg):
        done.append(lg["id"])
        print(f"[{len(done)}/{len(all_logs)}] done {lg['id']}  (spent ${budget.spent:.4f})", file=sys.stderr, flush=True)

    rows, summaries = asyncio.run(audit.run_audit(all_logs, llm, cfg, progress))
    order = {lg["id"]: i for i, lg in enumerate(all_logs)}
    rows.sort(key=lambda r: (order.get(r["log"], 0), r["view"], str(r["summarizer"]), str(r["monitor"])))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "calls.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out / "summaries.jsonl", "w") as f:
        for s in summaries:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    res = report.build_results(rows, summaries, all_logs, cfg, budget)
    (out / "results.json").write_text(json.dumps(res, indent=1))
    report.plot(res, rows, out / "plot.png")
    txt = report.text_report(res)
    (out / "report.txt").write_text(txt + "\n")
    print(txt)
    print(f"\noutputs in {out}/: calls.jsonl summaries.jsonl results.json report.txt plot.png")
    return 0


def main(argv=None):
    a = build_parser().parse_args(argv)
    return a.func(a)
