# Submission checklist: Jollen only (2026-11-07)

Everything below needs you. Nothing has been submitted, published or pushed.

## Deadlines
- **Video:** Sun 8 Nov, 10:00 PT (LA hub; this gates the top 15).
- **Report PDF:** Sun 8 Nov, 23:59 AoE = Mon 9 Nov, 03:59 PT (Apart global round).

## 1. Fill three placeholders in `paper/main.tex` (about 10 min)
- **Line 27, author:** replace `\todo{full name and affiliation: TO FILL}` with your full name and affiliation.
- **Line 147, repo link:** replace `\todo{repository link: TO FILL}` with the public repo URL once you have published it
  (step 3).
- **Line 149, LLM usage statement:** rewrite the sentence after "LLM usage statement." to describe your own role, and
  delete `\todo{Jollen: edit to describe your own role.}`.
- **Rebuild:** `cd summarizer-monitor/paper && tectonic -X compile main.tex`. Check that no red text is left and that
  the main text ends on page 8.

## 2. Decide: LaTeX PDF or Apart's Google Doc template
- Apart says to use its official template, a Google Doc (see `paper/README.md` §Template).
- `main.tex` follows that template's structure: title footnote, authors, "With Apart Research", abstract, sections,
  limitations/dual-use appendix.
- **My recommendation:** submit the LaTeX PDF unless the form rejects it. Porting is about 1 h of copy-paste, and every
  number would have to be re-checked by hand.

## 3. Publish the code repo (needed for the repo link; about 30 min)
- The tracked files have no keys or personal email (scanned 7 Nov). `.env` is gitignored.
- Records for today's experiments (E3-E10) are now bundled in `data/records_2026-11-07/` (13 MB, sha256 manifest).
  Older pilot runs still read from `~/research-taste/...`; their consolidated CSVs are in `data/`.
- The `publish-research-repo-cleanly` skill covers the scrub, verify and cold-clone steps. Ask me to run it, then you
  create the GitHub repo and push.

## 4. Record the video (about 1-2 h)
- **Script:** `to_human/video_narration_clean.md`, about 410 words, about 3:00. It's a draft; rewrite it in your own voice.
  Sources for every number are in `to_human/video_script.md`.
- **On-screen material:**
  - `to_human/demo.html` (offline replay; tabs 1-3)
  - `to_human/fig_dial.png` (the dial, now the paper's Figure 1: 26 summarizers on the same held-out deals)
  - `to_human/slides.html` (12 slides)
- Keep the scope line in beat 7: agent-written deals show a small effect at matched false alarms.

## 5. Press submit (yours alone)
- **Video:** the LA-hub form, by Sun 10:00 PT.
- **Report PDF:** the Apart project page, by Mon 03:59 PT. Resubmitting with the same title replaces the PDF.

## Account item
- OpenRouter key 2 has reached its total spend limit (403). Key 1 still works. Raise key 2's limit only if you want more
  runs.

## State of the evidence (for your talk)
- **Planted deals:** the summarizer is a dial. GPT-5.6-luna 55/80 → 25/80; Opus summaries beat the raw log, 70/78 vs
  54/78.
- **Canary audit:** 32/36 prospective calls right (always-FAIL 26/36).
  - 12/12 in the first four tests.
  - 5/6 in a second environment.
  - 3/6 for vendors picked blind, all near the threshold (E8 failed).
  - Far from the threshold: 14/14 post hoc, then 8/8 in a preregistered test (all lossy side).
  - A preregistered PASS-side test (E10) was inconclusive: only 1 of 3 new summarizers landed far.
  - Near the threshold, treat the label as undecided.
- **Agent-written deals:** small losses. Calibration shifts a lot between summarizers (the 10%-FA threshold ranges
  23-83). The canary ranking met its bar with two monitor families.
- **Testimony:** a blame note gets laundered through summaries: 16/28 vs 0/14 on raw logs. One summarizer line fixes it
  (0/28).
