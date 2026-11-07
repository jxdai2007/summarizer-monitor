#!/usr/bin/env python3
"""Gate checks for the 2026-11-07 strengthening pass (GATES.md). Usage: python3 check_gates.py <gate>.
Each gate prints its success token only after every assertion passes; otherwise it prints the failure and exits 1."""
import re
import subprocess
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
TEX = (PAPER / "main.tex").read_text()
BODY = TEX.split("\\begin{abstract}", 1)[1].split("\\appendix", 1)[0]
MAIN = BODY.split("\\section{Conclusion}", 1)[0]  # abstract .. discussion
ABS = TEX.split("\\begin{abstract}", 1)[1].split("\\end{abstract}", 1)[0]
HEDGE = re.compile(r"post hoc|narrow|borderline|n\.s\.|not significant|deviation|swapped out|after the external review", re.I)


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def abstract():
    words = len(re.sub(r"\\[A-Za-z]+|[{}$\\]", " ", ABS).split())
    if not 150 <= words <= 215:
        fail(f"abstract has {words} words (want 150-215)")
    if "raw log" not in ABS or "mutation" not in ABS.lower():
        fail("abstract lacks the dial framing ('raw log') or the mutation-testing framing")
    print(f"ABSTRACT_OK words={words}")


def reframe():
    intro = TEX.split("\\section{Introduction}", 1)[1].split("\\section{Related work}", 1)[0]
    first = intro.split("\n\n", 1)[0]
    if not re.search(r"dial", first, re.I) or "raw log" not in first:
        fail("intro paragraph 1 lacks the dial framing")
    title = TEX.split("\\title{", 1)[1].split("\\thanks", 1)[0]
    if "Raw" not in title and "raw" not in title:
        fail("title subtitle does not carry the dial framing")
    print("REFRAME_OK")


def mutation():
    vs = (ROOT / "to_human" / "video_script.md").read_text().lower()
    if "mutation testing" not in TEX.lower() or "mutation testing" not in vs:
        fail("'mutation testing' missing from paper or video script")
    print("MUTATION_OK")


def calib():
    nums = (PAPER / "numbers.tex").read_text()
    keys = re.findall(r"\{(E3-[a-z0-9-]+)\}", nums)
    used = re.findall(r"\\N\{(E3-[a-z0-9-]+)\}", TEX)
    if len(set(keys)) < 6 or not used or not set(used) <= set(keys):
        fail(f"E3 macros: {len(set(keys))} generated, {len(set(used))} used, missing {set(used) - set(keys)}")
    print(f"CALIB_OK generated={len(set(keys))} used={len(set(used))}")


def caveats():
    n = len(HEDGE.findall(MAIN))
    if n > 7:
        fail(f"{n} hedge terms in abstract..discussion (want <= 7)")
    if "\\section{Deviations and post-hoc analyses}" not in TEX:
        fail("appendix lacks the Deviations section")
    for s in ("swapped out", "after the external review", "control design was switched"):
        if s in MAIN:
            fail(f"deviation narrative still in main text: {s}")
    print(f"CAVEAT_OK hedges={n}")


def build():
    r = subprocess.run(["tectonic", "-X", "compile", "main.tex"], cwd=PAPER, capture_output=True, text=True)
    if r.returncode != 0:
        fail("tectonic failed: " + r.stderr[-400:])
    log = (r.stdout + r.stderr)
    if re.search(r"undefined (control sequence|references)|Reference .* undefined", log, re.I):
        fail("undefined references or control sequences in build log")
    defined = set(re.findall(r"\\numdef\{([A-Za-z0-9-]+)\}", (PAPER / "numbers.tex").read_text()))
    used = set(re.findall(r"\\N\{([A-Za-z0-9-]+)\}", TEX + (PAPER / "tables.tex").read_text()))
    if used - defined:
        fail(f"undefined number macros (would render as red ??): {sorted(used - defined)[:8]}")
    out = subprocess.run(["mdls", "-raw", "-name", "kMDItemNumberOfPages", "main.pdf"], cwd=PAPER, capture_output=True,
                         text=True).stdout.strip()
    if not out.isdigit():
        d = (PAPER / "main.pdf").read_bytes()
        out = str(max([int(x) for x in re.findall(rb"/Count (\d+)", d)] or [0]))
    print(f"BUILD_OK pages={out}")


def e3():
    p = ROOT / "experiments" / "E3-canary-agent-written" / "results" / "analysis.txt"
    if not p.exists():
        fail("E3 analysis.txt missing")
    m = re.search(r"E3 VERDICT: (PASS|MIXED|KILL)", p.read_text())
    if not m:
        fail("E3 verdict line missing")
    if f"E3" not in TEX:
        fail("E3 not reported in the paper")
    print(f"E3_OK verdict={m.group(1)}")


def video():
    vs = (ROOT / "to_human" / "video_script.md").read_text()
    hook = vs.split("## Beat 1", 1)[1].split("## Beat 2", 1)[0]
    if "raw log" not in hook.lower():
        fail("video hook lacks the dial framing")
    narr = " ".join(l.lstrip("> ") for l in vs.splitlines() if l.startswith(">"))
    narr = re.sub(r"\{\{.*?\}\}", "", narr)
    w = len(narr.split())
    if w > 430:
        fail(f"narration {w} words (> 430)")
    print(f"VIDEO_OK narration_words={w}")


{"abstract": abstract, "reframe": reframe, "mutation": mutation, "calib": calib, "caveats": caveats, "build": build,
 "e3": e3, "video": video}[sys.argv[1]]()
