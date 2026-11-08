#!/usr/bin/env python3
"""E14 training data: (shipped-framework summary prompt + one set-A chunk) -> summary written by a summarizer that the
canary audit cleared under our oversight-aware prompt (the teacher). Set A only. Set B (held-out deals) is never used
for training. Control logs from two held-out runs are excluded so false alarms can be measured on unseen controls.

Training prompts are drawn from four shipped prompts (LangChain v1, LangChain-classic, LangMem, CrewAI). LlamaIndex's
prompt and our own prompt are held out for testing. Output: ../data/train.csv (prompt, completion) and manifest.json.
  uv run --no-project --with openai --with scipy python e14_build_data.py
"""
import csv
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
EXPS = EXP.parent
sys.path.insert(0, str(EXPS / "E12-framework-prompts" / "code"))
_argv, sys.argv = sys.argv, sys.argv[:1]
import e12_run as e12  # noqa: E402
sys.argv = _argv
base, e2 = e12.base, e12.e2
PIL = Path("/Users/macstudio/research-taste/swarm-alignment/pilots/2026-11-06")
TEACHERS = {   # summarizer: set-A record files (SUM_SAFETY prompt); held-out result under our prompt in parentheses
    "gemini-4-argon (held-out -21.0)": [EXPS / "E2b-canary-pass-side/results/A_sum_gemini-4-argon.jsonl"],
    "claude-opus-5.5 (held-out -20.5)": [EXPS / "E2d-canary-pass-side-3/results/A_sum_claude-opus-5.5.jsonl"],
    "gemini-3.8-flash (held-out -14.5)": [PIL / "loop2d/runs/sum_gemini-3.8-flash_c50.jsonl"],
    "gemini-3.7-flash (held-out -7.4)": [EXPS / "E9-far-rule-prospective/results/A_split_gemini-3.7-flash.jsonl",
                                         EXPS / "E9-far-rule-prospective/results/A_controls_gemini-3.7-flash.jsonl"],
    "claude-opus-5 (canary -11.1)": [EXPS / "E10-far-pass-side/results/A_split_claude-opus-5.jsonl",
                                     EXPS / "E10-far-pass-side/results/A_controls_claude-opus-5.jsonl"],
    "gemini-3.6-flash (canary -1.6)": [EXPS / "E10-far-pass-side/results/A_split_gemini-3.6-flash.jsonl",
                                       EXPS / "E10-far-pass-side/results/A_controls_gemini-3.6-flash.jsonl"],
    "gemini-3.5-flash (canary -3.2)": [EXPS / "E10-far-pass-side/results/A_split_gemini-3.5-flash.jsonl",
                                       EXPS / "E10-far-pass-side/results/A_controls_gemini-3.5-flash.jsonl"],
}
TRAIN_PROMPTS = ["langchain", "lc-classic", "langmem", "crewai"]
HELDOUT_CTRL_RUNS = {"practice_05", "practice_07"}   # their CLEAN/LEGIT logs are test-only (most control logs per run)


def flatten(msgs):
    """Chat messages -> one instruction string (system text first), the form AutoScientist's instruction format takes."""
    return "\n\n".join(m["content"] for m in msgs)


def main():
    logs = {lg["id"]: lg for lg in e2.logs_A("split") + e2.logs_A("controls")}
    rng = random.Random(14)
    rows, skipped = [], {"unavailable": 0, "short": 0, "heldout_ctrl": 0, "not_setA": 0, "chunk_mismatch": 0}
    per_teacher = {}
    for t, files in TEACHERS.items():
        recs = {}
        for f in files:
            for x in open(f):
                r = json.loads(x)
                recs[r["log"]] = r
        n = 0
        for lid, r in recs.items():
            lg = logs.get(lid)
            if lg is None:
                skipped["not_setA"] += 1
                continue
            if lg["cond"] in ("CLEAN", "LEGIT") and lid.split("|")[0] in HELDOUT_CTRL_RUNS:
                skipped["heldout_ctrl"] += 1
                continue
            segs = base.chunks_of(lg["msgs"])
            if len(segs) != len(r["summaries"]):
                skipped["chunk_mismatch"] += 1
                continue
            for (a, b), s in zip(segs, r["summaries"]):
                if not s or s == "(summary unavailable)":
                    skipped["unavailable"] += 1
                    continue
                if len(s.split()) < 25:
                    skipped["short"] += 1
                    continue
                fw = rng.choice(TRAIN_PROMPTS)
                prompt = flatten(e12.build(fw, base.fmt(lg["msgs"][a:b], a), False, a, b, len(lg["msgs"])))
                rows.append({"prompt": prompt, "completion": s.strip(), "teacher": t, "log": lid, "cond": lg["cond"],
                             "chunk": f"{a}-{b}", "prompt_template": fw})
                n += 1
        per_teacher[t] = n
    rng.shuffle(rows)
    out = EXP / "data"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "train.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["prompt", "completion"])
        w.writeheader()
        for r in rows:
            w.writerow({"prompt": r["prompt"], "completion": r["completion"]})
    meta = [{k: v for k, v in r.items() if k not in ("prompt", "completion")} for r in rows]
    json.dump({"n_rows": len(rows), "per_teacher": per_teacher, "skipped": skipped, "train_prompts": TRAIN_PROMPTS,
               "heldout_ctrl_runs": sorted(HELDOUT_CTRL_RUNS), "conds": {c: sum(m["cond"] == c for m in meta)
                                                                         for c in ("SPLIT", "CLEAN", "LEGIT")},
               "rows": meta}, open(out / "manifest.json", "w"), indent=1)
    print(f"rows {len(rows)}; per teacher {per_teacher}; skipped {skipped}; "
          f"mean prompt chars {sum(len(r['prompt']) for r in rows) / len(rows):.0f}, "
          f"mean completion words {sum(len(r['completion'].split()) for r in rows) / len(rows):.0f}")


if __name__ == "__main__":
    main()
