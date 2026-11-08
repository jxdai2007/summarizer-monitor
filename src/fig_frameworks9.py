"""E12 + E13 figure: for each of nine summarizers, held-out (set B) detection loss under our oversight-aware prompt
(blue circle), under each shipped framework prompt (orange squares, filled) and with E12's one-sentence notice added
(orange squares, hollow). Data: experiments/E12-framework-prompts/results/cells.json (locked analysis) and
experiments/E13-framework-prompts-scale/results/cells.json. Usage (from summarizer-monitor/):
  /Users/macstudio/projects/swarm-alignment/.venv/bin/python src/fig_frameworks9.py
Outputs: paper/fig_frameworks9.pdf, to_human/fig_frameworks9.png, to_human/panels/frameworks9.png
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
OURS_C, SHIP_C = "#2a78d6", "#eb6834"  # validated pair (dataviz palette slots 1-2)
E12 = json.load(open(ROOT / "experiments/E12-framework-prompts/results/cells.json"))
E13 = json.load(open(ROOT / "experiments/E13-framework-prompts-scale/results/cells.json"))
ROWS = [  # (label, source dict, key prefix, frameworks)
    ("Gemini 3.7 Flash", E12, "gemini-3.7-flash", ["langchain", "llamaindex"]),
    ("Tencent hy3", E12, "tencent-hy3", ["langchain", "lc-classic", "llamaindex", "langmem", "crewai"]),
    ("DeepSeek v4 Flash", E13, "deepseek-v4-flash", ["langchain", "llamaindex"]),
    ("GLM-5.3 Flash", E13, "glm-53-flash", ["langchain", "llamaindex"]),
    ("GLM-5.2", E13, "glm-5.2", ["langchain", "llamaindex"]),
    ("Qwen3.5-397B", E13, "qwen3.5-397b", ["langchain", "llamaindex"]),
    ("Gemma 4 31B", E13, "gemma-4-31b-it", ["langchain", "llamaindex"]),
    ("Qwen3.8-27B", E13, "qwen3.8-27b", ["langchain", "llamaindex"]),
    ("Qwen3.8-Flash-Next (local)", E12, "local-qwen3.8-flash-next", ["langchain", "lc-classic", "llamaindex", "langmem", "crewai"]),
]


def get(src, k):
    c = src.get(k)
    return None if not c else c.get("B")


def draw(paper):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig, ax = plt.subplots(figsize=(7.2, 3.9) if paper else (10.5, 5.6), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    n = len(ROWS)
    for i, (lab, src, key, fws) in enumerate(ROWS):
        y = n - 1 - i
        d = [get(src, f"{key}|{f}|default") for f in fws]
        nt = [get(src, f"{key}|{f}|notice") for f in fws]
        ours = get(src, f"{key}|safety|default")
        vals = [v for v in d + nt + [ours] if v is not None]
        if vals:
            ax.plot([min(vals), max(vals)], [y, y], color=GRID, lw=1.2, zorder=1)
        ax.scatter([v for v in d if v is not None], [y] * sum(v is not None for v in d), s=34, marker="s", color=SHIP_C,
                   zorder=3, edgecolor=SURFACE, linewidth=1)
        ax.scatter([v for v in nt if v is not None], [y] * sum(v is not None for v in nt), s=34, marker="s",
                   facecolor=SURFACE, edgecolor=SHIP_C, linewidth=1.4, zorder=3)
        if ours is not None:
            ax.scatter([ours], [y], s=52, marker="o", color=OURS_C, zorder=4, edgecolor=SURFACE, linewidth=1.2)
    ax.set_yticks(range(n))
    ax.set_yticklabels([r[0] for r in reversed(ROWS)], color=INK, fontsize=9)
    ax.axvline(0, color=INK, lw=1.0)
    ax.axvline(15, color=INK2, lw=0.9, ls=(0, (4, 3)))
    ax.text(15.8, n - 0.45, "FAIL line", color=INK2, fontsize=8, va="bottom")
    ax.set_xlim(-20, 80)
    ax.set_ylim(-0.7, n - 0.1)
    ax.set_xlabel("Detection lost, summaries vs raw log (points; held-out set B)", color=INK2, fontsize=9)
    ax.grid(axis="x", color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", colors=INK2)
    h = [plt.Line2D([], [], color=OURS_C, marker="o", ls="", ms=7, label="our prompt" if paper else "our oversight-aware prompt"),
         plt.Line2D([], [], color=SHIP_C, marker="s", ls="", ms=6, label="shipped prompt" if paper else "shipped framework prompt"),
         plt.Line2D([], [], markerfacecolor=SURFACE, markeredgecolor=SHIP_C, marker="s", ls="", ms=6, mew=1.4,
                    label="shipped + one sentence" if paper else "shipped prompt + one sentence")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=3, frameon=False, fontsize=8.5)
    fig.tight_layout()
    if paper:
        fig.savefig(ROOT / "paper/fig_frameworks9.pdf", facecolor=SURFACE)
    else:
        fig.suptitle("Nine summarizers: shipped prompts lose the deals for all; an oversight-aware prompt keeps them for most", x=0.01,
                     ha="left", fontsize=12.5, color=INK, fontweight="bold")
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        fig.savefig(ROOT / "to_human/fig_frameworks9.png", dpi=200, facecolor=SURFACE)
        fig.savefig(ROOT / "to_human/panels/frameworks9.png", dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    draw(True)
    draw(False)
    print("saved fig_frameworks9")
