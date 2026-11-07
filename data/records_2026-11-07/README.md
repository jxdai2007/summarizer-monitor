# Records used by the 2026-11-07 experiments (E3-E10), bundled for reproducibility

These are byte-identical copies, checked against `MANIFEST.sha256`, of the pilot records that today's experiment code
reads from `~/research-taste/swarm-alignment/pilots/2026-11-06/` (the author's machine).
- `loop8/runs/`: agent-written sessions (`sessions/`), privileged labels (`labels.jsonl`), and loop8 summaries and
  monitor scores. These are the corpus and the FULL/LUNA/GEM views for E3, E3b and E6.
- `loop2d/runs/newdeals_mon.jsonl`: set-B full-log monitor scores, the held-out baseline for E2-E2d, E4, E5, E8, E9
  and E10.
- `loop9/`: ChatDev corpus (`corpus2.json`), Grok-written deals (`runs/c2_gen.jsonl`) and set-C full-log scores
  (`runs/c2_mon.jsonl`), used by E7, E8 and E9.

To rerun from a clone, point the scripts' pilot path at this folder: replace
`Path.home() / "research-taste/swarm-alignment/pilots/2026-11-06"` and the absolute
`/Users/macstudio/research-taste/...` paths in `experiments/*/code/*.py` and `paper/make_numbers.py`.

Sources: Mantiq swarm traces and MAST-Data (ChatDev), both CC BY 4.0. All planted deals are fictional and benign. No
keys or personal data are included (scanned 2026-11-07).
