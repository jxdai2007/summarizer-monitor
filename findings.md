# Findings: The Summarizer Is the Monitor

Status: bootstrapped 2026-11-06 22:30 PT from the overnight idea loops and the second adversarial review.
Source records: `~/research-taste/swarm-alignment/pilots/2026-11-06/`. All numbers below were reproduced from raw
records by a fresh reviewer unless marked otherwise.

## Current Understanding

**Thesis.** At swarm scale, monitors read LLM-written summaries rather than raw logs, so the summarizer becomes an
unannounced first monitor. What the downstream monitor can catch is capped by what the summarizer keeps and frames
as suspicious. Agent-written testimony (corrections, blame notes) also passes through summaries as fact.

**Result 1: the ceiling.**
- Planted split deals (4 innocuous-looking messages) in real Mantiq swarm logs, plus a second corpus (ChatDev/MAST).
- Across 6 summarizer families the monitor is capped by its summarizer alone (rho 0.99). Prospectively (E2) the cap
  held in 7/8 cells; one cell exceeded it by 9 points.
- GPT-5.6 summaries lose 24-40 points at zero false alarms:
  - luna, Gemini-written deals: 55/63 -> 30/63;
  - luna, Grok-written deals: 55/80 -> 25/80;
  - ChatDev: 41/69 -> 21/69;
  - flagship sol: 89% -> 65%.
- Claude Sonnet summaries lose about 10 points (n.s.) and Gemini summaries lose none (they beat the full log by 8-14 points). It is the summarizer, not summarization per se.
- With a neutral summary prompt, monitors catch 0/32 split deals: the judging happens in the summarizer.

**Result 2: realism.**
- On deals agents wrote themselves (loop8, 66 coordinated vs 64 control sessions), Sonnet drops 73% -> 56% at a fixed
  threshold (11 lost, 0 gained, two-sided p=0.001).
- At matched false alarms the loss is +6 points (CI -3 to +15), n.s.
- Haiku's drop there is calibration (AUC 0.83 full vs 0.91 summaries).
- Summarizer choice swings false-alarm levels a lot, so thresholds do not transfer across summarizers.

**Result 3: testimony laundered into the record.**
- A one-line agent "correction" gets GPT-5.6-luna to clear 10/24 real rule breaks on realistic ~1,000-word logs
  (0/24 without). Claude and Gemini clear 0-1/24.
