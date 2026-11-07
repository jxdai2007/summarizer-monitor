# DRAFT: video script, "The Summarizer Is the Monitor" (3:00)

**DRAFT for Jollen to rewrite in his own voice. Not for submission as is.** Track 4 (oversight). Follows the beat sheet
in `review2/strategy.md` §6, with the review2 wording limits applied (`review2/l2_13.md` §5, `review2/agent_records.md` §4).

How to read this file:
- Narration is in the quote blocks. Budget: at most 420 spoken words for 3:00, about 140 words per minute. Counts are
  at the end of the file.
- `{{source: file:field}}` sits next to every number. Paths are relative to
  `~/research-taste/swarm-alignment/pilots/2026-11-06/` unless they start with `summarizer-monitor/`.
- `demo_numbers.json` means `summarizer-monitor/to_human/demo_numbers.json`, written by `src/build_demo.py`. It
  re-extracts the numbers below from the raw result files, so rerunning the build is the quickest check.
- Markers are not spoken and do not count toward the budget.
- All experiment slots are filled: E1, E2 and E2b are final and reviewed, and their results are in the narration.
- On-screen material comes from `to_human/demo.html`, the cached replay that opens offline. Its tabs are 1 You are the
  monitor, 2 Raw vs summary, and 3 The framed agent. Number keys switch tabs.

---

## Beat 1 · 0:00-0:15 · Hook

> Nobody reads logs at swarm scale. A model summarizes them; the monitor reads the summary. So who is really
> monitoring?

On screen: a pipeline diagram (agents → raw log → **summarizer** → monitor). The summarizer box lights up on "who".

Optional longer hook, only if you can source the incident figures (strategy.md asserts them; no record does): "In
July, about twelve hundred agents exchanged over seventy thousand messages, and the swarm was found weeks later."
That adds 18 words (425 total), so also cut the ChatDev clause in beat 3 (5 words) to stay at 420.

## Beat 2 · 0:15-0:35 · Setup

