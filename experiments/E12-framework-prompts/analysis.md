# E12 analysis (in progress)

## Deviations (logged before the affected results were seen)

**D0, throughput only (15:47 and 15:56 PT).** The runner was restarted twice to raise client concurrency: separate
OpenRouter clients per lane, local Splash concurrency 6 → 16 → 32. Prompts, models, max_tokens and records are unchanged.
In-flight jobs were dropped and re-run. Completed records are append-only and resumable.

**D1, refill of empty hy3 chunk summaries (16:02 PT).**
- *What happened.* With LangChain's default prompt ("think deeply about what information is most important"), Tencent
  hy3 at default reasoning used up the locked max_tokens of 4000 in reasoning and returned no text.
  - Interim count: 47 of 162 set-B chunks.
  - Diagnosis call (tag `E12-diag`, $0.006): `finish_reason=length`, 4000 of 4000 completion tokens were reasoning, for
    3 of 4 chunks of one log.
- *Why it matters.* The locked pipeline passes "(summary unavailable)" to the monitor for such chunks. That inflates the
  loss for reasons that have nothing to do with what the summarizer chose to keep.
- *Fix.* `e12_run.py refill` re-summarizes only the empty chunks with max_tokens 16000 and keeps every other chunk
  summary. It then re-runs both monitors on the repaired summaries and writes `*_refill.jsonl` next to the locked records,
  which stay untouched.
- *Reporting.* Both analyses are reported: `analysis.txt` (locked) and `analysis_refill.txt` (D1). Claims use the D1
  numbers only where the two disagree in label, and say so.
- *What had been seen at decision time.* The interim drop on hy3's LangChain default arm: +67.5 over all logs, +65.0 on
  the 10 logs with no failed chunk. No refilled score had been seen.
- *Scope.* The local and Gemini lanes had 0 failed chunks at decision time and are not refilled.

**D2, budget (16:08 PT).**
- The D1 refill has its own ledger tag, `E12-refill`, capped at $9. The main E12 cap stays $18.
- The ledger stop line moves from $475 to $484, still inside the approved overall $500. The ledger was $458.6 at the
  time.

**D2b, budget (16:13 PT).** At 200 of 861 remaining hy3 logs the E12 tag was at $9.88, and its cost per log (about $0.018
with monitors) projected past the $18 cap. The cap was raised to $25 and the main run restarted (resumable; no prompts
changed). Projected ledger at the end is about $483, under the $484 stop line and the approved $500.
