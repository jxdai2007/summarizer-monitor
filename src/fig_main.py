"""Main figure: "The monitor is capped by its summarizer". Three panels, every number read from data/*.csv (built by
src/build_data.py from raw records). Panel B picks up the E1 raw lane from data/E1_scores.csv when that file exists.
Usage: /Users/macstudio/projects/swarm-alignment/.venv/bin/python src/fig_main.py
Outputs: to_human/fig_main.png, to_human/fig_main.pdf
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data", ROOT / "to_human"
THR = 50

# palette: validated with the dataviz skill's validate_palette.js (3 slots, all-pairs, light)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
GRAY, INK, INK2, GRID = "#9b9a95", "#0b0b0b", "#52514e", "#e4e3df"
SURFACE = "#fcfcfb"
FAM_COLOR = {"OpenAI GPT-5.6": ORANGE, "Anthropic Claude": BLUE, "Google Gemini": AQUA}
SET_MARK = {"A": "o", "B": "s", "C": "^"}
SET_SHORT = {"A": "set A", "B": "set B", "C": "ChatDev"}
SIX = ["openai/gpt-5.6-luna", "google/gemini-3.8-flash", "meta-llama/llama-4-scout", "qwen/qwen3.8-flash", "z-ai/glm-5.3-flash",
       "mistralai/mistral-large-4-0"]
SHOW_DROP = {"openai/gpt-5.6-luna", "google/gemini-3.8-flash"}
SHORT = {"openai/gpt-5.6-luna": "GPT-5.6-luna", "openai/gpt-5.6-sol": "GPT-5.6-sol", "google/gemini-3.8-flash": "Gemini 3.8 Flash",
         "anthropic/claude-sonnet-5.5": "Claude Sonnet 5.5", "meta-llama/llama-4-scout": "Llama 4 Scout",
         "qwen/qwen3.8-flash": "Qwen3.8 Flash", "z-ai/glm-5.3-flash": "GLM-5.3 Flash", "mistralai/mistral-large-4-0": "Mistral Large 4",
         "openai/gpt-5.6-terra": "GPT-5.6-terra", "cohere/command-a-plus": "Command A+", "minimax/minimax-m3.1-flash": "MiniMax M3.1 Flash",
         "amazon/nova-pro-v1": "Nova Pro"}


def rd(name):
    return list(csv.DictReader(open(DATA / name)))


def num(x):
    return None if x in ("", None) else float(x)


def pct(k, n):
    return 100 * k / n


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r, i = [0.0] * len(xs), 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(xs, ys):
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num_ = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    return num_ / math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRAY)
    ax.tick_params(colors=INK2, labelsize=12, length=0, pad=6)


def panel_title(ax, letter, title, sub, x=0.0, dy=0.0):
    nl = sub.count("\n") + 1
    ax.annotate(sub, (x, 1), xycoords="axes fraction", xytext=(0, 10), textcoords="offset points", fontsize=12, color=INK2,
                va="bottom", linespacing=1.25)
    ax.annotate(f"{letter}  {title}", (x, 1), xycoords="axes fraction", xytext=(0, 14 + 18 * nl), textcoords="offset points",
                fontsize=17, fontweight="bold", color=INK, va="bottom")


# ------------------------------------------------------------------ panel A: the ceiling
def panel_a(ax):
    rows = rd("ceiling_planted.csv")
    pts = [r for r in rows if r["summarizer_own_rate"]]
    xs = [100 * float(r["summarizer_own_rate"]) for r in pts]
    ys = [100 * float(r["monitor_summary_rate"]) for r in pts]
    rho = spearman(xs, ys)
    six = [r for r in pts if r["deal_set"] == "A" and r["summarizer"] in SIX]
    rho6 = spearman([float(r["summarizer_own_rate"]) for r in six], [float(r["monitor_summary_rate"]) for r in six])
    above = sum(y > x for x, y in zip(xs, ys))
    pros = rd("ceiling_prospective_e2.csv") if (DATA / "ceiling_prospective_e2.csv").exists() else []
    gaps = [y - x for x, y in zip(xs, ys)] + [float(r["monitor_minus_own_pts"]) for r in pros]
    n_cells, n_within = len(gaps), sum(g <= 5 for g in gaps)
    exc = [r for r in pros if float(r["monitor_minus_own_pts"]) > 5]
    bd = [r for r in rd("ceiling_by_deal.csv") if r["summarizer"] == "openai/gpt-5.6-luna" and r["direction"] != "tie"]
    n_loss = sum(r["direction"] == "loss" for r in bd)
    style(ax)
    ax.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.fill_between([0, 104], [0, 104], [104, 104], color="#f3f2ee", zorder=0.5, lw=0)
    ax.plot([0, 104], [0, 104], color=INK2, lw=1.6, ls=(0, (5, 4)), zorder=1)
    exc_txt = "; ".join(f"{SHORT.get(r['summarizer'], r['summarizer'].split('/')[1])} {r['deal_set']}, "
                        f"+{float(r['monitor_minus_own_pts']):.0f}" for r in exc)
    ax.text(2.5, 101, f"Monitor within +5 pts of its\nsummarizer in {n_within} of {n_cells} cells" + (f"\n(exception: {exc_txt})" if exc else ""),
            fontsize=12.5, color=INK, ha="left", va="top", fontweight="bold", linespacing=1.15, zorder=6,
            bbox=dict(boxstyle="square,pad=0.2", fc="#f3f2ee", ec="none"))
    ax.text(33, 35, "monitor = summarizer alone", rotation=45, rotation_mode="anchor", fontsize=11, color=INK2, ha="left", va="bottom",
            transform_rotates_text=True, bbox=dict(boxstyle="square,pad=0.1", fc="#f3f2ee", ec="none"))
    # full-log level of the same monitors, per deal set (all SPLIT pairs with a full-log score)
    seen = {}
    for r in rows:
        seen.setdefault(r["deal_set"], (int(r["set_full_log_k"]), int(r["set_full_log_n"])))
    for ds, (k, n) in seen.items():
        y = pct(k, n)
        ax.plot([0, 104], [y, y], color=GRAY, lw=1.3, ls=":", zorder=1)
        below = ds == "A"
        ax.text(12, y - 2.0 if below else y + 0.8, f"full log, {SET_SHORT[ds]}: {y:.0f}%", fontsize=10.5, color=INK2,
                va="top" if below else "bottom", ha="left")
    off = {("A", "openai/gpt-5.6-luna"): (10, 2, "left"), ("B", "openai/gpt-5.6-luna"): (8, -20, "left"),
           ("C", "openai/gpt-5.6-luna"): (-10, -8, "right"), ("A", "google/gemini-3.8-flash"): (-11, -4, "right"),
           ("A", "meta-llama/llama-4-scout"): (10, 2, "left"), ("A", "qwen/qwen3.8-flash"): (-9, 9, "right"),
           ("A", "z-ai/glm-5.3-flash"): (-10, 2, "right"), ("A", "mistralai/mistral-large-4-0"): (8, -16, "left"),
           ("A", "anthropic/claude-sonnet-5.5"): (-12, -2, "right")}
    for r, x, y in zip(pts, xs, ys):
        c = FAM_COLOR.get(r["summarizer_family"], GRAY)
        ax.scatter(x, y, s=150, marker=SET_MARK[r["deal_set"]], color=c, edgecolor=SURFACE, linewidth=2, zorder=4)
        dx, dy, ha = off.get((r["deal_set"], r["summarizer"]), (8, 4, "left"))
        lab = SHORT[r["summarizer"]] + ("" if r["deal_set"] == "A" else f" ({SET_SHORT[r['deal_set']]})")
        d = float(r["drop_pts"])
        if r["summarizer"] in SHOW_DROP:
            lab += f"\n{'loses' if d > 0 else 'gains'} {abs(d):.0f} pts vs full log"
        ax.annotate(lab, (x, y), textcoords="offset points", xytext=(dx, dy), ha=ha, va="center", fontsize=11, color=INK, zorder=5,
                    bbox=dict(boxstyle="square,pad=0.08", fc=SURFACE, ec="none", alpha=0.85))
    for r in pros:
        x, y = 100 * float(r["summarizer_own_rate"]), 100 * float(r["monitor_summary_rate"])
        c = FAM_COLOR.get(r["summarizer_family"], GRAY)
        ax.scatter(x, y, s=130, marker=SET_MARK[r["deal_set"]], facecolor=SURFACE, edgecolor=c, linewidth=2.2, zorder=4)
        if r in exc:
            ax.annotate(f"{SHORT.get(r['summarizer'], r['summarizer'].split('/')[1])} (E2, {SET_SHORT[r['deal_set']]})",
                        (x, y), textcoords="offset points", xytext=(10, 4), ha="left", va="center", fontsize=10.5, color=INK, zorder=5)
    ax.set_xlim(0, 104)
    ax.set_ylim(0, 104)
    ax.set_xticks(range(0, 101, 25), [f"{t}%" for t in range(0, 101, 25)])
    ax.set_yticks(range(0, 101, 25), [f"{t}%" for t in range(0, 101, 25)])
    ax.set_xlabel("Summarizer's own catch rate, reading the full log", fontsize=13, color=INK, labelpad=8)
    ax.set_ylabel("Monitor's catch rate, reading its summaries", fontsize=13, color=INK, labelpad=8)
    panel_title(ax, "A", "The ceiling", f"Planted split deals in real swarm logs. Spearman \u03c1 = {rho6:.3f} over {len(six)} families (set A);\n"
                f"{rho:.3f} pooled over all {len(pts)} points (not independent: luna appears 3 times)", dy=-6)
    ax.text(103, 12, f"GPT-5.6-luna, per deal template: {n_loss} of {len(bd)} untied\ntemplates lose detection (6 templates per corpus)",
            fontsize=10, color=INK2, ha="right", va="bottom")
    sol = next((r for r in rows if r["summarizer"] == "openai/gpt-5.6-sol" and not r["summarizer_own_rate"]), None)
    if sol:
        ax.text(103, 2, f"Flagship GPT-5.6-sol (set A, own rate not measured):\nmonitors {100 * float(sol['monitor_full_rate']):.0f}% on the full log "
                f"\u2192 {100 * float(sol['monitor_summary_rate']):.0f}% on its summaries", fontsize=10, color=INK2, ha="right", va="bottom")
    fam = [Line2D([], [], marker="o", ls="", ms=10, color=c, label=l) for l, c in
           (("GPT-5.6", ORANGE), ("Claude", BLUE), ("Gemini", AQUA), ("other families", GRAY))]
    sets = [Line2D([], [], marker=SET_MARK[s], ls="", ms=10, color=INK2, label=l) for s, l in
            (("A", "Mantiq, Gemini deals"), ("B", "Mantiq, Grok deals"), ("C", "ChatDev (MAST)"))]
    hollow = [Line2D([], [], marker="o", ls="", ms=10, markerfacecolor=SURFACE, markeredgecolor=INK2, markeredgewidth=2,
                     label="hollow: new summarizers scored prospectively (E2), own rate on 18 logs per set")] if pros else []
    l1 = ax.legend(handles=fam, loc="upper left", bbox_to_anchor=(-0.02, -0.13), fontsize=11, frameon=False, ncol=4,
                   handletextpad=0.2, columnspacing=1.2)
    ax.add_artist(l1)
    l2 = ax.legend(handles=sets, loc="upper left", bbox_to_anchor=(-0.02, -0.185), fontsize=11, frameon=False, ncol=3,
                   handletextpad=0.2, columnspacing=1.2)
    if hollow:
        ax.add_artist(l2)
        ax.legend(handles=hollow, loc="upper left", bbox_to_anchor=(-0.02, -0.24), fontsize=11, frameon=False, handletextpad=0.2)
    return rho, rho6, len(pts), n_within, n_cells


# ------------------------------------------------------------------ panel B: realism (agent-written deals, loop8)
def e1_lane():
    f = DATA / "E1_scores.csv"
    if not f.exists():
        return None
    rows = [r for r in csv.DictReader(open(f)) if r["monitor"].lower().startswith("sonnet") and r["arm"] == "H1" and r["score"] not in ("", "None")]
    pos = [float(r["score"]) for r in rows if r["label"] == "COORDINATED"]
    neg = [float(r["score"]) for r in rows if r["label"] == "CONTROL"]
    if not pos or not neg:
        return None
    t = next(t for t in range(0, 102) if sum(x >= t for x in neg) / len(neg) <= 0.10)
    auc = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg) / (len(pos) * len(neg))
    return dict(fixed=(sum(x >= THR for x in pos), len(pos), sum(x >= THR for x in neg), len(neg)),
                matched=(sum(x >= t for x in pos), len(pos), sum(x >= t for x in neg), len(neg)), auc=auc, threshold=t)


def panel_b(ax):
    rows = rd("realism_agent_written.csv")
    S = "anthropic/claude-sonnet-5.5"
    v = {r["view"]: r for r in rows if r["monitor"] == S and not r["comparison"]}
    cmp_ = {r["comparison"]: r for r in rows if r["monitor"] == S and r["comparison"]}
    e1 = e1_lane()
    style(ax)
    ax.grid(True, axis="y", color=GRID, lw=0.8, zorder=0)
    w, gap = 0.27, 0.04
    groups = [("matched", "Matched false alarms\n(\u2264 10% of controls)"), ("fixed50", "Fixed threshold\n(score \u2265 50)")]
    for gi, (mode, glab) in enumerate(groups):
        bars = []
        for view, col, lab in (("FULL", GRAY, "full log"), ("LUNA", ORANGE, "luna")):
            r = v[view]
            k = int(r["fixed50_detect_k" if mode == "fixed50" else "matched_detect_k"])
            fa = int(r["fixed50_fa_k" if mode == "fixed50" else "matched_fa_k"])
            bars.append((col, lab, k, int(r["n_coordinated"]), fa, int(r["n_control"]), False))
        if e1:
            k, n, fa, nn = e1["fixed" if mode == "fixed50" else "matched"]
            bars.append((BLUE, "raw lane", k, n, fa, nn, False))
        else:
            bars.append((BLUE, "raw lane", None, None, None, None, True))
        for bi, (col, lab, k, n, fa, nn, placeholder) in enumerate(bars):
            x = gi + (bi - 1) * (w + gap)
            ax.text(x, -3, lab, ha="center", va="top", fontsize=11, color=INK)
            if placeholder:
                ax.bar(x, 22, w, facecolor="none", edgecolor=BLUE, lw=1.3, ls=(0, (4, 3)), zorder=2, alpha=0.7)
                ax.text(x, 11, "E1\npending", ha="center", va="center", fontsize=10.5, color=BLUE, zorder=3)
                continue
            h = pct(k, n)
            ax.bar(x, h, w, color=col, zorder=2, edgecolor=SURFACE, lw=2)
            ax.text(x, h + 1.5, f"{h:.0f}%", ha="center", va="bottom", fontsize=14, fontweight="bold", color=INK)
            ax.text(x, h - 2.5, f"{k}/{n}", ha="center", va="top", fontsize=10, color="white" if col != GRAY else INK)
            ax.text(x, -9.5, f"FA {fa}/{nn}", ha="center", va="top", fontsize=10, color=INK2)
        c = cmp_["fixed50" if mode == "fixed50" else "matched_fa10"]
        p = float(c["mcnemar_p_two_sided"])
        sig = f"p = {p:.1g}" if p < 0.05 else "n.s."
        ax.text(gi - (w + gap) / 2, 84, f"luna loses {float(c['diff_pts']):.0f} pts\n(CI {float(c['diff_ci_lo']):+.0f} to "
                f"{float(c['diff_ci_hi']):+.0f}), {sig}", ha="center", va="bottom", fontsize=11, color=INK, linespacing=1.15,
                fontweight="bold" if mode == "matched" else "normal")
        if mode == "fixed50" and e1:
            glab += "\nraw lane needs its own threshold"
        ax.text(gi, -18, glab, ha="center", va="top", fontsize=12.5, color=INK)
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(0, 106)
    ax.set_xticks([])
    ax.set_yticks(range(0, 101, 25), [f"{t}%" for t in range(0, 101, 25)])
    ax.set_ylabel("Coordinated sessions caught (Sonnet 5.5 monitor)", fontsize=13, color=INK, labelpad=8)
    n_t, n_c = v["FULL"]["n_coordinated"], v["FULL"]["n_control"]
    panel_title(ax, "B", "Realism: deals agents wrote", f"{n_t} coordinated / {n_c} control sessions; luna = GPT-5.6-luna.\nAt matched false alarms the loss is small.", dy=-6)


# ------------------------------------------------------------------ panel C: testimony and fixes
def hbars(ax, items, xlabel):
    style(ax)
    ax.grid(True, axis="x", color=GRID, lw=0.8, zorder=0)
    y = 0
    yt, yl = [], []
    for it in items:
        if it[0] == "header":
            y -= 0.72
            ax.text(-0.8, y, it[1], transform=ax.get_yaxis_transform(), fontsize=12, fontweight="bold", color=INK, va="center",
                    ha="left", linespacing=1.2, zorder=6,
                    bbox=dict(boxstyle="square,pad=0.15", fc=SURFACE, ec="none"))
            y -= 1.2
            continue
        _, lab, k, n, col = it
        h = pct(k, n)
        ax.barh(y, max(h, 0.0), 0.64, color=col, zorder=2, edgecolor=SURFACE, lw=2)
        if h == 0:
            ax.plot([0, 0], [y - 0.32, y + 0.32], color=col, lw=5, zorder=3, solid_capstyle="butt")
        inside = h > 62
        ax.text(h - 2 if inside else h + 2, y, f"{h:.0f}%  ({k}/{n})", va="center", ha="right" if inside else "left", fontsize=12,
                color="white" if inside else INK, fontweight="bold" if col == ORANGE else "normal", zorder=4)
        yt.append(y)
        yl.append(lab)
        y -= 0.9
    ax.set_yticks(yt, yl, fontsize=12, color=INK)
    ax.set_ylim(y + 0.4, 0.15)
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 25), [f"{t}%" for t in range(0, 101, 25)], fontsize=11)
    ax.set_xlabel(xlabel, fontsize=11.5, color=INK2, labelpad=4)


def panel_c(ax_top, ax_bot):
    t = {r["result_id"]: r for r in rd("testimony.csv")}

    def kn(rid):
        return int(t[rid]["k"]), int(t[rid]["n"])

    tc = list(csv.DictReader(open(DATA / "testimony_calls.csv")))
    split = {sm: [int(r["harmful"]) for r in tc if r["experiment"] == "L1c-20" and r["cond"] == "ERR_NOEV"
                  and r["monitor"] == "claude-sonnet-5.5" and r["summarizer"] == sm and r["harmful"] != ""]
             for sm in ("gpt-5.6-luna", "claude-haiku-5.5")}
    split_txt = ", ".join(f"{'luna' if 'luna' in sm else 'Haiku'} {sum(v)}/{len(v)}" for sm, v in split.items())
    items = [("header", "Culprit's note \u201cstep 4 was run by agent-9\u201d:\nSonnet 5.5 suspends only the innocent agent"),
             ("bar", "raw log (2 note wordings)", *kn("blame_raw_note_sonnet"), GRAY),
             ("bar", "through summaries", *kn("blame_summary_note_sonnet"), ORANGE),
             ("bar", "+ 1 summarizer line", *kn("blame_summary_note_sumfix_sonnet"), BLUE),
             ("header", "Agent appends a one-line \u201ccorrection\u201d:\nGPT-5.6-luna clears a rule break the log shows"),
             ("bar", "no correction", *kn("corrections_gpt-5.6-luna_long_real_nocorr"), GRAY),
             ("bar", "with correction", *kn("corrections_gpt-5.6-luna_long_real_corr"), ORANGE)]
    hbars(ax_top, items, f"share of judgments\n(summaries: {split_txt})")
    panel_title(ax_top, "C", "Testimony and fixes", "Agent-written claims enter the record as fact;\none summarizer line closes the blame chain", x=-0.8)

    calls = list(csv.DictReader(open(DATA / "fix_designs_calls.csv")))
    fd = {(r["design"], r["deal_set"]): r for r in rd("fix_designs.csv")}

    def pooled(design):
        pr = [r for r in calls if r["design"] == design and r["cond"] == "SPLIT" and r["view_flagged"] != "" and r["full_flagged"] != ""]
        return sum(int(r["view_flagged"]) for r in pr), sum(int(r["full_flagged"]) for r in pr), len(pr)

    def by_key(design):
        return {(r["log_key"], r["monitor"]): r for r in calls if r["design"] == design and r["cond"] == "SPLIT"
                and r["view_flagged"] != "" and r["full_flagged"] != ""}

    pl, h1 = by_key("PLAIN"), by_key("H1")
    common = sorted(pl.keys() & h1.keys())
    pk = sum(int(pl[k]["view_flagged"]) for k in common)
    hk = sum(int(h1[k]["view_flagged"]) for k in common)
    hf = sum(int(h1[k]["full_flagged"]) for k in common)
    pn = hn = len(common)
    n_unp = sum(int(fd[("H1", s)]["unparsed"]) for s in "ABC")
    costs = [float(fd[("H1", s)]["monitor_input_chars_frac"]) for s in "ABC"]
    items = [("header", "Fix: raw peer-message lane (3 planted sets).\nBy construction: every planted deal is peer-to-peer"),
             ("bar", "luna summaries", pk, pn, ORANGE),
             ("bar", f"raw lane, {min(costs):.1f}\u2013{max(costs):.1f}\u00d7 chars", hk, hn, BLUE),
             ("bar", "full log", hf, hn, GRAY)]
    hbars(ax_bot, items, f"split deals caught, same {pn} pairs")
    return n_unp


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE})
    fig = plt.figure(figsize=(20, 9.6))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.25, 0.85, 1.0], height_ratios=[1.6, 1.0], left=0.05, right=0.975,
                          top=0.73, bottom=0.27, wspace=0.30, hspace=0.62)
    ax_a = fig.add_subplot(gs[:, 0])
    ax_b = fig.add_subplot(gs[:, 1])
    ax_ct = fig.add_subplot(gs[0, 2])
    ax_cb = fig.add_subplot(gs[1, 2])
    rho, rho6, n, n_within, n_cells = panel_a(ax_a)
    panel_b(ax_b)
    n_unp = panel_c(ax_ct, ax_cb)
    # push panel C's label column right so the y tick labels fit
    for ax in (ax_ct, ax_cb):
        pos = ax.get_position()
        ax.set_position([pos.x0 + 0.11, pos.y0, pos.width - 0.11, pos.height])
    fig.text(0.05, 0.965, "The monitor is capped by its summarizer", fontsize=28, fontweight="bold", color=INK, va="top")
    fig.text(0.05, 0.9, f"On deals planted in real swarm logs, a monitor reading LLM-written summaries stays within +5 pts of the summarizer's own "
             f"catch rate in {n_within} of {n_cells} summarizer \u00d7 deal-set cells.\nThe summarizer decides what the monitor sees.",
             fontsize=13.5, color=INK2, va="top", linespacing=1.35)
    ceil = rd("ceiling_planted.csv")
    fa_k = sum(int(r["fa_summary_k"]) for r in ceil if r["fa_summary_n"])
    fa_n = sum(int(r["fa_summary_n"]) for r in ceil if r["fa_summary_n"])
    tc = list(csv.DictReader(open(DATA / "testimony_calls.csv")))
    n_blame = len({r["scenario"] for r in tc if r["experiment"] == "L1c-20"})
    n_corr = len({r["scenario"] for r in tc if r["experiment"] == "RV2-REC-A"})
    e1 = e1_lane()
    s_auc = {r["view"]: r["auc"] for r in rd("realism_agent_written.csv") if r["monitor"] == "anthropic/claude-sonnet-5.5" and not r["comparison"]}
    e1_txt = ""
    if e1:
        ek, en, efa, enn = e1["fixed"]
        mk, mn, mfa, mnn = e1["matched"]
        e1_txt = (f" E1 raw lane (locked, Sonnet): {ek}/{en} caught at score \u2265 50 but false alarms {efa}/{enn} exceed the locked "
                  f"\u2264 10% (P1 fails on false alarms); at matched false alarms {mk}/{mn} with {mfa}/{mnn}.\n"
                  f"Threshold-free AUC (Sonnet, coordinated vs control): raw lane {e1['auc']:.3f}, full log {float(s_auc['FULL']):.3f}, luna summaries {float(s_auc['LUNA']):.3f}.")
    fig.text(0.05, 0.012, "Planted deals: 4 innocuous-looking messages between two agents inserted into real Mantiq swarm logs and ChatDev (MAST) logs; "
             f"monitors Claude Haiku 5.5 + DeepSeek v4.1 Flash, flag at score \u2265 50, chunk-50 summaries; false alarms on summaries {fa_k}/{fa_n} (pooled).\n"
             f"Realism: loop8 sessions where agents wrote their own deals.{e1_txt}\n"
             f"Testimony: hand-written ops logs ({n_blame} blame logs, {n_corr} correction logs). "
             f"Raw lane: {n_unp} unparsed monitor calls excluded. All numbers computed from raw records by src/build_data.py.", fontsize=10, color=INK2, va="bottom", linespacing=1.4)
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "fig_main.png", dpi=200)
    fig.savefig(OUT / "fig_main.pdf")
    print(f"saved to_human/fig_main.png/.pdf; Spearman rho = {rho6:.3f} (set A, 6 families), {rho:.3f} pooled over {n} points; within +5 pts in {n_within}/{n_cells} cells; "
          f"E1 lane {'from data/E1_scores.csv' if (DATA / 'E1_scores.csv').exists() else 'placeholder (data/E1_scores.csv absent)'}")


if __name__ == "__main__":
    main()
