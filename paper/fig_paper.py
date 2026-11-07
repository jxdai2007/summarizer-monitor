"""Paper layout of the main figure: the same panel code and data as src/fig_main.py, split into two figures so the text
stays legible at single-column width. Usage (from summarizer-monitor/):
  /Users/macstudio/projects/swarm-alignment/.venv/bin/python paper/fig_paper.py
Outputs: paper/fig_ceiling.pdf (panel A), paper/fig_realism_testimony.pdf (panels B and C).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import fig_main as fm  # noqa: E402

plt = fm.plt
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": "white", "savefig.facecolor": "white"})
fm.SURFACE = "white"

# Figure 1: the ceiling (panel A)
fig = plt.figure(figsize=(10.5, 9.6))
ax = fig.add_axes([0.10, 0.25, 0.86, 0.62])
fm.panel_a(ax)
fig.savefig(ROOT / "paper/fig_ceiling.pdf")

# Figure 2: realism (panel B) and testimony + fixes (panel C)
fig = plt.figure(figsize=(15, 8.8))
gs = fig.add_gridspec(2, 2, width_ratios=[0.9, 1.0], height_ratios=[1.6, 1.0], left=0.06, right=0.985, top=0.86,
                      bottom=0.2, wspace=0.28, hspace=0.62)
ax_b = fig.add_subplot(gs[:, 0])
ax_ct = fig.add_subplot(gs[0, 1])
ax_cb = fig.add_subplot(gs[1, 1])
fm.panel_b(ax_b)
fm.panel_c(ax_ct, ax_cb)
for a in (ax_ct, ax_cb):
    pos = a.get_position()
    a.set_position([pos.x0 + 0.13, pos.y0, pos.width - 0.13, pos.height])
fig.savefig(ROOT / "paper/fig_realism_testimony.pdf")
print("saved paper/fig_ceiling.pdf, paper/fig_realism_testimony.pdf")
