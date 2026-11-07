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
- Claude and Gemini summaries lose 0-10 points (n.s.). It is the summarizer, not summarization per se.
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
- False alarms were 0/42 in every cell. The canary overstates held-out loss by about 10 points.
- Cost: $0.38-1.68 and 2-4 minutes per audit.
- Caveat: all 4 were canary-FAIL, so only the warning side was tested. E2b (locked bec2a9b) tests the PASS side.
- Ceiling exception (prospective Q4): monitors on Nova summaries beat Nova's own full-log catch by 9 points on set A
  (bar was +5); the other 7/8 cells held. Wording is now "capped by / rarely beats", never "never beats".
- Deviation: Kimi k3.1-pro was swapped out for cost and leaked reasoning text before its scores were read. Its partial,
  exploratory drops were +12.5 and +10, so it was the only family heading for PASS (see the E2 analysis).

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
- E2: answered for the warning side (4/4, rho 0.983). E2b: is the PASS side right too?
