"""The dial figure: held-out detection loss (full log minus summaries) for every summarizer on the same set-B deals, same
monitors, with its deal-clustered CI; marker shape = canary call. Data are parsed from paper/tables.tex (TabCanary), which
make_numbers.py generates from the records. Usage (from summarizer-monitor/):
  /Users/macstudio/projects/swarm-alignment/.venv/bin/python src/fig_dial.py
Outputs: to_human/fig_dial.png, paper/fig_dial.pdf
"""
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
PASS_C, FAIL_C = "#2a78d6", "#eb6834"  # validated pair (dataviz palette slots 1-2)


def num(s):
    s = s.replace("\\ensuremath{-}", "-").strip()
    return float(s)


def rows():
    tab = (ROOT / "paper/tables.tex").read_text().split("\\newcommand{\\TabCanary}", 1)[1].split("\\newcommand", 1)[0]
    out = []
    for line in tab.splitlines():
        m = re.match(r"(.+?) & (.+?) & ([^&]+) & (PASS|FAIL) & ([^\[&]+)\[([^,]+), ([^\]]+)\] & (PASS|FAIL)", line)
        if m:
            out.append(dict(name=m.group(1).strip(), src=m.group(2).strip(), canary=num(m.group(3)), call=m.group(4),
                            held=num(m.group(5)), lo=num(m.group(6)), hi=num(m.group(7)), obs=m.group(8)))
    return out


def main():
    R = sorted(rows(), key=lambda r: r["held"])
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, ax = plt.subplots(figsize=(9.5, 7.2), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for i, r in enumerate(R):
        c = PASS_C if r["call"] == "PASS" else FAIL_C
        ax.plot([r["lo"], r["hi"]], [i, i], color=c, lw=1.6, alpha=0.55, solid_capstyle="round")
        ax.scatter([r["held"]], [i], s=58, color=c, marker="o" if r["call"] == "PASS" else "s", zorder=3,
                   edgecolor=SURFACE, linewidth=1.5)
        ax.text(max(r["hi"], r["held"]) + 2.2, i, f"{r['held']:+.0f}", va="center", fontsize=9.5, color=INK2)
    ax.set_yticks(range(len(R)))
    ax.set_yticklabels([r["name"] + (" *" if r["src"] == "retrospective" else "") for r in R], color=INK, fontsize=10)
    ax.axvline(0, color=INK, lw=1.2)
    ax.axvline(15, color=INK2, lw=1, ls=(0, (4, 3)))
    ax.text(0, len(R) - 0.2, " raw log", color=INK, fontsize=9.5, va="bottom")
    ax.text(15, len(R) - 0.2, " FAIL line (15 pts)", color=INK2, fontsize=9.5, va="bottom")
    ax.axvspan(-40, 0, color=PASS_C, alpha=0.05, lw=0)
    ax.text(-38, -1.15, "summaries beat the raw log", color=PASS_C, fontsize=9.5)
    ax.set_xlim(-40, 100)
    ax.set_ylim(-1.6, len(R) + 0.6)
    ax.set_xlabel("Detection lost by reading summaries instead of the raw log (points; same held-out deals and monitors)",
                  color=INK2, fontsize=10)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", colors=INK2)
    h1 = ax.scatter([], [], s=58, color=PASS_C, marker="o", label="canary called PASS")
    h2 = ax.scatter([], [], s=58, color=FAIL_C, marker="s", label="canary called FAIL")
    ax.legend(handles=[h1, h2], loc="lower right", frameon=False, fontsize=9.5)
    fig.suptitle(f"The summarizer is a dial: same deals, same monitors, {len(R)} summarizers", x=0.02, ha="left", fontsize=13.5,
                 color=INK, fontweight="bold")
    fig.text(0.02, 0.925, "Held-out set B; bars = 95% deal-clustered CI; * = scored before the prospective tests",
             fontsize=9.5, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(ROOT / "to_human/fig_dial.png", dpi=200, facecolor=SURFACE)
    fig.savefig(ROOT / "paper/fig_dial.pdf", facecolor=SURFACE)
    fig.savefig(ROOT / "to_human/panels/dial.png", dpi=150, facecolor=SURFACE)
    print(f"saved to_human/fig_dial.png, paper/fig_dial.pdf ({len(R)} summarizers)")


if __name__ == "__main__":
    main()
