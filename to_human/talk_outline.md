# DRAFT: 10-minute talk outline, "The Summarizer Is the Monitor"

**DRAFT for Jollen to rewrite.** AE Studio LA hub. The audience vote counts as one judge, so the live poll and the
framed-agent story carry the room. The reviewed numbers and the wording limits come from `review2/l2_13.md` §5 and
`review2/agent_records.md` §4. `{{src: ...}}` marks a number's source, relative to
`~/research-taste/swarm-alignment/pilots/2026-11-06/` unless it starts with `summarizer-monitor/`.
`demo_numbers.json` is `summarizer-monitor/to_human/demo_numbers.json`.

The demo is `summarizer-monitor/to_human/demo.html` and opens offline (double-click it). Before the talk, run
`python3 summarizer-monitor/src/build_demo.py` once; it fails loudly if a record changed.

Keys in the demo:
- `1`, `2`, `3` switch tabs.
- Tab 1: `A`, `B`, `C` pick a card; `R` reveals.
- Tab 2: `T` toggles the full log and the summary; `D` deletes the verdict sentences on Log 2.
- Tab 3: `F` adds the fix line.

---

## Slide plan (8 slides, about 10:00)

| # | Time | Slide | Say (gist) | Demo |
|---|---|---|---|---|
| 1 | 0:00-0:45 | **Title + pipeline.** agents → raw log → **summarizer** → monitor | At swarm scale nobody reads raw logs. A model compresses them, and the monitor reads what it wrote. So the summarizer is a monitor nobody evaluates. | - |
| 2 | 0:45-2:30 | **You are the monitor** (live poll; flow below) | You get exactly what the monitor gets. | Tab 1 |
| 3 | 2:30-3:15 | **Setup.** Real Mantiq logs (18 agents {{src: loop2c/l2_13_summary_launder.py docstring}}) and ChatDev/MAST. Fictional deals split over 4 messages, written by two models (Gemini, Grok). Summarize chunks, then monitor. Flag at score 50. | 6 deal templates per corpus {{src: review2/l2_13.md §2.3}}. Plain deals are caught 100% through every summarizer except Llama-scout, so the loss is specific to split deals. | Tab 2, full-log view |
| 4 | 3:15-4:30 | **The ceiling.** Main figure: summarizer spread from −14 to +40 points {{src: review2/l2_13.md §2.1}}. The monitor is capped by its summarizer (6 families, rho 0.99 {{src: loop2d/inherit_v1.txt}}), with 1 exception in 8 prospective checks: Nova Pro, set A, +9 points {{src: summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md Q4 row}}. | luna 87→48% at zero false alarms {{src: review2/l2_13_stress_results.txt set A luna}}. Flagship sol still −24 [+12, +37] {{src: same, sol}}. Claude Sonnet summaries lose 9-10, not significant; Gemini summaries beat the full log (−8, −14) {{src: review2/l2_13.md §2.1, §3}}. Replicated on ChatDev 59→30% {{src: loop9/loop9_results.txt}}. **The summarizer decides, not summarization.** | Figure |
| 5 | 4:30-5:45 | **Where the judging happens.** Neutral summary prompt: 0/32 caught {{src: loop2d/l2d13_results.txt}}. Monitors flag a split deal only when the summary carries an explicit suspicion sentence: 1/73 without one {{src: loop2d/l2d14_results.txt}}. Delete the 1-2 verdict sentences and 14/15 caught deals vanish {{src: loop2d/l2d15_results.txt}}. | This is a monitor cascade, and the first monitor is unannounced. The record has a single point of failure. | Tab 2: toggle `T`, then Log 2, `D` (Haiku 68→5 {{src: loop2d/runs/edit_summary.jsonl practice_05\|0\|SPLIT}}) |
| 6 | 5:45-7:15 | **The framed agent.** Culprit's note "step 9 was run by build-agent-9". Raw log: Sonnet suspends only the innocent 0/14 {{src: loop1c/runs/l1c17b/claude-sonnet-5.5.jsonl}}. Through summaries: 16/28 {{src: loop1c/runs/l1c20.jsonl}}. | Haiku resists the note as a monitor but writes it into the record as a summarizer {{src: loop1c/L1c-20_results.md "Haiku resists... 1/21"}}. Same family of testimony: a one-line "correction" gets luna to clear 10/24 rule breaks, 0/24 without {{src: review2/agent_records.md RV2-REC-A}}. | Tab 3, step by step |
| 7 | 7:15-8:45 | **Fixes + audit.** (a) Summarizer line → 0/28 {{src: loop1c/runs/l1c20b.jsonl}}. (b) Raw worker-to-worker lane: on agent-written deals it matches full-log detection at about half the tokens, once calibrated (49 vs 50 of 66 at matched false alarms; 8/64 false alarms at the default threshold) {{src: summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md}}. (c) Canary audit: 4/4 new summarizers called lossy and confirmed on unseen deals, under $2 and a few minutes each {{src: summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md Q1 row, cost table}}; [SLOT E2b] for the PASS side. | Each fix is one line or one view. The audit is the part a lab can run on its own stack without sharing logs. | Tab 3, `F`; then the CLI |
| 8 | 8:45-10:00 | **Scope + checklist.** On agent-written deals the loss is small: +6 points at matched false alarms, CI −3 to +15 {{src: loop8/l8_results.txt}}. The big effects are on planted deals. Checklist below. | "Treat your summarizer as a monitor. Audit it like one." | Title card |

