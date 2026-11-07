# E3b analysis: E3 re-scored with Grok 4.20 as monitor (locked 237ecb0). Verdict: PASS. Spend $2.37.

**Sessions.** 66 coordinated / 64 controls, all scored in every view (0 unparsed). Summaries are identical to E3; only
the monitor changed. Raw output: `results/analysis.txt`.

| View | Canary | AUC (loss vs full) | Matched-FA detection (loss) | Controls flagged at threshold 50 |
|---|---|---|---|---|
| FULL | — | 0.725 | 0.348 | — |
| luna | +39.7 | 0.781 (−0.06) | 0.394 (−4.5) | 64% |
| Gemini 3.8 Flash | −8.1 | 0.838 (−0.11) | 0.379 (−3.0) | 98% |
| Gemini 4 Argon | −12.5 | 0.855 (−0.13) | 0.227 (+12.1) | 83% |
| Kimi k3.1 | +8.2 | 0.796 (−0.07) | 0.561 (−21.2) | 83% |
| gpt-oss-120b | +74.2 | 0.580 (+0.15) | 0.167 (+18.2) | 89% |
| Phi-4 | +87.5 | 0.708 (+0.02) | 0.076 (+27.3) | 23% |

**Locked tests.**
- P1 PASS: Spearman(canary, AUC loss) = +0.94.
- P2 PASS: FAIL−PASS matched-FA loss = +17.7 points, bootstrap 95% CI [+9.1, +40.4].

**With E3 (Haiku monitor).**
- Haiku met P1 (ρ = +0.60, at the bar) but not P2 (+9.1, CI −2.0 to +19.2).
- Grok meets both.
- Across two monitor families, the canary ranks summarizers on agent-written deals in the predicted direction.
- The size of the gap depends on the monitor.

**Caveats.**
- Grok over-flags controls at the default threshold (23-98% depending on summarizer), so its matched thresholds are high
  (66-86) and matched-FA detection is low and noisy.
- As in E3, luna and Gemini 3.8 Flash summaries were seen before the lock; the four others are prospective with respect
  to these sessions.
- Grok 4.20 wrote the planted deals in sets B and C but plays no role in this corpus.
