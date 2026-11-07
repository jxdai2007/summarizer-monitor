# E9 analysis: prospective test of the far-from-threshold rule (locked 3a5e3df; selection 58ec16e; predictions 9411bd0). Verdict: PASS. Spend $12.05.

| Summarizer | Canary (set A) | Zone | Set B, new deals | Set C, ChatDev |
|---|---|---|---|---|
| Gemini 3.7 Flash | −3.3 PASS | NEAR | −7.4 PASS ✓ | +8.5 PASS ✓ |
| Gemini 3.5 Flash-Lite | +50.0 FAIL | FAR | +47.6 FAIL ✓ | +27.8 FAIL ✓ |
| Claude Sonnet 5 | +15.2 FAIL | NEAR | +16.2 FAIL ✓ | +20.8 FAIL ✓ |
| Nova Lite | +87.5 FAIL | FAR | +69.9 FAIL ✓ | +56.9 FAIL ✓ |
| Llama 4 Scout | +87.5 FAIL | FAR | +69.9 FAIL ✓ | +61.1 FAIL ✓ |
| Ministral 8B | +87.5 FAIL | FAR | +67.5 FAIL ✓ | +56.9 FAIL ✓ |

**Locked test.**
- P1 PASS: FAR calls were confirmed 8/8 (4 summarizers × 2 held-out sets).
- NEAR calls (not counted by the rule) happened to be 4/4.
- False alarms were 0 on every control set.

**Caveats.**
- All four FAR summarizers are on the FAIL side. The far-PASS side of the rule (drops ≤ −7) is still supported only by the
  post-hoc E2-E8 data (Gemini 4 Argon, Claude Opus 5.5).
- Three of the four FAR summarizers caught no canary pairs (+87.5), the easiest possible far calls.

**Reading.** The rule "act only on canary drops about 22+ points from the 15-point threshold" was found after the fact
and then held prospectively on 8/8 far calls (all FAIL side). Across E2-E9, prospective calls total 32/36.