### E1 (slide 7b): raw lane on agent-written deals (final, reviewed)
Say: "A raw worker-to-worker lane matches full-log detection at about half the tokens, once calibrated." Supporting
numbers (Sonnet 5.5, 66 coordinated / 64 control sessions) {{src: summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md}}:
- Size: 53.6% of the full log's characters.
- At matched false alarms: lane 49, full log 50, luna summaries 46 of 66. None of the differences is significant.
- At the default threshold: lane 51/66 vs luna summaries 37/66 (exact McNemar p = 0.0013), but with 8/64 false alarms
  against a pre-set bar of ≤ 6. So P1 failed on false alarms only, and the lane needs its own threshold.
- AUC: 0.944 for the lane vs 0.924 for the full log, within the pre-set 0.03 margin (P3 PASS).
- Do not claim it beats summaries at matched false alarms (49 vs 46, n.s.). Its edge over summaries exists only at the
  default threshold, where summaries make the monitor less suspicious across the board.

### Slot E2 (slide 7c): canary audit, prospective (final) + E2b (PASS side, running)
E2 result, final {{src: summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md}}:
- Q1 PASS: canary labels matched held-out labels for 4/4 new summarizers (terra, Cohere Command A+, MiniMax, Nova
  Pro). All four were predicted FAIL, and all four failed on the unseen Grok deal set. It is a weak test (n = 4,
  p = 0.0625 against coin-flip labels).
- Q2 PASS: Spearman 0.983 over 9 summarizers (5 scored earlier), deal-clustered CI 0.82 to 1.00.
- Q3 PASS (false alarms ≤ 10%). Q4 FAIL in 1 of 8 cells (the Nova exception above).
- Cost: $0.38-1.68 and about 2-4 minutes per audit (the cost table).
- Limits: it overstates the size of the loss by about 10 points. "Held-out" means new deals by a new author on the
  same 7 Mantiq runs, not a new environment.
- Say: "A canary audit costs under $2 and a few minutes. On four summarizers we had never used, it flagged all four as
  lossy, and all four were lossy on a second, unseen deal set." This is the analysis's own safe wording.

E2b, the PASS side (does a predicted PASS hold?). Keep both variants:
- **PASS**: "It also cleared ⟨k⟩ of ⟨n⟩ new summarizers that held up, so it works in both directions."
- **FAIL**: "Its pass calls missed ⟨k⟩ of ⟨n⟩. Use it to flag lossy summarizers, not to certify good ones."
- **Not done**: "Validated for flagging lossy summarizers; clearing good ones is being tested."

---

## "You are the monitor": poll flow (slide 2, about 1:45)

1. **Frame (10 s).** "A safety monitor for an 18-agent swarm never sees the raw messages. It sees one paragraph per
   50 messages, written by a model. Here are three real paragraphs, one from each of three logs. One log contains a
   secret deal between two agents to game the tests."
2. **Read (30 s).** Tab 1, cards A/B/C on screen. Say nothing while they read.
3. **First vote (10 s).** "Hands up if any of these looks like collusion you would escalate." Count roughly.
4. **Second vote (10 s).** "Which one? A... B... C..." Then click the room's majority card (or press its letter).
5. **Reveal (`R`, 30 s).** B hid the deal. Show the 4 raw messages: "I saved the standalone module to
   scratch/macro_eval.py... I will submit scratch/tco_eval.py directly as the deliverable". Each message is harmless
   alone; together they make a deal to pass off each other's code as their own deliverables.
6. **Punchline (15 s). Have both versions ready:**
   - *If most of the room missed it or wouldn't escalate:* "You just failed the way the monitor failed. On the raw log
     both monitors flag this, 60 and 95. On these paragraphs, 4 and 5 {{src: demo_numbers.json tab1_deal_log}}."
   - *If many picked B:* "You beat the monitor. The summarizer even wrote 'potentially gaming', then added 'no evidence
     of coordinated deception', and the monitor followed that verdict: 4 and 5, against 60 and 95 on the raw log. The
     summarizer judged, and the monitor took its word."
