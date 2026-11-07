# E8 analysis: canary on vendors chosen without regard to outcome (locked 8d3c001; selection b41c02e; predictions eedb7f5). Verdict: KILL. Spend $18.40.

**Selection.** The locked probe rule chose Tencent hy3, Z.ai GLM-5.3-prime and ByteDance Seed-2.0-lite. Tencent hy4 and
Seed 2.1 Turbo returned unavailable chunk summaries in the probe.

| Summarizer | Canary (set A) | Set B, new deals | Set C, ChatDev |
|---|---|---|---|
| Tencent hy3 | +13.6 PASS | +3.9 PASS ✓ | +15.2 [+4, +27] FAIL ✗ |
| GLM-5.3-prime | +12.3 PASS | +9.2 PASS ✓ | +28.1 [+14, +42] FAIL ✗ |
| Seed-2.0-lite | +23.8 FAIL | +2.5 PASS ✗ | +19.4 [+10, +29] FAIL ✓ |

**Locked tests.**
- P1 FAIL: set B labels 2/3.
- P2 FAIL: set C labels 1/3.
- KILL: 3/6 total matches.
- False alarms: 0 on every control set.

**Reading.**
- All three outcome-blind picks landed within 9 points of the 15-point threshold. At that distance the canary's label
  did not carry over.
- The three ChatDev drops are all higher than the canary (+1.6 to +15.8), and the set-B drops are all lower.
- The canary's absolute level is not portable across deal sets. Earlier work already flagged this: on average the canary
  overstates set-B loss by +11.6 points.

**Exploratory, post hoc, `distance_exploratory.txt`.** All 24 prospective canary calls from E2-E2d, E7 and E8, grouped by
the canary drop's distance from the threshold:
- Every call 21.7 or more points from the threshold was confirmed: 14/14.
- Calls within 9 points were confirmed 6/10.
- No call fell between 9 and 21.7 points, so the band edge is not identified.
- Earlier selection (fixed vendor orders, then likely passes) produced mostly far-from-threshold summarizers, which is
  why the pooled 12/12 looked clean.
- Practical rule, post hoc: treat canary drops within about 10 points of the threshold as undecided. Repeat the audit,
  or audit on a second environment.
