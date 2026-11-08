# E13 analysis

## Result, locked analysis (20:53 PT; 2,596 of 2,598 records): **PASS**
- **Q1 PASS.** Shipped prompts: 12/12 FAIL, mean +62.4.
- **Q2 PASS.** The notice is better in 11/12 pairs, with a mean reduction of +20.5.
- **Q3 PASS.** Agreement 29/30. The canary cleared 5 of the 6 held-out-PASS cells and flagged 24 of the 24 FAIL cells.
  Balanced accuracy 0.92; ρ = 0.94.
- **Q4 PASS.** Notice controls: 0/500 pairs flagged.


## Deviations (logged before any analysis of E13 scores)
- **D0, throughput only (18:37 and 18:42 PT).** The runner was restarted twice:
  - 18:37: Adaption client concurrency 96 → 400, job concurrency 40 → 120, monitor concurrency 64 → 128.
  - 18:42: jobs interleaved round-robin across summarizers within each set, because Adaption appears to rate-limit per
    model and the original order ran one model at a time.
- Prompts, models, sampling, sets and analysis are unchanged.
- Records are append-only and resumable; in-flight jobs were dropped and re-run.

- **D1, refill of empty chunk summaries (20:55 PT; logged before any refilled score).** The locked records have 589
  empty chunks out of about 10,000. They are concentrated in the LangChain-prompt arms:
  - qwen3.8-27b: 139/286 (default) and 308/365 (notice);
  - glm-53-flash notice: 63/365;
  - deepseek-v4-flash: 28/286 and 12/365;
  - qwen3.5-397b under our prompt: 32/365.
- **Why it matters.** Empty chunks reach the monitor as "(summary unavailable)", which inflates the loss. This is
  likely why qwen3.8-27b's notice arm looks worse than its default arm, the one pair in Q2 that does not improve.
- **Fix.** `e13_run.py refill` re-summarizes only the empty chunks with max_output_tokens 32000, re-runs both monitors,
  and writes `*_refill.jsonl`. The locked records stay untouched. Both analyses are reported. Headline numbers stay with
  the locked analysis unless a label differs, and any label that differs is reported.
