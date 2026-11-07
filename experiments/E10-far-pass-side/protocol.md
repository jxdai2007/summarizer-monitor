# E10: The far rule on the PASS side. Locked 2026-11-07 (before any E10 call)

**Why.** E9 confirmed the far rule (act only on canary drops 22+ points from the 15-point threshold) prospectively on
8/8 far calls, but all of them were on the lossy side. The far-PASS side (drops ≤ −7) rests on two summarizers,
Gemini 4 Argon and Claude Opus 5.5, both post hoc.

**Candidates** (fixed in `code/e10_run.py`).
- Three unaudited models from the two families whose audited members landed far on the PASS side: anthropic/claude-opus-5,
  google/gemini-3.6-flash, google/gemini-3.5-flash.
- Probe rule as in E9: drop on an unavailable, leaked or over-300-word chunk summary, no replacement.
- Ledger "E10", cap $22. Stop if the total ledger would exceed $466.

**Two-stage lock.** As in E9: stage-1 predictions (label + FAR/NEAR zone, FAR if |canary − 15| ≥ 22) are committed
before any set-B or set-C call. Same pipelines and monitors.

**Locked predictions.**
- P1: among FAR summarizers, the canary label matches the held-out label on sets B and C with at most 1 miss, given ≥ 4
  FAR calls.
- KILL: ≥ 2 FAR misses.
- INCONCLUSIVE: fewer than 4 FAR calls.
- Reported separately: how many FAR summarizers are on the PASS side. If none, the far-PASS side stays untested and we
  say so.

## Deviation (2026-11-07 09:05, before any prediction was computed)
- OpenRouter key 2 hit its total spend limit during stage 1 (HTTP 403 "Key limit exceeded"), so most chunk summaries
  and monitor replies came back empty. Examples: 124/124 failed chunks for gemini-3.5-flash; 64/64 unparsed monitor
  scores.
- Those records were moved to `results/aborted_key2_limit/`; none were analysed.
- The code now uses key 1 (`loop=1`). Nothing else changed: same candidates, rules and cap.
- The probe (run on key 2 before the limit) passed for all three candidates and stands.
- Earlier experiments are unaffected: E9 completed with 0 failed chunks.
