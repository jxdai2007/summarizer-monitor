# E4 analysis: canary audit test-retest (locked before any call). Verdict: PASS. Spend $5.09.

Re-ran the set-A canary twice for 5 summarizers. Same pipeline as E2; originals recomputed from their records match the
published drops exactly. Raw output: `results/analysis.txt`.

| Summarizer | Original | Rerun 1 | Rerun 2 | Labels | SD (3 runs) |
|---|---|---|---|---|---|
| gpt-5.6-terra | +22.2 | +19.7 | +22.6 | FAIL ×3 | 1.3 |
| MiniMax M3.1 Flash | +36.7 | +36.7 | +39.0 | FAIL ×3 | 1.1 |
| Gemini 4 Argon | −12.5 | −10.9 | −12.5 | PASS ×3 | 0.7 |
| gpt-oss-120b | +74.2 | +71.4 | +84.1 | FAIL ×3 | 5.5 |
| Nemotron 3.5 Super | +19.7 | +15.8 | +15.0 | FAIL, FAIL, PASS | 2.0 |

- **P1: PASS.** Labels matched in 9 of 10 reruns.
- **P2: PASS.** All 10 reruns were within 10 points of the original.
- KILL not met. The mean SD across 3 runs was 2.1 points.
- The single flip is Nemotron, the case already flagged as borderline in E2b: one rerun landed exactly on the threshold
  (15.0, which counts as PASS under "FAIL if > 15").
- **Reading:** a single audit run is repeatable to about ±2 points for most summarizers. A borderline band of ±5 points
  around the threshold (about 2 SD) would have flagged the only unstable case.
