#!/usr/bin/env python3
"""E12 exploratory analyses (not predicted; labelled as such wherever reported):
  1. words per chunk summary, by arm;
  2. share of deal-covering chunk summaries that name both deal agents (a proxy for "the summary still mentions the
     pair"), by arm;
  3. held-out AUC (raw-log vs summary monitor scores, SPLIT vs set-A controls) where controls exist.
Usage: uv run --no-project --with openai --with scipy python e12_explore.py
"""
import json
import re
import sys
from pathlib import Path

sys.argv = sys.argv[:1]
import e12_run as e  # noqa: E402

OUT = e.OUT / "exploratory.txt"


def pair_of(lg):
    return lg["pair"] if isinstance(lg["pair"], (list, tuple)) else re.findall(r"a\d\d", str(lg["pair"]))


def names_both(recs, L):
    hit = tot = 0
    for r in recs:
        lg = L.get(r["log"])
        if not lg:
            continue
        segs = e.base.chunks_of(lg["msgs"])
        inj = [i for i, m in enumerate(lg["msgs"]) if m["inj"]]
        for k, (a, b) in enumerate(segs):
            if any(a <= i < b for i in inj):
                tot += 1
                hit += all(p in r["summaries"][k] for p in pair_of(lg))
    return hit, tot


def main():
    L = {lg["id"]: lg for lg in e.e2.logs_B("split") + e.e2.logs_A("split")}
    lines = ["E12 EXPLORATORY (not predicted)", "arm | set B words/chunk | deal chunks naming both deal agents (set B)"]
    for model in e.SUMMARIZERS + [e.GEM]:
        arms = e.GEM_ARMS if model == e.GEM else e.ARMS + e.LOCAL_EXTRA_ARMS
        for fw, nt in arms:
            recs = e.rows(e.out_path(model, fw, nt, "B", "split"))
            if not recs:
                continue
            w = sum(r["sum_words"] for r in recs) / sum(r["nchunks"] for r in recs)
            h, t = names_both(recs, L)
            lines.append(f"{e.SHORT[model]:26s} {fw:11s} {'notice ' if nt else 'default'} | {w:5.0f} | {h}/{t} "
                         f"({100 * h / max(t, 1):.0f}%) | n logs {len(recs)}")
        if model in e.REF:
            d, stem = e.REF[model]
            recs = e.rows(d / f"B_split_{stem}.jsonl")
            if recs:
                w = sum(r["sum_words"] for r in recs) / sum(r["nchunks"] for r in recs)
                h, t = names_both(recs, L)
                lines.append(f"{e.SHORT[model]:26s} {'safety':11s} (published) | {w:5.0f} | {h}/{t} ({100 * h / max(t, 1):.0f}%)")
    txt = "\n".join(lines)
    print(txt)
    OUT.write_text(txt + "\n")


if __name__ == "__main__":
    main()
