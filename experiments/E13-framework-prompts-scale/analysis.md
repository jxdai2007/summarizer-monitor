# E13 analysis (in progress)

## Deviations (logged before any analysis of E13 scores)
- **D0, throughput only (18:37 and 18:42 PT).** The runner was restarted twice:
  - 18:37: Adaption client concurrency 96 → 400, job concurrency 40 → 120, monitor concurrency 64 → 128.
  - 18:42: jobs interleaved round-robin across summarizers within each set, because Adaption appears to rate-limit per
    model and the original order ran one model at a time.
- Prompts, models, sampling, sets and analysis are unchanged.
- Records are append-only and resumable; in-flight jobs were dropped and re-run.
