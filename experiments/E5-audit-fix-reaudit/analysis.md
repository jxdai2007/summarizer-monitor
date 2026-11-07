# E5 analysis: audit → fix → re-audit (locked ebbee5b). Verdict under the locked rule: PASS (weakly informative). Spend $2.70.

| Summarizer | Original canary / held-out | FIX canary | FIX held-out | FIX controls flagged |
|---|---|---|---|---|
| gpt-oss-120b | +74.2 / +52.4 | +57.1 (FAIL) | +45.0 (FAIL) | 0/42 |
| MiniMax M3.1 Flash | +36.7 / +26.7 | +26.8 (FAIL) | +25.0 (FAIL) | 0/42 |

**Locked tests.**
- P1 PASS: labels match.
- P2 PASS: the canary and held-out changes go the same direction.
- P3 PASS: no over-flagging.

**Why "weakly informative".**
- Every label, before and after the fix, was FAIL, so an always-FAIL rule also passes P1.
- The fix helped only modestly:
  - The canary moved −17 (gpt-oss) and −10 (MiniMax).
  - Held-out moved −7 and −2.
- The audit correctly called both fixed summarizers still lossy, but it overstated the fix's gain, consistent with the
  known canary offset (+11.6 points).

**Exploratory, a side effect the audit caught.**
- With the FIX sentence, MiniMax failed to return 71 of 365 chunk summaries (19.5%: 25/124 set A, 29/162 set B, 17/79
  controls; 58/95 logs had at least one), against 0 failures in its original E2 runs on the same logs.
- Monitors then read "(summary unavailable)" for those segments.
- Post hoc, on fully summarized logs only, MiniMax FIX drops +12.5 (set A, 13 logs) and +9.1 (set B, 18 logs). That would
  be PASS on both, so the fix may work when it runs.
- These subsets are small and selected after the fact; this is a lead, not a result.

**Reading.**
- The audit → fix → re-audit loop gives consistent direction, and it refused to pass fixes that did not close the gap.
- The one-sentence fix tested here is not a general remedy.
- MiniMax's held-out change (−1.7) is within E4's run-to-run noise, so its direction match is noise-level.
- The MiniMax FIX numbers mix the prompt effect with the 20% failed chunks.
- Review (fresh, PASS WITH FIXES): numbers reproduced; the chunk-failure rate was corrected from "25-29%" (those were
  counts) to 19.5%.