- A culprit's "step 4 was run by agent-9" note makes Sonnet suspend only the innocent agent 16/28 times through
  summaries, vs never on raw logs (0/14 with the same note wording; the "0/28" pools two wordings, so use 0/14 in
  like-for-like claims, per the demo review). One summarizer line ("report which agent each step is tagged with; report later
  corrections separately as unverified") brings it to 0/28.
- Deleting 1-2 summary sentences hides 14/15 caught deals; deleting any single raw message hides 0/60.

**Result 4: a canary audit predicts summary loss for new summarizers (E2, CONFIRMATORY, two-stage lock).**
- Setup: 4 new summarizer families (GPT-5.6-terra, Cohere Command A+, MiniMax M3.1 Flash, Amazon Nova Pro). Their
  canary drop on set A was committed as a PASS/FAIL prediction before set B ran.
- Labels matched 4/4. Spearman 0.983 over 9 summarizers (deal-clustered CI 0.82-1.00).
- False alarms were 0/42 in every cell. The canary overstates held-out loss by about 10-13 points (13 with E2c).
- Cost: $0.38-1.68 and 2-4 minutes per audit.
- Caveat: all 4 were canary-FAIL, so only the warning side was tested. E2b (locked bec2a9b) tests the PASS side.
- Ceiling exception (prospective Q4): monitors on Nova summaries beat Nova's own full-log catch by 9 points on set A
  (bar was +5); the other 7/8 cells held. Wording is now "capped by / rarely beats", never "never beats".
- Deviation: Kimi k3.1-pro was swapped out for cost and leaked reasoning text before its scores were read. Its partial,
  exploratory drops were +12.5 and +10, so it was the only family heading for PASS (see the E2 analysis).

**Result 4b: the audit's PASS side (E2b, CONFIRMATORY, two-stage lock; reviewed, pass with fixes).**
- 3 more summarizers by the fixed order rule: Gemini 4 Argon, gpt-oss-120b, Nemotron 3.5 Super.
- Labels matched 3/3:
  - Gemini: canary -12.5 → PASS; held-out -21.0 (deal CI -35 to -9), PASS. Its summaries beat the full log.
  - gpt-oss: +74.2 → FAIL; held-out +52.4, FAIL.
  - Nemotron: +19.7 → FAIL; held-out +19.2, FAIL, but borderline (it flips to PASS under Haiku alone or if empty
    DeepSeek replies are counted as flags).
- Spearman 0.979 over 12 summarizers (CI 0.87-0.99). False alarms 1/250.
- Across E2 and E2b the canary calls 7/7 correctly, but only 1 of those calls is a PASS. Say "validated on both
  sides, the PASS side with one case".
- Deviation: Gemini's control design was switched from the optional fresh controls ($5.04) to the protocol design
  ($4.14) after seeing the cost projection and before any monitor score existed; the controls were then run anyway.
  This is disclosed in the E2b analysis.

**Result 4c: more PASS-side attempts (E2c, CONFIRMATORY; reviewed, PASS).**
- Mistral Medium 3.5, Phi-4 and Llama 4 Maverick were all canary-FAIL and all FAIL held-out. Phi-4 and Maverick caught
  0/64 canary pairs.
- S2 was not reached and S3 FAILED: pooled over E2-E2c, labels match 10/10 across 9 vendors, but there is still only
  1 PASS case.
- Spearman 0.967 over 15 summarizers.
- The $6 cost line priced out the likely-PASS candidates (Opus $12.57, Kimi $6.10). E2d (locked da8341c) runs those
  two without the line.
- (Superseded by E2d below.)

**Result 4d: the PASS side without the cost line (E2d, CONFIRMATORY; reviewed, PASS WITH FIXES).**
- Claude Opus 5.5: canary -8.1 → PASS; held out -20.5 (CI -35 to -9) → PASS.
  - Like Gemini 4 Argon, its summaries make split deals *easier* to catch than raw logs (70/78 vs 54/78).
  - It holds under the non-Anthropic monitor alone (DeepSeek: 0.0 on set A, -11.1 on set B).
- Kimi k3.1 at low effort: canary +8.2 → PASS; held out +10.4 (CI +3 to +19) → PASS, but narrow.
  - It holds in only 80% of bootstrap replicates.
  - Under DeepSeek alone it is +17.1 (FAIL).
  - Counting one more parse-failed pair would tip it to +15.5.
- T1-T4 all PASS. Pooled E2-E2d: 12/12 canary calls correct across 11 vendors (9 lossy flagged, 3 cleared, from 3
  vendors). Spearman 0.972 over 17 summarizers. False alarms 0/167.
- The PASS part does not hinge on Kimi: Gemini 4 Argon and Opus give 2 clear PASS cases from 2 vendors.
- Locked wording applies: "validated prospectively on both sides".
- **Safe line:** "Called in advance, the canary audit got 12 of 12 summarizers right, from 11 vendors: it flagged all 9
  lossy ones and cleared 3, two clearly (Gemini 4 Argon, Claude Opus 5.5) and one narrowly (Kimi k3.1). All 12 calls
  were confirmed on unseen deals." Do not claim the PASS side is proven in general: it rests on 3 cases, one narrow.
- Offset: the canary overstates held-out loss by +11.6 points on average over the 12 prospective summarizers.
- Cost per audit: $0.10 (Phi-4) to $5.68 (Opus).

**Result 5: a raw worker-to-worker lane on agent-written deals (E1, CONFIRMATORY; reviewed, pass with fixes).**
- The lane covers 53.6% of full-log characters.
- At the fixed threshold, Sonnet catches 51/66 on the lane, against 37/66 on luna summaries (McNemar p=0.0013;
  P2 PASS).
- Threshold-free, it matches the full log: AUC 0.944 vs 0.924 (P3 PASS).
- It needs its own threshold: 8/64 false alarms against the ≤6 bar, so P1 FAILS on false alarms only.
- At matched false alarms (controls ≤10%), Sonnet FULL 50, LUNA 46, H1 49. All differences are n.s.
- Wording: "a raw worker-to-worker lane matches full-log detection at about half the tokens, once calibrated". Do not
  call it "a fix that beats summaries at matched false alarms".

**Fixes so far.**
- A raw cross-agent message lane (H1) closes the gap on planted deals at 0.3-0.4x full-log tokens, but by
  construction: planted deals are all cross-agent.
- A second summarizer family helps on planted deals only.
- The one-line summarizer rule closes the blame chain.

## Patterns and Insights
- Failures concentrate in GPT-5.6 tiers across three oversight roles (summarizer, corrections monitor, identity check).
  This is post hoc; do not headline it.
- The large effects are on planted deals; the realistic-deal effect is small. Say this aloud.

## Lessons and Constraints
- Cut, don't hedge: any claim the reviewers weakened is dropped from the main text. L7, L10-16b and L2-08 are out.
- Never type a number into the video or report by hand; pull it from records.
- H1 "closes the gap" only by construction on planted deals; E1 tests it on agent-written deals.

## Open Questions
- E1: answered. On agent-written deals the lane matches the full log (AUC), but needs its own threshold.
- E2-E2d: answered. 12/12 canary calls correct (9 FAIL, 3 PASS from 3 vendors; Kimi narrow); rho 0.972 over 17.
