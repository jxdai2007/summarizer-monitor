"""E12 figure: held-out (set B) detection loss for each framework's shipped summary prompt, as shipped vs with the
one-sentence oversight notice, per summarizer (small multiples), with our oversight-aware prompt as a reference line.
Data: experiments/E12-framework-prompts/results/cells.json (written by e12_run.py analyze from the raw records).
Usage (from summarizer-monitor/): /Users/macstudio/projects/swarm-alignment/.venv/bin/python src/fig_frameworks.py
Outputs: to_human/fig_frameworks.png, paper/fig_frameworks.pdf, to_human/panels/frameworks.png
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
NOTICE_C, DEFAULT_C = "#2a78d6", "#eb6834"  # validated pair (dataviz palette slots 1-2)
FW = [("langchain", "LangChain v1\n(SummarizationMiddleware)"), ("lc-classic", "LangChain classic\n(SummaryMemory)"),
      ("llamaindex", "LlamaIndex\n(ChatSummaryMemory)"), ("langmem", "LangMem\n(summarize_messages)"),
      ("crewai", "CrewAI\n(context summarizer)")]
SUMS = [("tencent-hy3", "Tencent hy3"), ("local-qwen3.8-flash-next", "Qwen3.8-Flash-Next (local)"),
        ("gemini-3.7-flash", "Gemini 3.7 Flash (2 frameworks)")]


def main():
    C = json.load(open(ROOT / "experiments/E12-framework-prompts/results/cells.json"))  # locked analysis (headline)
    have = [(s, t) for s, t in SUMS if any(C.get(f"{s}|{f}|default", {}).get("B") is not None for f, _ in FW)]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig, axes = plt.subplots(1, len(have), figsize=(4.1 * len(have) + 1.4, 4.6), facecolor=SURFACE, sharey=True,
                             squeeze=False)
    axes = axes[0]
    for ax, (s, title) in zip(axes, have):
        ax.set_facecolor(SURFACE)
        ref = C.get(f"{s}|safety|default", {}).get("B")
        for i, (f, _) in enumerate(FW):
            d, n = C.get(f"{s}|{f}|default", {}), C.get(f"{s}|{f}|notice", {})
            if d.get("B") is None:
                continue
            y = len(FW) - 1 - i
            if n.get("B") is not None:
                ax.annotate("", xy=(n["B"], y), xytext=(d["B"], y),
                            arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.2, shrinkA=6, shrinkB=6))
                ax.scatter([n["B"]], [y], s=60, color=NOTICE_C, marker="o", zorder=3, edgecolor=SURFACE, linewidth=1.5)
                ax.text(min(n["B"], d["B"]) - 3.5, y, f"{n['B']:+.0f}", ha="right", va="center", fontsize=8.5, color=NOTICE_C)
            ax.scatter([d["B"]], [y], s=60, color=DEFAULT_C, marker="s", zorder=3, edgecolor=SURFACE, linewidth=1.5)
            ax.text(max(d["B"], n.get("B") or -99) + 3.5, y, f"{d['B']:+.0f}", ha="left", va="center", fontsize=8.5,
                    color=DEFAULT_C)
        ax.axvline(0, color=INK, lw=1.1)
        ax.axvline(15, color=INK2, lw=0.9, ls=(0, (4, 3)))
        if ref is not None:
            ax.axvline(ref, color=NOTICE_C, lw=1.0, ls=(0, (1, 2)))
            ax.text(ref + 1.5, len(FW) - 0.45, f"our prompt {ref:+.0f}", color=NOTICE_C, fontsize=8, ha="left", va="bottom")
        ax.set_title(title, fontsize=10.5, color=INK, loc="left", pad=22)
        ax.set_xlim(-25, 108)
        ax.set_ylim(-0.8, len(FW) + 0.3)
        ax.grid(axis="x", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", colors=INK2)
    axes[0].set_yticks(range(len(FW)))
    axes[0].set_yticklabels([t for _, t in reversed(FW)], color=INK, fontsize=9)
    fig.supxlabel("Detection lost by reading summaries instead of the raw log (points; held-out set B; 15 = FAIL line)",
                  color=INK2, fontsize=9.5)
    h1 = plt.Line2D([], [], color=DEFAULT_C, marker="s", ls="", ms=8, label="framework prompt as shipped")
    h2 = plt.Line2D([], [], color=NOTICE_C, marker="o", ls="", ms=8, label="+ one sentence: a monitor will read this")
    fig.legend(handles=[h1, h2], loc="upper left", frameon=False, fontsize=9, ncol=2, bbox_to_anchor=(0.005, 0.935))
    fig.suptitle("Shipped summary prompts hide split deals; one added sentence helps some summarizers far more than others", x=0.01, ha="left", y=0.985,
                 fontsize=12.5, color=INK, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    fig.savefig(ROOT / "to_human/fig_frameworks.png", dpi=200, facecolor=SURFACE)
    fig.savefig(ROOT / "paper/fig_frameworks.pdf", facecolor=SURFACE)
    fig.savefig(ROOT / "to_human/panels/frameworks.png", dpi=150, facecolor=SURFACE)
    print(f"saved fig_frameworks ({len(have)} summarizer panels)")


if __name__ == "__main__":
    main()
