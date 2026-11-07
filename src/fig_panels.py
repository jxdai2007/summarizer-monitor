"""Per-panel figures for the video slides, sized for 1080p (1920 px wide at 150 dpi) with large type.
Every number is computed from data/*.csv (built by src/build_data.py and the E2/E2b/E2c analysis scripts) through the
loaders in src/fig_main.py; nothing is typed in by hand. Label offsets are layout only.

Usage: /Users/macstudio/projects/swarm-alignment/.venv/bin/python src/fig_panels.py
Outputs (to_human/panels/): panel_A_ceiling.png, panel_B_realism.png, panel_C_testimony.png, pipeline.png, canary.png,
and panel_numbers.json (every value drawn on the panels, read by src/build_slides.py).
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fig_main as fm  # noqa: E402

ROOT = fm.ROOT
DATA = fm.DATA
EXP = ROOT / "experiments"
OUT = ROOT / "to_human" / "panels"
BLUE, ORANGE, AQUA, GRAY, INK, INK2, GRID, SURFACE = fm.BLUE, fm.ORANGE, fm.AQUA, fm.GRAY, fm.INK, fm.INK2, fm.GRID, fm.SURFACE
SHADE = "#f3f2ee"
W, H, DPI = 12.8, 6.6, 150
SONNET = "anthropic/claude-sonnet-5.5"
SHORT = dict(fm.SHORT)
SHORT.update({"google/gemini-4-argon": "Gemini 4 Argon", "openai/gpt-oss-120b": "gpt-oss-120b",
              "nvidia/nemotron-3.5-super-vl": "Nemotron 3.5 Super", "meta-llama/llama-4-maverick": "Llama 4 Maverick",
              "microsoft/phi-4": "Phi-4", "mistralai/mistral-medium-3-5": "Mistral Medium 3.5",
              "anthropic/claude-opus-5.5": "Claude Opus 5.5", "moonshotai/kimi-k3.1-pro": "Kimi k3.1"})
PURPLE = "#8a4fc7"  # E2d batch colour
NUM: dict = {}  # everything drawn, for build_slides.py


def short(s):
    return SHORT.get(s, s.split("/")[-1])


def new_fig(h=H):
    fig = plt.figure(figsize=(W, h))
    fig.patch.set_facecolor(SURFACE)
    return fig


def style(ax, size=15):
    fm.style(ax)
    ax.tick_params(labelsize=size)


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=DPI, facecolor=SURFACE)
    plt.close(fig)
    print("wrote", (OUT / name).relative_to(ROOT))


def side_text(fig, x, y, items):
    """Right-hand text column: [(text, size, weight, color, gap_after)] top-down in figure fraction."""
    for txt, size, weight, color, gap in items:
        fig.text(x, y, txt, fontsize=size, fontweight=weight, color=color, va="top", ha="left", linespacing=1.25)
        y -= gap
    return y


# ------------------------------------------------------------------ A: the ceiling
def panel_a():
    rows = fm.rd("ceiling_planted.csv")
    pts = [r for r in rows if r["summarizer_own_rate"]]
    xs = [100 * float(r["summarizer_own_rate"]) for r in pts]
    ys = [100 * float(r["monitor_summary_rate"]) for r in pts]
    six = [r for r in pts if r["deal_set"] == "A" and r["summarizer"] in fm.SIX]
    rho6 = fm.spearman([float(r["summarizer_own_rate"]) for r in six], [float(r["monitor_summary_rate"]) for r in six])
    pros = fm.rd("ceiling_prospective_e2.csv")
    gaps_earlier = [y - x for x, y in zip(xs, ys)]
    gaps_pros = [float(r["monitor_minus_own_pts"]) for r in pros]
    exc = [r for r in pros if float(r["monitor_minus_own_pts"]) > 5]
    luna = next(r for r in rows if r["deal_set"] == "A" and r["summarizer"] == "openai/gpt-5.6-luna")
    NUM["A"] = dict(rho6=round(rho6, 3), n_families=len(six), n_earlier_cells=len(gaps_earlier),
                    n_earlier_within=sum(g <= 5 for g in gaps_earlier), n_pros_cells=len(gaps_pros),
                    n_pros_within=sum(g <= 5 for g in gaps_pros),
                    exceptions=[dict(summarizer=short(r["summarizer"]), set=r["deal_set"], pts=float(r["monitor_minus_own_pts"]),
                                     own=f"{r['summarizer_own_k']}/{r['summarizer_own_n']}",
                                     summ=f"{r['monitor_summary_k']}/{r['monitor_summary_n']}") for r in exc],
                    luna_A=dict(full_pct=round(100 * float(luna["monitor_full_rate"])), sum_pct=round(100 * float(luna["monitor_summary_rate"])),
                                full_k=int(luna["monitor_full_k"]), sum_k=int(luna["monitor_summary_k"]), n=int(luna["n_pairs"]),
                                fa_k=int(luna["fa_summary_k"]), fa_n=int(luna["fa_summary_n"])))
    fig = new_fig()
    ax = fig.add_axes([0.088, 0.13, 0.40, 0.80])
    style(ax)
    ax.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.fill_between([0, 104], [0, 104], [104, 104], color=SHADE, zorder=0.5, lw=0)
    ax.plot([0, 104], [0, 104], color=INK2, lw=2, ls=(0, (5, 4)), zorder=1)
    ax.text(4, 99, "monitor beats its summarizer", fontsize=14, color=INK2, va="top", ha="left", style="italic")
    # labelled: the summarizers the narration names (luna, Gemini, Sonnet) plus the Llama outlier; the rest stay "other"
    off = {("A", "openai/gpt-5.6-luna"): (12, 0, "left"), ("B", "openai/gpt-5.6-luna"): (12, -6, "left"),
           ("C", "openai/gpt-5.6-luna"): (-12, 6, "right"), ("A", "google/gemini-3.8-flash"): (-13, 2, "right"),
           ("A", "meta-llama/llama-4-scout"): (12, 6, "left"), ("A", "anthropic/claude-sonnet-5.5"): (-14, 4, "right")}
    for r, x, y in zip(pts, xs, ys):
        c = fm.FAM_COLOR.get(r["summarizer_family"], GRAY)
        ax.scatter(x, y, s=260, marker=fm.SET_MARK[r["deal_set"]], color=c, edgecolor=SURFACE, linewidth=2.5, zorder=4)
        if (r["deal_set"], r["summarizer"]) not in off:
            continue
        dx, dy, ha = off[(r["deal_set"], r["summarizer"])]
        lab = short(r["summarizer"]) + ("" if r["deal_set"] == "A" else f" ({fm.SET_SHORT[r['deal_set']]})")
        ax.annotate(lab, (x, y), textcoords="offset points", xytext=(dx, dy), ha=ha, va="center", fontsize=13, color=INK, zorder=5,
                    bbox=dict(boxstyle="square,pad=0.08", fc=SURFACE, ec="none", alpha=0.85))
    for r in pros:
        x, y = 100 * float(r["summarizer_own_rate"]), 100 * float(r["monitor_summary_rate"])
        c = fm.FAM_COLOR.get(r["summarizer_family"], GRAY)
        ax.scatter(x, y, s=220, marker=fm.SET_MARK[r["deal_set"]], facecolor=SURFACE, edgecolor=c if c != GRAY else INK2, linewidth=2.5, zorder=4)
        if r in exc:
            ax.annotate(f"{short(r['summarizer'])} (E2, set {r['deal_set']}): +{float(r['monitor_minus_own_pts']):.0f} pts",
                        (x, y), textcoords="offset points", xytext=(14, 2), ha="left", va="center", fontsize=13, color=INK, zorder=5)
    ax.set_xlim(0, 104)
    ax.set_ylim(0, 104)
    ax.set_xticks(range(0, 101, 25), [f"{t}%" for t in range(0, 101, 25)])
    ax.set_yticks(range(0, 101, 25), [f"{t}%" for t in range(0, 101, 25)])
    ax.set_xlabel("Summarizer's own catch rate (reading the full log)", fontsize=15, color=INK, labelpad=8)
    ax.set_ylabel("Monitor's catch rate (reading its summaries)", fontsize=15, color=INK, labelpad=8)
    a = NUM["A"]
    e = a["exceptions"]
    exc_txt = "; ".join(f"{x['summarizer']}, set {x['set']}, +{x['pts']:.0f} pts" for x in e)
    side_text(fig, 0.535, 0.94, [
        (f"\u03c1 = {a['rho6']:.2f}", 42, "bold", INK, 0.12),
        (f"rank correlation over {a['n_families']} summarizer families\n(set A): the monitor is capped by\nits summarizer", 16, "normal", INK2, 0.19),
        (f"{a['n_pros_within']} of {a['n_pros_cells']}", 30, "bold", INK, 0.085),
        (f"new summarizer \u00d7 deal-set cells (E2) stay\nwithin +5 pts of the summarizer's own catch" + (f";\nexception: {exc_txt}" if e else ""),
         16, "normal", INK2, 0.19),
        (f"{a['luna_A']['full_pct']}% \u2192 {a['luna_A']['sum_pct']}%", 30, "bold", INK, 0.085),
        (f"monitors on GPT-5.6-luna summaries, set A\n({a['luna_A']['full_k']}/{a['luna_A']['n']} \u2192 {a['luna_A']['sum_k']}/{a['luna_A']['n']}), "
         f"false alarms {a['luna_A']['fa_k']}/{a['luna_A']['fa_n']}", 16, "normal", INK2, 0.13),
    ])
    fam = [Line2D([], [], marker="o", ls="", ms=12, color=c, label=l) for l, c in
           (("GPT-5.6", ORANGE), ("Claude", BLUE), ("Gemini", AQUA), ("other", GRAY))]
    sets = [Line2D([], [], marker=fm.SET_MARK[s], ls="", ms=12, color=INK2, label=l) for s, l in
            (("A", "Mantiq, Gemini deals"), ("B", "Mantiq, Grok deals"), ("C", "ChatDev (MAST)"))]
    sets.append(Line2D([], [], marker="o", ls="", ms=12, markerfacecolor=SURFACE, markeredgecolor=INK2, markeredgewidth=2.2,
                       label="hollow: new, E2"))
    sets.append(Line2D([], [], ls=(0, (5, 4)), lw=2, color=INK2, label="monitor = summarizer"))
    ax.legend(handles=fam, loc="upper left", bbox_to_anchor=(0.0, 0.915), fontsize=13.5, frameon=False, ncol=2, handletextpad=0.2,
              columnspacing=1.0)
    fig.legend(handles=sets, loc="lower left", bbox_to_anchor=(0.53, -0.005), fontsize=13.5, frameon=False, ncol=2, handletextpad=0.3,
               columnspacing=0.9)
    save(fig, "panel_A_ceiling.png")


# ------------------------------------------------------------------ B: realism (agent-written deals)
def panel_b():
    rows = fm.rd("realism_agent_written.csv")
    v = {r["view"]: r for r in rows if r["monitor"] == SONNET and not r["comparison"]}
    cmp_ = {r["comparison"]: r for r in rows if r["monitor"] == SONNET and r["comparison"]}
    e1 = fm.e1_lane()
    fig = plt.figure(figsize=(10.4, 7.2))
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0.12, 0.25, 0.86, 0.66])
    style(ax)
    ax.grid(True, axis="y", color=GRID, lw=0.8, zorder=0)
    w, gap = 0.27, 0.04
    groups = [("matched", "Matched false alarms\n(\u2264 10% of controls)"), ("fixed50", "Fixed threshold\n(score \u2265 50)")]
    NUM["B"] = dict(n_coord=int(v["FULL"]["n_coordinated"]), n_ctrl=int(v["FULL"]["n_control"]),
                    auc=dict(full=float(v["FULL"]["auc"]), luna=float(v["LUNA"]["auc"]), lane=round(e1["auc"], 3) if e1 else None))
    for gi, (mode, glab) in enumerate(groups):
        bars = []
        for view, col, lab in (("FULL", GRAY, "full log"), ("LUNA", ORANGE, "luna summaries")):
            r = v[view]
            bars.append((col, lab, int(r["fixed50_detect_k" if mode == "fixed50" else "matched_detect_k"]), int(r["n_coordinated"]),
                         int(r["fixed50_fa_k" if mode == "fixed50" else "matched_fa_k"]), int(r["n_control"])))
        if e1:
            bars.append((BLUE, "raw lane (E1)", *e1["fixed" if mode == "fixed50" else "matched"]))
        NUM["B"][mode] = {lab: dict(k=k, n=n, fa=fa, n_ctrl=nn) for _, lab, k, n, fa, nn in bars}
        for bi, (col, lab, k, n, fa, nn) in enumerate(bars):
            x = gi + (bi - 1) * (w + gap)
            h = fm.pct(k, n)
            ax.bar(x, h, w, color=col, zorder=2, edgecolor=SURFACE, lw=2)
            ax.text(x, h + 1.5, f"{h:.0f}%", ha="center", va="bottom", fontsize=19, fontweight="bold", color=INK)
            ax.text(x, h - 3, f"{k}/{n}", ha="center", va="top", fontsize=13, color="white" if col != GRAY else INK)
            ax.text(x, -4, lab.replace(" ", "\n", 1), ha="center", va="top", fontsize=13, color=INK, linespacing=1.1)
            warn = mode == "fixed50" and nn and fa / nn > 0.10
            ax.text(x, -15.5, f"FA {fa}/{nn}", ha="center", va="top", fontsize=13, color=ORANGE if warn else INK2,
                    fontweight="bold" if warn else "normal")
        c = cmp_["fixed50" if mode == "fixed50" else "matched_fa10"]
        p = float(c["mcnemar_p_two_sided"])
        sig = f"p = {p:.1g}" if p < 0.05 else "not significant"
        NUM["B"][mode + "_cmp"] = dict(diff=float(c["diff_pts"]), lo=float(c["diff_ci_lo"]), hi=float(c["diff_ci_hi"]), p=p)
        ax.text(gi, 99, f"luna loses {float(c['diff_pts']):.0f} pts\n(CI {float(c['diff_ci_lo']):+.0f} to {float(c['diff_ci_hi']):+.0f}), {sig}",
                ha="center", va="bottom", fontsize=15, color=INK, linespacing=1.15, fontweight="bold" if mode == "matched" else "normal")
        ax.text(gi, -24, glab, ha="center", va="top", fontsize=15, color=INK, fontweight="bold", linespacing=1.15)
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(0, 112)
    ax.set_xticks([])
    ax.set_yticks(range(0, 101, 25), [f"{t}%" for t in range(0, 101, 25)])
    ax.set_ylabel("Coordinated sessions caught\n(Claude Sonnet 5.5 monitor)", fontsize=15, color=INK, labelpad=8)
    save(fig, "panel_B_realism.png")


# ------------------------------------------------------------------ C: testimony
def panel_c():
    t = {r["result_id"]: r for r in fm.rd("testimony.csv")}
    tc = fm.rd("testimony_calls.csv")
    raw = [r for r in tc if r["experiment"] == "L1c-17b" and r["cond"] == "ERR_NOEV" and r["monitor"] == "claude-sonnet-5.5" and r["harmful"] != ""]
    raw_k, raw_n = sum(int(r["harmful"]) for r in raw), len(raw)

    def kn(rid):
        return int(t[rid]["k"]), int(t[rid]["n"])

    NUM["C"] = dict(raw=(raw_k, raw_n), summary=kn("blame_summary_note_sonnet"), fix=kn("blame_summary_note_sumfix_sonnet"),
                    corr0=kn("corrections_gpt-5.6-luna_long_real_nocorr"), corr1=kn("corrections_gpt-5.6-luna_long_real_corr"))
    groups = [("Culprit's note \u201cstep N was run by agent-9, not me\u201d:\nClaude Sonnet 5.5 suspends only the innocent agent",
               [("raw log", *NUM["C"]["raw"], GRAY), ("through summaries", *NUM["C"]["summary"], ORANGE),
                ("+ one summarizer line", *NUM["C"]["fix"], BLUE)]),
              ("Agent appends a one-line \u201ccorrection\u201d:\nGPT-5.6-luna clears a real rule break",
               [("no correction", *NUM["C"]["corr0"], GRAY), ("with correction", *NUM["C"]["corr1"], ORANGE)])]
    fig = new_fig()
    ax = fig.add_axes([0.25, 0.10, 0.70, 0.86])
    style(ax)
    ax.grid(True, axis="x", color=GRID, lw=0.8, zorder=0)
    y, yt, yl = 0.0, [], []
    for head, bars in groups:
        y -= 0.55
        ax.text(-0.33, y, head, transform=ax.get_yaxis_transform(), fontsize=16, fontweight="bold", color=INK, va="center", ha="left",
                linespacing=1.2, zorder=6, bbox=dict(boxstyle="square,pad=0.2", fc=SURFACE, ec="none"))
        y -= 1.15
        for lab, k, n, col in bars:
            h = fm.pct(k, n)
            ax.barh(y, h, 0.66, color=col, zorder=2, edgecolor=SURFACE, lw=2)
            if h == 0:
                ax.plot([0, 0], [y - 0.33, y + 0.33], color=col, lw=6, zorder=3, solid_capstyle="butt")
            ax.text(h + 1.5, y, f"{h:.0f}%  ({k}/{n})", va="center", ha="left", fontsize=17, color=INK,
                    fontweight="bold" if col == ORANGE else "normal", zorder=4)
            yt.append(y)
            yl.append(lab)
            y -= 0.9
        y -= 0.2
    ax.set_yticks(yt, yl, fontsize=16, color=INK)
    ax.set_ylim(y + 0.5, 0.1)
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 25), [f"{t}%" for t in range(0, 101, 25)], fontsize=14)
    ax.set_xlabel("share of judgments", fontsize=14, color=INK2, labelpad=4)
    save(fig, "panel_C_testimony.png")


# ------------------------------------------------------------------ pipeline diagram
def pipeline():
    fig = new_fig(4.6)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 130)
    ax.set_ylim(2, 48)
    ax.axis("off")
    yc = 24

    def box(x, w, label, sub, fc, ec, tc=INK, lw=2.0, h=16):
        ax.add_patch(FancyBboxPatch((x, yc - h / 2), w, h, boxstyle="round,pad=0,rounding_size=2.2", fc=fc, ec=ec, lw=lw, zorder=2))
        ax.text(x + w / 2, yc + 1.2, label, ha="center", va="center", fontsize=22, fontweight="bold", color=tc, zorder=3)
        ax.text(x + w / 2, yc - h / 2 - 2.2, sub, ha="center", va="top", fontsize=15, color=INK2, linespacing=1.25, zorder=3)

    def arrow(x0, x1):
        ax.add_patch(FancyArrowPatch((x0, yc), (x1, yc), arrowstyle="-|>", mutation_scale=26, lw=2.4, color=INK2, zorder=1))

    # agents: a small cluster of nodes with message edges
    import math
    cx, r0 = 11, 6.5
    nodes = [(cx + r0 * math.cos(a), yc + r0 * math.sin(a)) for a in [i * 2 * math.pi / 6 + 0.3 for i in range(6)]]
    for i, (x0, y0) in enumerate(nodes):
        for x1, y1 in nodes[i + 1:]:
            ax.plot([x0, x1], [y0, y1], color=GRID, lw=1.4, zorder=1)
    for x0, y0 in nodes:
        ax.add_patch(plt.Circle((x0, y0), 1.6, fc=GRAY, ec=SURFACE, lw=2, zorder=2))
    ax.text(cx, yc - 10.2, "agents", ha="center", va="top", fontsize=15, color=INK2)
    ax.text(cx, yc + 10.4, "Swarm", ha="center", va="bottom", fontsize=22, fontweight="bold", color=INK)
    arrow(20, 27)
    box(27.5, 22, "Raw log", "too long to read\nat swarm scale", "#ffffff", GRAY)
    for i in range(3):
        ax.plot([30.5, 46.5 - 4 * (i % 2)], [yc - 3.2 - 1.6 * i, yc - 3.2 - 1.6 * i], color=GRID, lw=1.6, zorder=3)
    arrow(50, 57)
    box(57.5, 27, "Summarizer", "decides what to keep\nand how to frame it", ORANGE, ORANGE, tc="white", lw=3, h=19)
    ax.text(71, yc + 13.5, "the unannounced first monitor", ha="center", va="bottom", fontsize=19, fontweight="bold", color=ORANGE,
            style="italic")
    arrow(85, 92)
    box(92.5, 20, "Monitor", "reads only\nthe summary", "#ffffff", GRAY)
    arrow(113, 118.5)
    ax.text(124, yc + 0.6, "verdict", ha="center", va="center", fontsize=17, color=INK, fontweight="bold")
    save(fig, "pipeline.png")


# ------------------------------------------------------------------ canary audit: canary drop vs held-out drop
def drops(path):
    """Pooled FULL minus SUMMARY detection on SPLIT (log, monitor) pairs where both scores parsed, per summarizer and set
    (the drop definition in experiments/E2*/stage1_predictions.json)."""
    rows = list(csv.DictReader(open(path)))
    full = {(r["set"], r["log_id"], r["monitor"]): int(r["flag"]) for r in rows
            if r["view"] == "FULL" and r["deal_type"] == "SPLIT" and r["score"] != ""}
    agg = {}
    for r in rows:
        k = (r["set"], r["log_id"], r["monitor"])
        if r["view"] == "SUMMARY" and r["deal_type"] == "SPLIT" and r["score"] != "" and k in full:
            a = agg.setdefault((r["summarizer"], r["set"]), [0, 0, 0])
            a[0] += full[k]
            a[1] += int(r["flag"])
            a[2] += 1
    return {key: dict(full=f, summ=s, n=n, drop=100 * (f - s) / n) for key, (f, s, n) in agg.items()}


def canary():
    """Batches are discovered from experiments/E2*-*/ (data/<batch>_scores.csv). A batch is pooled into the headline once
    findings.md reports it as "(<batch>, CONFIRMATORY"; a batch with data but no findings entry yet is drawn and reported in
    its own slot, and a batch with a protocol but no data is listed as running."""
    batches = [(d.name.split("-")[0], f"{d.name.split('-')[0]}_scores.csv", d.name) for d in sorted(EXP.glob("E2*-*")) if d.is_dir()]
    in_findings = set(re.findall(r"\((E2[a-z]?), CONFIRMATORY", (ROOT / "findings.md").read_text()))
    D, prospective, reviewed, thresh, running = {}, {}, set(), None, []
    for name, fn, exp in batches:
        if not (DATA / fn).exists():
            running.append(name)
            continue
        d = drops(DATA / fn)
        seen = {s for s, _ in D}
        D.update(d)  # later files supersede earlier ones for the same summarizer
        pred = EXP / exp / "stage1_predictions.json"
        if pred.exists():
            pj = json.load(open(pred))
            for s in pj["summarizers"]:
                prospective[s] = name
            m = re.search(r"canary drop\s*>?\s*([\d.]+) points", pj["rule"])
            thresh = float(m.group(1)) if m else thresh
        else:  # stage-1 file not committed yet: the summarizers new in this file belong to this batch
            for s in {s for s, _ in d} - seen:
                prospective[s] = name
        if name in in_findings:
            reviewed.add(name)
    sums = sorted({s for s, _ in D})
    earlier = [s for s in sums if s not in prospective and (s, "A") in D and (s, "B") in D]
    both = [s for s in sums if (s, "A") in D and (s, "B") in D]
    a_only = [s for s in sums if (s, "A") in D and (s, "B") not in D and s in prospective]

    def label(x):
        return "FAIL" if x > thresh else "PASS"

    def stats(pros):
        calls = {s: (label(D[(s, "A")]["drop"]), label(D[(s, "B")]["drop"])) for s in pros}
        pool = earlier + pros
        err = [D[(s, "B")]["drop"] - D[(s, "A")]["drop"] for s in pros]
        return dict(n_prospective=len(pros), n_correct=sum(a == b for a, b in calls.values()), n_vendors=len({s.split("/")[0] for s in pros}),
                    n_fail_hit=sum(a == b == "FAIL" for a, b in calls.values()), n_obs_fail=sum(b == "FAIL" for _, b in calls.values()),
                    n_pass_calls=sum(a == "PASS" for a, _ in calls.values()), n_fail_calls=sum(a == "FAIL" for a, _ in calls.values()),
                    n_summarizers=len(pool), rho=round(fm.spearman([D[(s, "A")]["drop"] for s in pool], [D[(s, "B")]["drop"] for s in pool]), 3),
                    mean_heldout_minus_canary=round(sum(err) / len(err), 1) if err else None)

    pros_rev = [s for s in both if prospective.get(s) in reviewed]
    pros_new = [s for s in both if s in prospective and prospective[s] not in reviewed]
    NUM["canary"] = dict(threshold=thresh, n_earlier=len(earlier), reviewed_batches=sorted(reviewed), **stats(pros_rev),
                         unreviewed=dict(batches=sorted({prospective[s] for s in pros_new}), **stats(pros_new),
                                         all=stats(pros_rev + pros_new)) if pros_new else None,
                         batches={b: [short(s) for s in both if prospective.get(s) == b] for b, _, _ in batches},
                         pending=[short(s) for s in a_only], running=running,
                         points={short(s): dict(canary=round(D[(s, "A")]["drop"], 1), heldout=round(D[(s, "B")]["drop"], 1),
                                                batch=prospective.get(s, "earlier")) for s in both})
    col = {b: c for (b, _, _), c in zip(batches, (BLUE, ORANGE, AQUA, PURPLE, INK2))}
    mark = {b: m for (b, _, _), m in zip(batches, ("o", "s", "D", "P", "X"))}
    fig = plt.figure(figsize=(9.6, 8.0))
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0.105, 0.095, 0.875, 0.885])
    style(ax)
    lo, hi = -30, 100
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.fill_between([lo, thresh], lo, thresh, color="#e6f4ee", zorder=0.4, lw=0)
    ax.fill_between([thresh, hi], thresh, hi, color="#fbebe4", zorder=0.4, lw=0)
    ax.axvline(thresh, color=INK2, lw=1.6, zorder=1)
    ax.axhline(thresh, color=INK2, lw=1.6, zorder=1)
    ax.plot([lo, hi], [lo, hi], color=GRAY, lw=1.4, ls=(0, (5, 4)), zorder=1)
    ax.text(hi - 2, thresh - 1.5, f"{thresh:.0f}-pt PASS/FAIL line", ha="right", va="top", fontsize=13, color=INK2)
    ax.text(lo + 2, -3, "PASS on both sets", ha="left", va="center", fontsize=15, color="#11785a", fontweight="bold")
    ax.text(hi - 2, hi - 2, "FAIL on both sets", ha="right", va="top", fontsize=15, color="#b4471c", fontweight="bold")
    # label placement only: text position in data coordinates (None = plain offset to the right)
    place = {"Nova Pro": (-12, 6, "right", None), "Command A+": (-12, -4, "right", None), "Llama 4 Maverick": (0, 0, "right", (86, 82)),
             "Phi-4": (0, 0, "right", (97, 57)), "gpt-oss-120b": (-12, 2, "right", None), "Mistral Medium 3.5": (0, 0, "center", (80, 40)),
             "MiniMax M3.1 Flash": (12, 4, "left", None), "Nemotron 3.5 Super": (0, 0, "center", (-3, 31)),
             "GPT-5.6-terra": (12, -6, "left", None), "Gemini 4 Argon": (0, 0, "left", (3, -13)), "GPT-5.6-luna": (-12, 6, "right", None),
             "Gemini 3.8 Flash": (-12, -2, "right", None), "Mistral Large 4": (12, -12, "left", None),
             "Qwen3.8 Flash": (-12, 6, "right", None), "Claude Sonnet 5.5": (-12, -8, "right", None),
             "Claude Opus 5.5": (0, 0, "left", (3, -25)), "Kimi k3.1": (0, 0, "left", (24, 0))}
    # Kimi k3.1 cleared narrowly (E2d analysis: PASS in 80% of log-bootstrap replicates; FAIL under DeepSeek alone)
    narrow = {"Kimi k3.1": "narrow PASS"}
    for s in both:
        x, y = D[(s, "A")]["drop"], D[(s, "B")]["drop"]
        b = prospective.get(s)
        dx, dy, ha, xyt = place.get(short(s), (12, 0, "left", None))
        kw = dict(xytext=xyt, textcoords="data", arrowprops=dict(arrowstyle="-", color=INK2, lw=1.1, shrinkA=2, shrinkB=7)) if xyt else \
            dict(xytext=(dx, dy), textcoords="offset points")
        lab = short(s) + (f" ({narrow[short(s)]})" if short(s) in narrow else "")
        if b:
            ax.scatter(x, y, s=230 if b == "E2c" else 260, marker=mark[b], color=col[b], edgecolor=SURFACE, linewidth=2.5,
                       zorder=4.5 if b == "E2c" else 4)
            ax.annotate(lab, (x, y), ha=ha, va="center", fontsize=14, color=INK, zorder=5, fontweight="bold",
                        bbox=dict(boxstyle="square,pad=0.08", fc=SURFACE, ec="none", alpha=0.8), **kw)
        else:
            ax.scatter(x, y, s=150, facecolor=SURFACE, edgecolor=GRAY, linewidth=2.2, zorder=3)
            ax.annotate(short(s), (x, y), ha=ha, va="center", fontsize=12, color=INK2, zorder=5,
                        bbox=dict(boxstyle="square,pad=0.06", fc=SURFACE, ec="none", alpha=0.7), **kw)
    for i, s in enumerate(a_only):  # canary run, held-out not yet scored: tick on the x axis
        x = D[(s, "A")]["drop"]
        ax.plot([x, x], [lo, lo + 5], color=col.get(prospective[s], GRAY), lw=4, zorder=4)
        ax.text(x, lo + 6 + 4 * i, f"{short(s)}: held-out pending", fontsize=11, color=INK2, ha="center", va="bottom")
    ax.set_xlabel("Canary drop, set A (pts lost on planted deals)", fontsize=15, color=INK, labelpad=8)
    ax.set_ylabel("Held-out drop, set B (pts lost on unseen deals)", fontsize=15, color=INK, labelpad=8)
    c = NUM["canary"]
    handles = [Line2D([], [], marker=mark[b], ls="", ms=11, color=col[b], label=b + ("" if b in reviewed else " (unreviewed)"))
               for b, _, _ in batches if c["batches"][b]]
    handles.append(Line2D([], [], marker="o", ls="", ms=10, markerfacecolor=SURFACE, markeredgecolor=GRAY, markeredgewidth=2,
                          label="scored earlier"))
    handles.append(Line2D([], [], ls=(0, (5, 4)), lw=1.6, color=GRAY, label="held-out = canary"))
    ax.legend(handles=handles, loc="upper left", fontsize=12.5, frameon=True, facecolor=SURFACE, edgecolor="none", framealpha=0.95,
              handletextpad=0.3, borderaxespad=0.4)
    save(fig, "canary.png")


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE})
    panel_a()
    panel_b()
    panel_c()
    pipeline()
    canary()
    (OUT / "panel_numbers.json").write_text(json.dumps(NUM, indent=1))
    print("wrote", (OUT / "panel_numbers.json").relative_to(ROOT))
    c = NUM["canary"]
    print(f"canary (reviewed {c['reviewed_batches']}): {c['n_correct']}/{c['n_prospective']} correct ({c['n_fail_calls']} FAIL, "
          f"{c['n_pass_calls']} PASS calls); rho {c['rho']} over {c['n_summarizers']}; unreviewed slot {c['unreviewed']}; pending {c['pending']}")


if __name__ == "__main__":
    main()