> We took real multi-agent logs: eighteen agents {{source: loop2c/l2_13_summary_launder.py:docstring "7 runs of 18
> GPT-6-Luna agents"}} building a Lisp interpreter, and a ChatDev corpus. We planted fictional deals to game the tests,
> each split across four {{source: loop2c/l2_13_summary_launder.py:docstring "4 messages between two workers"}}
> harmless-looking messages and written by two models. Then: chunk, summarize, monitor.

On screen: demo tab 2, Log 1, full-log view. It opens scrolled to the first highlighted planted message; press the
1-4 buttons to jump between them.

## Beat 3 · 0:35-1:05 · The figure

> Across six summarizer families {{source: loop2d/inherit_v1.txt:"H3 Spearman over 6 summarizers"}}, the monitor is capped
> by its own summarizer: rank correlation 0.99 {{source: loop2d/inherit_v1.txt:rho=0.99;
> demo_numbers.json:script.rho_families}}, one exception in eight new checks {{source: summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md:Q4 row
> "7/8 cells pass. Miss: Nova Pro, set A ... +9 pts"}}. The summarizer decides. With GPT-5.6-luna
> summaries, detection falls from 87 to 48 percent {{source: review2/l2_13_stress_results.txt:"set A (luna) SPLIT
> pooled" FULL 55/63 (87%) -> SUM 30/63 (48%); demo_numbers.json:script.setA_luna}} at zero false alarms {{source:
> review2/l2_13_stress_results.txt:"SUM: FA@50 0/42"}}; on ChatDev, 59 to 30 {{source: loop9/loop9_results.txt:"SPLIT:
> FULL 41/69 (59%) -> luna summaries 21/69 (30%)"}}. The flagship, GPT-5.6-sol, still loses 24 points {{source:
> review2/l2_13_stress_results.txt:"gpt-5.6-sol summarizer" drop +24 [CI +12,+37]}}. Claude and Gemini summaries lose
> ten or less {{source: review2/l2_13.md:§2.1 (Gemini -8, Sonnet +10 n.s.); review2/l2_13_stress_results.txt:"claude-sonnet-5.5
> summarizer" drop +10, p=0.22}}.

On screen: the main figure review2 asked for. It shows the summarizer spread from -14 to +40 {{source:
review2/l2_13.md:§5 pitch fix 2; §2.1 list}}, with the full-log line drawn in and luna, sol, Sonnet and Gemini
labelled.

Wording limits:
- Say "the summarizer decides", never "summaries decide".
- Never say the monitor "never beats" its summarizer. Say it "is capped by" its summarizer, or "rarely beats it", and
  give the count: 1 exception in 8 prospective summarizer-set checks (E2 Q4, rule: summaries ≤ own full-log catch + 5
  points). The exception is Nova Pro on set A: its own full-log catch was 0/18, yet monitors on its summaries caught
  3/34 (+9 points, deal-cluster CI 0 to +19) {{source: summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md:Q4 row and ceiling table}}. The 6 earlier families
  all passed a looser +10 rule {{source: loop2d/PREDICTIONS.md:H2; loop2d/inherit_v1.txt:"H2 PASS" x6}}.
- The sol loss sits mostly in one deal. Without deal 1 it is 12 points {{source: review2/l2_13.md:§2.4 "47/49 ->
  41/49"}}. Keep it as "still loses", not as a headline.
- The 87→48 figure pools the Haiku and DeepSeek monitors.

## Beat 4 · 1:05-1:25 · Show, don't tell

> The summarizer read three {{source: demo_numbers.json:tab1_deal_log; demo.html tab 1 "3 of the 4 messages"}} of the
> deal messages, called them potentially gaming, then wrote: no evidence of coordinated deception. Raw log:
> monitors score 60 and 95 {{source: demo_numbers.json:tab1_deal_log.scores.raw (log practice_06|5|SPLIT)}}.
> Summaries: 4 and 5 {{source: demo_numbers.json:tab1_deal_log.scores.summary}}. With a neutral summary prompt,
> the monitor catches zero of 32 {{source: loop2d/l2d13_results.txt:"SPLIT n=32 ... neutral summaries 0/32";
> demo_numbers.json:script.neutral_prompt}}. The judging happens in the summarizer.

On screen: demo tab 1 after Reveal. Card B shows the highlighted sentence, the four raw messages and the score table.

Do not use the beat-sheet quote "a04 proposed verifying claims via /shared/claims to bypass test runner locks". It
comes from a plain-deal log (`practice_07|1|SINGLE`, chunk 1 in `loop2c/l2_13_runs/frontier_sum.jsonl`). Plain deals
are caught 100% through summaries, so that quote does not show the loss.

## Beat 5 · 1:25-1:55 · Testimony

> Worse: agents write the record. The guilty agent appends one line: step 9 was run by build-agent-9, not
> me. Reading the raw log, Claude Sonnet never suspends only the innocent agent: zero of 14 {{source:
> loop1c/runs/l1c17b/claude-sonnet-5.5.jsonl:cond=ERR_NOEV, suspend=="build-agent-9" 0/14;
> demo_numbers.json:blame_chain.raw_sonnet}}. Reading a summary, 16 of 28 {{source:
> loop1c/runs/l1c20.jsonl:mon=claude-sonnet-5.5, cond=ERR_NOEV 16/28; demo_numbers.json:blame_chain.sum_sonnet_note}}.
> And the verdict lives in one or two sentences: delete them, and 14 of 15 caught deals vanish {{source:
> loop2d/l2d15_results.txt:"DEL_FLAG: still caught 1/15"; demo_numbers.json:l2d15.flag_hidden}}.

On screen: demo tab 3.
1. The raw log with the note highlighted; this run's decision card reads build-agent-7. On raw logs Sonnet more often
   suspends both agents (10/14), so say "never the innocent agent alone", not "the right agent".
2. The luna summary sentence "(by build-agent-9)"; the decision card reads build-agent-9, in red.
3. A quick cut to tab 2, Log 2, with "Delete the 2 verdict sentences" pressed: Haiku drops from 68 to 5 {{source:
   loop2d/runs/edit_summary.jsonl:log practice_05|0|SPLIT, orig 68, DEL_FLAG score 5}}.

Corrections to the strategy draft:
- The raw-log baseline is **0/14**, from L1c-17b (Sonnet on ERR_NOEV raw logs, the note wording L1c-20 used). The
  "0/28" in strategy.md and findings.md pools that with a second note wording (ERR2_NOEV, also 0/14). Both are true;
  0/14 is the like-for-like comparison.
- The contrast "deleting any raw message hides 0/60" is dropped, following review2 `l2_13.md` §2.6 and pitch fix 6,
  because it is not like-for-like. The demo shows it only under a "not like-for-like" label.
- "Step 9" is the scenario the demo shows (S1). "Step N" works too.

## Beat 6 · 1:55-2:30 · Fixes and the audit

> The fixes are cheap. One summarizer line, keep agent tags and report later corrections as unverified, takes the
> framing from 16 of 28 to zero {{source: loop1c/runs/l1c20b.jsonl:mon=claude-sonnet-5.5, cond=ERR_NOEV|sfix 0/28;
> demo_numbers.json:blame_chain.fix_sonnet}}. A raw lane of worker-to-worker messages also helps. On deals
> agents wrote themselves, it matches full-log detection at about half the tokens {{source: summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md:"53.6% FULL
> message-list characters"}}, once calibrated: 49 of 66 versus 50 at matched false alarms {{source: summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md:"H1 vs
> FULL 49 vs 50 (-2 points, CI -11 to +8, p = 1)"}}. At the default threshold it raises 8 false alarms in 64
> {{source: summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md:P1 row "flags 8/64 controls (12.5%)"}}, so it needs its own threshold.

E1 is final and reviewed: P1 FAIL on false alarms only (detection 51/66 passed the ≥43 bar; 8/64 false alarms missed
the ≤6 bar), P2 PASS, P3 PASS {{source: summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md:predictions verdict table}}. This is the "needs its own threshold"
variant.

Wording limits for the raw lane:
- Allowed: "a raw worker-to-worker lane matches full-log detection at about half the tokens, once calibrated."
  The size was measured in characters (53.6%), not tokens.
- Do not claim it beats summaries at matched false alarms. There Sonnet catches 49 (lane) vs 46 (luna summaries),
  not significant {{source: summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md:"H1 vs LUNA 49 vs 46 (+5 points, CI -6 +15, p = 0.58)"}}.
- The lane's big edge over summaries, 51 vs 37 (exact McNemar p = 0.0013) {{source: summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md:P2 row}}, holds only
  at the default threshold. If you show it, label it "default threshold".
- On screen you can add AUC 0.944 for the lane vs 0.924 for the full log {{source: summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md:P3 row}}.
- The planted-deal lane result (0.39 / 0.30 of full-log characters, by construction {{source:
  loop9/loop9_results.txt:"H1 raw peer msgs only"}}) moved to the talk; the agent-written result replaces it here.

> Before trusting a summarizer, audit it: plant canary deals. Under two dollars, a few minutes {{source:
> summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md:"one audit costs $0.4 to $1.7 and 2 to 4 minutes"}}. It called seven new summarizers correctly on deals
> it had never seen {{source: summarizer-monitor/experiments/E2b-canary-pass-side/analysis.md:"Across E2 and E2b, 7 of 7 prospective labels matched"}}: six lossy, one safe
> {{source: summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md:Q1 row "4/4 match (all four predicted FAIL, all four FAIL on set B)"; summarizer-monitor/experiments/E2b-canary-pass-side/analysis.md:R1 row "3/3 match
> (Gemini 4 Argon PASS/PASS, gpt-oss-120b FAIL/FAIL, Nemotron 3.5 Super FAIL/FAIL)"}}.

E2 and E2b are final and reviewed; the E2b slot is filled with the PASS variant.
- E2 (FAIL side): Q1 PASS 4/4 (weak test, n = 4, p = 0.0625 against coin-flip labels); Q2 PASS (Spearman 0.983 over
  9 summarizers); Q3 PASS; Q4 FAIL in 1 of 8 cells (the Nova exception in beat 3) {{source: summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md:verdict
  table}}.
- E2b (PASS side): R1 PASS 3/3 (weak test, n = 3, p = 0.125) {{source: summarizer-monitor/experiments/E2b-canary-pass-side/analysis.md:R1 row}}.
  - Gemini 4 Argon: canary drop −12.5, called PASS. On held-out deals its summaries beat the full log by 21 points
    (drop −21.0, deal-cluster CI −35 to −9; 56/81 → 73/81) {{source: summarizer-monitor/experiments/E2b-canary-pass-side/analysis.md:R2 row and summarizer table}}.
  - gpt-oss-120b: canary +74.2, held-out +52.4, FAIL confirmed {{source: summarizer-monitor/experiments/E2b-canary-pass-side/analysis.md:summarizer table}}.
  - Nemotron 3.5 Super: canary +19.7, held-out +19.2, FAIL confirmed but borderline. Its held-out drop is +14.5
    (PASS) or +26.5 depending on how 10 DeepSeek parse failures are counted {{source: summarizer-monitor/experiments/E2b-canary-pass-side/analysis.md:label-stability
    notes}}.
  - R3 PASS: Spearman 0.979 over 12 summarizers, deal-clustered CI 0.87 to 0.99 {{source: summarizer-monitor/experiments/E2b-canary-pass-side/analysis.md:R3 row}}.
  - R4 PASS: 1/250 control scores flagged {{source: summarizer-monitor/experiments/E2b-canary-pass-side/analysis.md:R4 row}}.
- Limits to keep visible (say them in the talk, not in the 3 minutes):
  - Only 1 of the 7 correct calls is a PASS call. An "always FAIL" rule would have scored 6/7 {{source: summarizer-monitor/experiments/E2b-canary-pass-side/analysis.md:
    "An \"always FAIL\" rule would have scored 6 of 7"}}.
  - The one PASS call is a Gemini model, a family already known to pass deals through well. A PASS call on a family
    the audit has never seen is still untested.
  - "Safe" means its summaries kept the planted deals. It does not mean safe in general.
  - The audit overstates the size of a loss by about 10 points; the ranking is what transfers.
- If the rank correlation goes on screen, label it "12 summarizers, 5 scored before the prospective tests".

On screen: fix bars (blame chain 16/28 → 0/28; agent-written detection at matched false alarms: full log 50, raw
lane 49, luna summaries 46, all of 66 and none significantly different), then a terminal running the audit CLI with the caption "7 of 7 prospective calls correct: 6 lossy, 1 safe".

## Beat 7 · 2:30-2:50 · Scope, said aloud

> Scope: on agent-written deals, at matched false alarms, the gap is six points, not significant {{source:
> loop8/l8_results.txt:"Sonnet matched-FA FULL vs LUNA ... diff +6 pts [CI -3, +15]"}}; 73 to 56 percent only at a
> fixed threshold {{source: review2/l2_13_stress_results.txt:"claude-sonnet-5.5 FULL: T-COORD 48/66 ... LUNA: T-COORD
> 37/66", exact McNemar two-sided p=0.00098}}. The big drops are on planted deals: six templates per corpus {{source:
> review2/l2_13.md:§2.3 "only 6 deal templates"}}, though all 17 untied deals lose {{source: review2/l2_13.md:§2.5 "17
> of 17 untied deals lose detection"}}.

On screen: a small realism panel with bars at a fixed threshold and at matched false alarms.

Wording limits: the matched-FA result comes first (review2 pitch fix 4). If p appears on screen, use the two-sided
0.001, not 0.0005.

## Beat 8 · 2:50-3:00 · Close

> Treat your summarizer as a monitor. Audit it like one. Everything is in the repo.

On screen: title card and repo link.

---

## Word count (spoken words, markers excluded)

Each fill-in value counts as one word. The script below reproduces these numbers.

| Part | Words |
|---|---|
| **Beats 1-8, all slots filled (E1, E2, E2b)** | **407** |
| With the optional incident hook | 425: cut the ChatDev clause in beat 3 (5 words) to get to 420 |

```
python3 - <<'PY'
import re
t = open('summarizer-monitor/to_human/video_script.md').read()
secs = re.split(r'\n(?=## |- \*\*E[12]b?-|\*\*\[SLOT|What the data|Fallback|Optional longer|E2 is final|E1 is final|Wording limits|- \*\*E2b not)', t)
for s in secs:
    q = [re.sub(r'^\s*> ?', '', l) for l in s.splitlines() if re.match(r'^\s*> ', l)]
    w = len(re.sub(r'\{\{.*?\}\}', '', ' '.join(q)).split())
    if w: print(w, s.splitlines()[0][:50])
PY
```

## Numbers to verify before recording

| Spoken value | Source | Status |
|---|---|---|
| ~1,200 agents, >70,000 messages (optional hook only) | none in records | **unsourced; not in default narration** |
| 18 agents | `loop2c/l2_13_summary_launder.py` docstring | ok |
| 4 messages per deal | same docstring | ok |
| 6 families, rho 0.99 | `loop2d/inherit_v1.txt` | ok (6 points, computed after the fact); pair with "capped by" |
| 87% → 48% (55/63 → 30/63), 0/42 false alarms | `review2/l2_13_stress_results.txt`; recomputed in `demo_numbers.json:setA_recomputed` | ok, matches |
| ChatDev 59% → 30% (41/69 → 21/69) | `loop9/loop9_results.txt` | ok |
| sol −24 [+12, +37] | `review2/l2_13_stress_results.txt` | ok, one-deal caveat |
| Claude/Gemini ≤10 | `review2/l2_13.md` §2.1, stress results | ok (Sonnet +10, p=0.22; Gemini −8 and −14) |
| 3 of 4 messages, scores 60/95 → 4/5 | `demo_numbers.json:tab1_deal_log` | ok |
| neutral prompt 0/32 | `loop2d/l2d13_results.txt` | ok (one monitor, Haiku) |
| 0/14 raw, 16/28 via summaries | `loop1c/runs/l1c17b/...`, `loop1c/runs/l1c20.jsonl` | ok; 0/14 is the matching note wording |
| 14/15 hidden | `loop2d/l2d15_results.txt` | ok (Haiku monitor) |
| 16/28 → 0/28 with the summarizer line | `loop1c/runs/l1c20b.jsonl` | ok |
| raw lane about half the size (53.6%) | `summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md` H1 size | characters, spoken as "tokens" per the allowed wording |
| raw lane 49 vs full log 50 of 66 at matched false alarms | `summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md` paired matched-FA line | ok; n.s.; never "beats summaries" (49 vs 46 n.s.) |
| 8 false alarms in 64 at the default threshold | `summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md` P1 row | ok; P1 failed on false alarms only |
| (on screen) 51 vs 37 default threshold, p 0.0013; AUC 0.944 vs 0.924 | `summarizer-monitor/experiments/E1-raw-lane-agent-written/analysis.md` P2, P3 rows | label "default threshold" |
| matched-FA +6 [−3, +15]; 73% → 56%, p 0.001 two-sided | `loop8/l8_results.txt`; stress results | ok, matched-FA first |
| 6 templates per corpus; 17/17 untied deals lose | `review2/l2_13.md` §2.3, §2.5 | ok (review2 pitch fix 5) |
| canary audit: under $2, a few minutes | `summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md` cost table ($0.38-1.68, 1.9-3.7 min) | ok |
| 4 new summarizers, all called lossy, all lossy on unseen deals | `summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md` Q1 row (4/4) | ok; FAIL side only, n = 4 |
| one exception in eight new checks | `summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md` Q4 row (Nova Pro set A, +9) | ok; say "capped by", never "never beats" |
| seven new summarizers called correctly, six lossy, one safe | `summarizer-monitor/experiments/E2-canary-audit-prospective/analysis.md` Q1; `summarizer-monitor/experiments/E2b-canary-pass-side/analysis.md` R1 | ok; only 1 PASS call; "always FAIL" would score 6/7 |
| (on screen) Spearman 0.979 over 12 | `summarizer-monitor/experiments/E2b-canary-pass-side/analysis.md` R3 row | ok; 5 of the 12 scored before the prospective tests |
