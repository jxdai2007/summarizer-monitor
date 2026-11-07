# E10 analysis: the far rule on the PASS side (locked d22a2db; deviation a5c373b). Verdict: INCONCLUSIVE by the locked rule. Spend $15.91 (includes the key-2 aborted attempt).

**Stage 1** (set-A canary, key 1; predictions committed with this file).

| Summarizer | Canary drop | Label | Zone |
|---|---|---|---|
| Claude Opus 5 | −11.1 | PASS | FAR |
| Gemini 3.6 Flash | −1.6 | PASS | NEAR |
| Gemini 3.5 Flash | −3.2 | PASS | NEAR |

- Controls flagged 0 for all three.
- Only one summarizer landed in the far zone, so at most 2 FAR calls are possible. The locked rule needs ≥ 4, so the
  verdict is INCONCLUSIVE whatever stage 2 would show.
- **Stage 2 was not run.** It could not change the locked verdict, and the Opus-tier held-out runs (about $10) would have
  pushed the total ledger near the $466 stop line.
- No held-out data exist, so nothing was selected after the fact.

**Reading.**
- The far-PASS side of the rule remains supported only by the post-hoc E2-E8 cases (Gemini 4 Argon, Claude Opus 5.5).
- Claude Opus 5 adds a third far-PASS canary, but it has no held-out confirmation.
- Two of three Gemini models landed near the threshold. Far-PASS summarizers seem rare, which limits how often the
  audit can clear a summarizer with confidence.