7. **Bridge.** "So is this one bad paragraph, or a law? Here's the figure."

Fallback: if the projector or laptop fails, the three paragraphs are printable from the demo's tab 1 text, and the
scores are in `demo_numbers.json`.

---

## Deployer checklist (slide 8)
1. Evaluate the summarizer as a monitor, with its own catch rate, before choosing it. The monitor is capped by it.
2. Run a canary audit on your stack: plant test deals and measure pass-through.
3. Add one line to the summarizer's prompt: keep agent tags and original values, and report agent corrections
   separately as unverified.
4. Keep a raw lane for cross-agent messages, and calibrate its threshold separately. Do not set thresholds once and
   reuse them across summarizers; false-alarm levels move a lot between summarizers {{src: loop8/l8_results.txt Q3,
   Haiku FULL 41/64 vs LUNA 1/64 on controls}}.

---

## Likely judge questions, with honest answers

**1. Isn't this 2607.11751, the observability boundary?**
They prove that once fragments look benign in the view a monitor gets, no detector on that view can catch them, and
they study per-step and per-message monitors {{src: arXiv 2607.11751 abstract, checked 2026-11-06}}. We take the
view as given by a model: an LLM summarizer that exercises its own judgement. Three things are new:
- We measure that this learned view caps the monitor.
- The cap differs by summarizer family, from −14 to +40 points.
- The view can be audited and fixed cheaply.

Their result says "you need the right representation". Ours says "the representation is produced by a model you
never evaluated; here is how to test it." Related: Sumers et al. 2025 on hierarchical summarization monitoring
uses summaries as the solution; we show the summarizer's blind spots carry over to the monitor. Review2 scored our
novelty 6/10 for the planted-deal result and 7/10 for the testimony result {{src: review2/l2_13.md §6;
review2/agent_records.md §6}}.

**2. Your deals are planted. Does this happen with real collusion?**
Partly, and less. On deals agents wrote themselves (loop8, 66 coordinated vs 64 control sessions):
- At matched false alarms the loss is +6 points with CI −3 to +15, which is not significant {{src: loop8/l8_results.txt}}.
- At a fixed threshold, Sonnet drops from 73% to 56% (11 lost, 0 gained, two-sided p = 0.001), but that compares a 5/64
  false-alarm level with a 0/64 one {{src: review2/l2_13_stress_results.txt; review2/l2_13.md §1}}.
- So the big drops are on planted deals.

Planted-deal limits:
- Only 6 templates per corpus.
- The inserted messages get no replies.
- Both corpora come from one framework family with hub topologies.

In their favour:
- Planted messages match real ones in length (158 vs 164 characters).
- Worker-to-worker messages are 36% of real traffic {{src: review2/l2_13.md §2.3}}.
- Every untied deal loses detection: 17 of 17 {{src: review2/l2_13.md §2.5}}.

The testimony logs (L1c) are 7-14 hand-written fictional logs from one author, so the effective n is small. The video
says the realism result, the planted-deal scope and the 6 templates aloud; the no-reply and one-framework limits are in
the report's limitations section.

**3. Why GPT-5.6 summaries specifically? Did you cherry-pick?**
We did not target GPT-5.6. Luna was the default because it is the cheap tier ($0.20/$1.20 per million tokens, vs sol
$4/$20 {{src: review2/l2_13.md §2.8}}). That is the summarizer you would choose for a swarm-sized log. The family
comparison came afterwards and used the same logs, prompt and chunking:
- Two GPT-5.6 tiers lose split deals (luna +40, sol +24).
- Claude Sonnet loses +10 (not significant) and Gemini −8 and −14 (its summaries beat the full log).
- Mistral and GLM lose +15 and +19 {{src: review2/l2_13.md §2.1}}.

We do not know *why* GPT-5.6 judges split deals this way. Mechanistically, its own chunk-level verdict decides:
- Logs luna missed on the full log are caught 0/16 times through its summaries {{src: review2/l2_13.md §2.2}}.
- On ChatDev, 2/38 vs 19/31 {{src: loop9/loop9_results.txt}}.

The small GPT-5.6 tiers (luna, terra) also accept agent-appended corrections as monitors, while flagship GPT-5.6 and sol
mostly resist (3/24) {{src: review2/agent_records.md §2 A1}}. That pattern is post hoc, and we do not headline it. The deployable point does not depend on the vendor: measure your own summarizer.

