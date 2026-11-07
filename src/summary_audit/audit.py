"""The audit pipeline: for every log (planted canaries + unplanted originals), the monitor reads the full log and the
summarizer's chunk summaries; every monitor call becomes one row of calls.jsonl."""
import asyncio

from . import prompts
from .llm import CapReached
from .logs import chunks_of

MAX_TOK = {"summarize": 4000, "full": 8000, "summary": 3000}


async def call(llm, model, prompt, kind, need_score=False, attempts=3):
    """Returns (text, error, cost). Up to `attempts` tries; a monitor reply without a parsable SCORE counts as a failed try."""
    last, err, cost = None, None, 0.0
    for _ in range(attempts):
        r = await llm.complete(model, prompt, MAX_TOK[kind], kind)
        cost += r.cost
        if r.err is None and r.text and r.text.strip() and (not need_score or prompts.score_of(r.text) is not None):
            return prompts.strip_think(r.text), None, cost
        err = r.err or ("empty reply" if not (r.text or "").strip() else "no parsable SCORE")
        if getattr(r, "fatal", False):
            break
    return None, err, cost


def make_prompts(log, cfg):
    team = cfg["team_desc"] or log["team"] or prompts.generic_team(log["agents"])
    preset = prompts.PRESETS.get(log["format"], prompts.PRESETS["jsonl"])
    task = cfg["task_desc"] or prompts.task_text(preset["target"])
    sum_instr = cfg["sum_desc"] or prompts.sum_text(preset["target"])
    return team, task, sum_instr


def row(log, view, summarizer, monitor, score, err, threshold, cost, **extra):
    return dict({"log": log["id"], "planted": log["planted"], "deal": log["deal"], "view": view, "summarizer": summarizer,
                 "monitor": monitor, "score": score, "flagged": (score >= threshold) if score is not None else None,
                 "error": err, "cost_usd": round(cost, 6)}, **extra)


async def audit_log(log, llm, cfg, rows, summaries):
    msgs, n = log["msgs"], len(log["msgs"])
    team, task, sum_instr = make_prompts(log, cfg)
    segs = chunks_of(msgs, cfg["chunk"])
    thr = cfg["threshold"]

    async def monitor_full(mon):
        t, err, cost = await call(llm, mon, prompts.full_prompt(team, task, msgs), "full", need_score=True)
        rows.append(row(log, "FULL", None, mon, prompts.score_of(t), err, thr, cost))

    async def summarize_then_monitor(s):
        res = await asyncio.gather(*[call(llm, s, prompts.summarizer_prompt(team, sum_instr, msgs, a, b), "summarize")
                                     for a, b in segs])
        sums = [t or "(summary unavailable)" for t, _, _ in res]
        scost = sum(c for _, _, c in res)
        nerr = sum(1 for t, _, _ in res if t is None)
        inj = [i for i, m in enumerate(msgs) if m["inj"]]
        span = len({k for k, (a, b) in enumerate(segs) for i in inj if a <= i < b})
        summaries.append({"log": log["id"], "summarizer": s, "chunks": [list(x) for x in segs], "summaries": sums,
                          "sum_err": nerr, "span": span, "cost_usd": round(scost, 6)})
        if nerr == len(segs):  # nothing to read
            for mon in cfg["monitors"]:
                rows.append(row(log, "SUMMARY", s, mon, None, "all summaries failed", thr, 0.0))
            return
        p = prompts.summary_judge_prompt(team, task, segs, sums, n)

        async def one(mon):
            t, err, cost = await call(llm, mon, p, "summary", need_score=True)
            rows.append(row(log, "SUMMARY", s, mon, prompts.score_of(t), err, thr, cost, sum_err=nerr, span=span))
        await asyncio.gather(*[one(m) for m in cfg["monitors"]])

    jobs = [monitor_full(m) for m in cfg["monitors"]] + [summarize_then_monitor(s) for s in cfg["summarizers"]]
    for r in await asyncio.gather(*jobs, return_exceptions=True):
        if isinstance(r, CapReached):
            rows.append({"log": log["id"], "planted": log["planted"], "deal": log["deal"], "view": "SKIPPED_CAP",
                         "summarizer": None, "monitor": None, "score": None, "flagged": None, "error": str(r), "cost_usd": 0.0})
        elif isinstance(r, Exception):
            raise r


async def run_audit(logs, llm, cfg, progress=None):
    rows, summaries = [], []
    sem = asyncio.Semaphore(cfg["log_parallel"])

    async def one(lg):
        async with sem:
            await audit_log(lg, llm, cfg, rows, summaries)
            if progress:
                progress(lg)
    await asyncio.gather(*[one(lg) for lg in logs])
    return rows, summaries
