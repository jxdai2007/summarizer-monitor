# paper/: hackathon report draft (PRIVATE, for Jollen to review and submit)

"The Summarizer Is the Monitor", Apart Research x AI Alignment Foundation Swarm Alignment Hackathon, Track 4.
Not submitted, uploaded or shared. Jollen submits it himself.

## Build
From `summarizer-monitor/`:
```
python3 paper/make_numbers.py                                          # writes paper/numbers.tex + paper/tables.tex
/Users/macstudio/projects/swarm-alignment/.venv/bin/python paper/fig_paper.py   # paper/fig_ceiling.pdf, fig_realism_testimony.pdf
cd paper && tectonic -X compile main.tex                                # main.pdf (tectonic runs bibtex itself)
```
Every number in `main.tex` is a `\N{key}` macro from `numbers.tex`, or a row of a `tables.tex` table. Both are written by
`make_numbers.py` from `data/*.csv`, the E1/E2/E2b `analysis.md` and `results/results.txt` files, the E2b
`stage1_predictions.json`, and the review files `review2/l2_13.md`, `review2/agent_records.md` and loop2d result files in
`~/research-taste/swarm-alignment/pilots/2026-11-06/`. Review-file numbers are matched by regex; the script stops if a
pattern disappears. An unknown key prints as a red `??key` in the PDF. Design constants (4 planted messages, 50-message
chunks, threshold 50, the 15-point audit rule) are typed in the text. Commit hashes in Appendix E are copied from `git log`.

The figures reuse the panel functions of `src/fig_main.py` (same data, same code); `fig_paper.py` only splits the
three-panel figure in two so that the text is legible at page width.

## Template
The official Apart template is a Google Doc
(https://docs.google.com/document/d/1_1_27EyZriMlc8n8EBE2YScaeyMjm-8xjR097nmHXAE, linked from
https://apartresearch.com/sprints/swarm-alignment-2026), not a LaTeX class. This draft is a clean single-column LaTeX
article that follows the template's structure: title with hackathon footnote, authors, "With Apart Research", abstract
(150-250 words; currently about 248 by pdftotext), Introduction with a contributions list, Related Work, Methods, Results,
Discussion and Limitations, Conclusion, Code and Data, LLM Usage Statement, References, Appendix. If the PDF must be
produced from the Google Doc itself, paste the sections into a copy of that doc.

Page count: main text pages 1-7 (references start on page 7); appendices follow. Limit: 8 pages excluding references
and appendices.

## Preexisting code (kickoff Fri 6 Nov 2026 13:30 PT)
- `steer/` in `~/projects/swarm-alignment` predates the sprint (first commit 43dcc62, 2026-11-04 23:58 PT; last change
  15044d6, 2026-11-06 00:39 PT). It is imported by the repo's own `tests/`, `analysis/`, `replay/`, and by pilot scripts
  that feed no result in the report (`pilots/2026-11-06/pa_laundering.py`, `pb_audit.py`, six scripts in `loop2/`).
- No code behind the report imports `steer`, directly or through pilot modules (checked: loop1b, loop1c, loop2b, loop2c,
  loop2d, loop6, loop7, loop8, loop9, loop10, review2, `or_client.py`, `summarizer-monitor/src`, `experiments`).
- Everything else was written after kickoff: the earliest pilot commit in `~/research-taste` is ae3e5cb (2026-11-06
  14:48 PT); `summarizer-monitor/` starts at 53978cd (22:23 PT).

## Citations
All ten papers in `refs.bib` were checked against their arXiv abstracts (get_abstract) on 2026-11-06. Eight come from
`literature/survey.md`; `cemri2025mast` (2503.13657, MAST) and `qian2023chatdev` (2307.07924, ChatDev) were added for the
corpora and verified the same way. The two Hugging Face dataset URLs returned HTTP 200. Not cited: Sumers et al. 2025
(hierarchical-summary monitoring, an Anthropic blog post): its URL was not verified, so the Introduction carries a red
TODO where it belongs. Add it only after opening the post.

## For Jollen to fill or decide
- Sumers et al. 2025 citation (red TODO in the Introduction): open the blog post, add a bib entry with its URL.
- Author line: full name and affiliation (`\author{...}` in main.tex).
- Repository link (Code and data paragraph).
- LLM usage statement: describe your own role.
- Whether to port the text into the official Google Doc template.