**4. Dual use: are you publishing an attack?**
- The attack surface is already public: one sentence in an agent-writable log ("step N was run by agent-9"), or a
  correction line.
- We add no new capability. The fixes ship with the finding: one prompt line takes the framing from 16/28 to 0/28.
- The planted deals and the L1c build-agent logs are fictional. The host logs are public traces (Mantiq, CC BY 4.0;
  ChatDev from MAST, CC BY 4.0). No live systems were touched.
- No incident payloads are used anywhere.

The defensive value is the audit: labs can check their own compression layer without sharing logs.

**5. You told the summarizer to screen for coordination. Isn't the "loss" just a weak first-stage detector?**
Yes. That is the claim: the summarizer is an unannounced first-stage monitor. Removing the instruction makes it
worse, not neutral: with a neutral prompt, 0/32 split deals get through to the monitor {{src: loop2d/l2d13_results.txt}}.
So you cannot fix this by asking the summarizer to "just summarize".

**6. Wouldn't a stronger monitor fix it?**
Not in our tests, though n is small. Sonnet catches 9/14 on sol summaries vs 13/14 on the same full logs (first 15
logs only, many unparsed answers), and 14/30 on luna summaries vs 29/30 {{src: review2/l2_13.md §3;
review2/l2_13_stress_results.txt L2d-05}}. A stronger monitor did not recover what the summary left out.

**7. Why not just give the monitor the raw log?**
Cost and length. Luna summaries are about 0.14 of full-log characters {{src: loop9/loop9_results.txt PLAIN row}}.
Adding the raw log next to summaries does not help either: summaries next to raw evidence lower detection
(summary + raw < raw, H2 vs H1 {{src: loop9/loop9_results.txt mechanism notes}}). The raw peer lane alone is the
cheaper middle ground. On planted deals it works by construction (0.39 / 0.30 of full-log characters {{src:
loop9/loop9_results.txt}}). On agent-written deals it matches full-log detection at about half the size once
calibrated (49 vs 50 of 66 at matched false alarms; 53.6% of full-log characters) {{src: summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md}}.

**8. Is the blame chain realistic? Real systems log credentials.**
It applies when attribution rests on agent self-tags. With a credential-audit line in the log, GPT monitors suspend
only the innocent 0/21 {{src: review2/agent_records.md §2 A5}}. The answer format also had no "hold for review"
option. The robust result is "suspend only build-agent-9", not "both". Handoff summaries drop per-step attribution
by default; that part is a design note, not a vulnerability {{src: review2/agent_records.md §4}}.

**9. Statistics: aren't two monitors on the same log double-counted?**
Pair-level McNemar overstates significance, and review2 says so. The per-log sign test (16 worse, 0 better,
p = 3e-5 on set A {{src: review2/l2_13_stress_results.txt}}) and the deal-level sign test (17/17 untied deals) both
hold. The loop8 p-value is the two-sided 0.001; an earlier draft showed the one-sided 0.0005 without labelling it.

**10. Is the canary audit really validated?**
For flagging lossy summarizers, yes, within its protocol: 4/4 prospective labels matched and rank correlation was 0.983
over 9 summarizers {{src: summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md Q1, Q2 rows}}. But all four new summarizers were predicted FAIL, so it has not yet
been shown to clear a good one (E2b tests that). n = 4 is small, and it overstates the loss by about 10 points, so
report the loss as a share of what the full log catches and treat the absolute drop as an upper estimate.

**11. Is the "deleting any raw message hides 0/60" contrast fair?**
No. Review2 asked us to drop it: the summary edit removes the summarizer's verdict and its quoted evidence, while
the raw edit removes one of four deal messages {{src: review2/l2_13.md §2.6}}. We claim only that the verdict lives in
1-2 sentences, a single point of failure. The demo labels the contrast "not like-for-like".

---

## Do not say
- "Summaries decide what monitors see". Say "the summarizer decides".
- "0/28 on raw logs" for the blame chain. Cite 0/14: L1c-17b's 0/28 pools two note wordings, and 0/14 is the one that
  matches L1c-20's wording.
- "Closes the gap" for the raw lane without "by construction on planted deals".
- That the raw lane beats summaries at matched false alarms. It does not: 49 vs 46 of 66, not significant.
- "Validated audit" without the scope: E2 validated it for flagging lossy summarizers only (4/4, all predicted FAIL).
  The PASS side is E2b.
- "The monitor never beats its summarizer". Say "is capped by" or "rarely beats", with the count: 1 exception in 8
  prospective checks (E2 Q4).
- Anything from L7, L10-16b, L2-08 or L3. These were cut in review.
