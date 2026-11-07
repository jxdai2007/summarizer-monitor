# The Summarizer Is the Monitor

Swarm Alignment Hackathon, track 4 (oversight). Every number here is copied from
[`findings.md`](findings.md) and the linked analysis files; nothing is typed in from memory.

**Thesis.** At swarm scale, monitors read LLM-written summaries rather than raw logs, so the summarizer
becomes an unannounced first monitor. What the downstream monitor can catch is capped by what the
summarizer keeps and frames as suspicious.

## Headline results

- **Result 1 - the ceiling.** Planted split deals (4 innocuous-looking messages) in real Mantiq swarm
  logs, plus a second corpus (ChatDev/MAST). Across 6 summarizer families the monitor is capped by its
  summarizer alone (rho 0.99). Prospectively (E2) the cap held in 7/8 cells; one cell exceeded it by 9
  points, so the claim reads "capped by / rarely beats". GPT-5.6 summaries lose 24-40 points at zero
  false alarms (luna on Gemini-written deals 55/63 -> 30/63; luna on Grok-written deals 55/80 -> 25/80;
  ChatDev 41/69 -> 21/69; flagship sol 89% -> 65%). Claude Sonnet summaries lose about 10 points (n.s.)
  and Gemini summaries lose none - they beat the full log by 8-14 points. With a neutral summary prompt
  monitors catch 0/32 split deals: the judging happens in the summarizer.
  -> [`data/ceiling_planted.csv`](data/ceiling_planted.csv), [`data/ceiling_by_deal.csv`](data/ceiling_by_deal.csv)
- **Result 2 - realism.** On deals agents wrote themselves (loop 8, 66 coordinated vs 64 control
  sessions) Sonnet drops 73% -> 56% at a fixed threshold (11 lost, 0 gained, two-sided p=0.001). At
  matched false alarms the loss is +6 points (CI -3 to +15), n.s. Haiku's drop there is calibration
  (AUC 0.83 full vs 0.91 summaries). Summarizer choice swings false-alarm levels a lot, so thresholds do
  not transfer across summarizers. -> [`data/realism_agent_written.csv`](data/realism_agent_written.csv)
- **Result 3 - testimony laundered into the record.** A one-line agent "correction" gets GPT-5.6-luna to
  clear 10/24 real rule breaks on realistic ~1,000-word logs (0/24 without); Claude and Gemini clear
  0-1/24. A culprit's "step 4 was run by agent-9" note makes Sonnet suspend only the innocent agent
  16/28 times through summaries, vs never on raw logs (0/14 with the same note wording, like-for-like).
  One summarizer line ("report which agent each step is tagged with; report later corrections separately
  as unverified") brings it to 0/28. Deleting 1-2 summary sentences hides 14/15 caught deals; deleting
  any single raw message hides 0/60 (not like-for-like, so the video and slides drop it).
  -> [`data/testimony.csv`](data/testimony.csv), [`data/fix_designs.csv`](data/fix_designs.csv)
- **Result 4 - a canary audit predicts summary loss for new summarizers.** CONFIRMATORY, two-stage lock
  (E2). 4 new summarizer families (GPT-5.6-terra, Cohere Command A+, MiniMax M3.1 Flash, Amazon Nova
  Pro); their canary drop on set A was committed as a PASS/FAIL prediction before set B ran. Labels
  matched 4/4; Spearman 0.983 over 9 summarizers (deal-clustered CI 0.82-1.00); false alarms 0/42 in
  every cell; the canary overstates held-out loss by about 10 points; cost $0.38-1.68 and 2-4 minutes
  per audit. All 4 were canary-FAIL, so only the warning side was tested. Ceiling exception (prospective
  Q4): monitors on Nova summaries beat Nova's own full-log catch by 9 points on set A (bar was +5); the
  other 7/8 cells held.
  -> [`experiments/E2-canary-audit-prospective/analysis.md`](experiments/E2-canary-audit-prospective/analysis.md)
- **Result 4b - the audit's PASS side.** CONFIRMATORY, two-stage lock; reviewed, pass with fixes (E2b).
  3 more summarizers by the fixed order rule (Gemini 4 Argon, gpt-oss-120b, Nemotron 3.5 Super); labels
  matched 3/3 (Gemini canary -12.5 -> PASS, held-out -21.0 -> PASS; gpt-oss +74.2 -> FAIL, held-out
  +52.4 -> FAIL; Nemotron +19.7 -> FAIL, held-out +19.2 -> FAIL, but borderline). Spearman 0.979 over 12
  summarizers (CI 0.87-0.99); false alarms 1/250. Across E2 and E2b the canary calls 7/7 correctly, but
  only 1 of those calls is a PASS: validated on both sides, the PASS side with one case.
  -> [`experiments/E2b-canary-pass-side/analysis.md`](experiments/E2b-canary-pass-side/analysis.md)
- **Result 4c - more PASS-side attempts.** CONFIRMATORY; reviewed, PASS (E2c). Mistral Medium 3.5, Phi-4 and
  Llama 4 Maverick were all canary-FAIL and all FAIL held-out. Pooled over E2-E2c, labels match 10/10 across
  9 vendors, but there is still only 1 PASS case (S2 not reached, S3 failed). Spearman 0.967 over 15
  summarizers. Safe wording: the audit flagged every lossy summarizer we tested in advance (9/9, 9 vendors,
  all confirmed on unseen deals); one PASS call held; the PASS side is preliminary.
  -> [`experiments/E2c-canary-pass-side-2/analysis.md`](experiments/E2c-canary-pass-side-2/analysis.md).
  E2d (two likely-PASS summarizers) is running: [`experiments/E2d-canary-pass-side-3/protocol.md`](experiments/E2d-canary-pass-side-3/protocol.md)
- **Result 5 - a raw worker-to-worker lane on agent-written deals.** CONFIRMATORY; reviewed, pass with
  fixes (E1). The lane covers 53.6% of full-log characters. At the fixed threshold Sonnet catches 51/66
  on the lane against 37/66 on luna summaries (McNemar p=0.0013; P2 PASS). Threshold-free, it matches the
  full log: AUC 0.944 vs 0.924 (P3 PASS). It needs its own threshold: 8/64 false alarms against the <=6
  bar, so P1 FAILS on false alarms only. At matched false alarms (controls <=10%), Sonnet FULL 50, LUNA
  46, H1 49; all differences are n.s. Wording: a raw worker-to-worker lane matches full-log detection at
  about half the tokens, once calibrated.
  -> [`experiments/E1-raw-lane-agent-written/analysis.md`](experiments/E1-raw-lane-agent-written/analysis.md), [`data/E1_scores.csv`](data/E1_scores.csv)
- **Fixes so far.** A raw cross-agent message lane (H1) closes the gap on planted deals at 0.3-0.4x
  full-log tokens, but by construction: planted deals are all cross-agent. A second summarizer family
  helps on planted deals only. The one-line summarizer rule closes the blame chain.
  -> [`data/fix_designs.csv`](data/fix_designs.csv), figure [`to_human/fig_main.png`](to_human/fig_main.png)

## Repo layout

| Path | What it holds |
|---|---|
| `src/build_data.py` | rebuilds `data/*.csv` from the raw pilot records (needs the records root, see Reproduce) |
| `src/fig_main.py` | the 3-panel main figure -> `to_human/fig_main.png` / `.pdf` |
| `src/fig_panels.py` | per-panel PNGs for the video at 1080p -> `to_human/panels/` (ceiling, realism, testimony, pipeline, canary) plus `panel_numbers.json` |
| `src/build_slides.py` | the offline slide deck -> `to_human/slides.html` (reruns `fig_panels.py`; arrow keys, N for speaker notes) |
| `src/build_demo.py`, `src/build_progress.py` | cached interactive demo (`to_human/demo.html`, `to_human/demo_numbers.json`) and progress page |
| `src/summary_audit/` | the `summary-audit` CLI package: `cli.py`, `audit.py`, `logs.py` (formats + canaries), `llm.py`, `prompts.py`, `report.py`, and `data/` (vendored corpora, planted deal templates, sample log) |
| `data/` | consolidated CSVs; [`data/README.md`](data/README.md) maps every column to its raw source file |
| `experiments/` | `E1-raw-lane-agent-written`, `E2-canary-audit-prospective`, `E2b-canary-pass-side`, `E2c-canary-pass-side-2` (protocol + analysis + code + raw results), `E2d-canary-pass-side-3` (running) |
| `to_human/` | `slides.html`, `panels/`, `demo.html`, `fig_main.png`, `talk_outline.md`, `video_script.md`, `progress.html` |
| `tests/` | `test_summary_audit.py`, 5 tests: offline dry run end to end, canary planting determinism, prompt parity with the original Mantiq text, chunking and format adapters, `convert` round-trip |
| `paper/`, `literature/` | draft report (numbers injected from generated LaTeX macros) and the verified related-work survey |
| `findings.md` | the single reviewed source for result wording |

## Reproduce

Python: `/Users/macstudio/projects/swarm-alignment/.venv/bin/python` (written `python` below). Every
command in this section was run on 2026-11-06 and finished with exit 0.

```bash
cd summarizer-monitor

python src/build_data.py         # rebuilds data/*.csv from the raw pilot records; the rebuilt CSVs matched the committed ones
python src/fig_main.py           # -> to_human/fig_main.png / .pdf
python src/fig_panels.py         # -> to_human/panels/*.png + panel_numbers.json (video panels)
python src/build_slides.py       # -> to_human/slides.html (reruns fig_panels.py first)
python src/build_demo.py         # -> to_human/demo.html, to_human/demo_numbers.json
python src/build_progress.py     # -> to_human/progress.html
```

`src/build_data.py:21` hard-codes the pilot records root (`~/research-taste/swarm-alignment/pilots/2026-11-06/`)
and `src/build_data.py:363` imports `loop9/l9_table.py` from it, so that folder has to exist; nothing in
`data/` is hand-edited. `fig_panels.py` and `build_slides.py` read only `data/*.csv`, the build outputs of
`build_demo.py`, `findings.md` (to decide which canary batches are reviewed) and two quoted lines in the E1/E2
analysis files; they type in no numbers.

The `summary-audit` CLI has the subcommands `run` and `convert`. The offline dry run needs no key and no
network, and has to be started from `src/`:

```bash
cd summarizer-monitor/src
python -m summary_audit --help
python -m summary_audit run --dry-run --format mantiq --run practice_07 --n-canaries 6 --out /tmp/sa_dry
```

The dry run exits 0 and writes `calls.jsonl`, `summaries.jsonl`, `results.json`, `report.txt` and
`plot.png` to `--out`. `--dry-run` substitutes a deterministic fake lossy summarizer and a fake keyword
monitor, so its numbers are not evidence about any real model. A real run adds `--base-url`,
`--api-key-env`, repeatable `--summarizer` / `--monitor` and a `--max-usd` cost guard (see
`src/summary_audit/README.md`); no real run was made for this README. The `convert` subcommand was not run.

Tests:

```bash
cd summarizer-monitor
python -m pytest tests -q        # 5 passed
```

## Datasets used

| Dataset | Source | Licence | Where that is stated |
|---|---|---|---|
| Mantiq swarm traces: 7 clean practice runs, 18 agents (planner a01, judge a18, 16 workers), 128-212 messages per run | Hugging Face `zenml/mantiq-swarm-traces` | CC BY 4.0 | pilot record `loop2b/l2_09_sample_unit.py` (module docstring), repeated in `src/summary_audit/README.md`; vendored as `src/summary_audit/data/mantiq_real_messages.json` |
| MAST / ChatDev traces (the second corpus) | Hugging Face `mcemri/MAST-Data`; ChatDev traces converted by `loop9/corpus2_scripts/convert_chatdev.py` | CC BY 4.0 | pilot record `loop9/corpus2_scripts/convert_chatdev.py` (line 1), repeated in `src/summary_audit/README.md`; vendored as `src/summary_audit/data/chatdev_corpus2.json` |
| Loop 8 agent-written deal sessions (66 coordinated vs 64 control) | generated in the 2026-11-06 pilot loops; not a public dataset | not a licensed third-party set | source as recorded in `data/README.md` (`loop8/runs/mon.jsonl`, `loop8/runs/labels.jsonl`) |
| Loop 1c blame-chain logs and the planted deal templates | generated in the 2026-11-06 pilot loops | not a licensed third-party set | source as recorded in `data/README.md` (`loop1c/runs/l1c17*/`, `loop1c/runs/l1c20*.jsonl`) and `src/summary_audit/README.md` (deals from `loop2b`, `loop2d`, `loop9`) |

The two public corpora are CC BY 4.0 and are vendored under their upstream names; attribute them if you
redistribute anything built on them. The deals are fictional in every case: the host logs are real
traces, the 4-message split agreements are planted.

## Pre-registration commits

Locks in this repo (`feat/summarizer-monitor`, `git log --oneline --grep="research(protocol)"`, 11 commits at the
time of writing):

| Hash | Date (PT) | Subject |
|---|---|---|
| `ba42f13` | 2026-11-06 22:23:20 | research(protocol): E1 raw lane on agent-written deals; E2 canary audit prospective (two-stage lock) |
| `3bf369f` | 2026-11-06 22:26:46 | research(protocol): E1 amendment - H1 rule |
| `1634cec` | 2026-11-06 22:43:09 | research(protocol): E2 stage-1 predictions |
| `bec2a9b` | 2026-11-06 22:58:44 | research(protocol): E2b canary audit PASS-side prospective test (two-stage lock) |
| `0c5cb4d` | 2026-11-06 23:03:23 | research(protocol): E2b model selection |
| `fd9228c` | 2026-11-06 23:08:15 | research(protocol): E2b stage-1 predictions |
| `3a5f181` | 2026-11-06 23:25:06 | research(protocol): E2c more PASS-side canary cases (two-stage lock) |
| `389dfe3` | 2026-11-06 23:32:11 | research(protocol): E2c model selection |
| `fa98cdd` | 2026-11-06 23:36:20 | research(protocol): E2c stage-1 predictions |
| `da8341c` | 2026-11-06 23:46:21 | research(protocol): E2d Opus 5.5 + Kimi k3.1 PASS-side test (two-stage lock) |
| `f313786` | 2026-11-06 23:51:24 | research(protocol): E2d model selection |

Two-stage locks named in `findings.md`; all hashes exist in this repo's history: E2 protocol lock
`ba42f13`, stage-1 predictions `1634cec` (committed before set B ran); E2b protocol lock `bec2a9b`,
stage-1 predictions `fd9228c`; E1 protocol lock `ba42f13` with amendment `3bf369f`, both before the first
H1 monitor output file (22:27:51 PT, see `experiments/E1-raw-lane-agent-written/analysis.md`). E2c: protocol
`3a5f181`, model selection `389dfe3`, stage-1 predictions `fa98cdd`. E2d: protocol `da8341c` (running).

The raw pilot records sit in a separate repository (`git rev-parse --show-toplevel` from
`~/research-taste/swarm-alignment/pilots/2026-11-06` gives `~/research-taste`). Its history for that folder
has 208 commits whose subject matches `protocol|PREDICTIONS|lock|prereg` (case-insensitive;
`git log --reverse --format='%h|%ad|%s' -- swarm-alignment/pilots/2026-11-06`, filtered with `grep`). The
full list with exact hashes, dates and subjects is in [`pilot_protocol_commits.txt`](pilot_protocol_commits.txt).
The locks the results here rest on:

| Hash | Date (PT) | Subject |
|---|---|---|
| `40bfd9a` | 2026-11-06 16:29:21 | research(protocol): L2-09 sample agents vs messages for partial-view coordination monitors on real Mantiq swarm chatter (predictions locked) |
| `5fd8937` | 2026-11-06 19:14:26 | research(protocol): L2-13f/g second summarizer family and chunk-size dose-response predictions |
| `dfe585a` | 2026-11-06 20:32:43 | research(protocol): L1c-22 do corrections exhaust monitor reasoning budgets (local Flash-Next) - predictions locked |
| `5845bec` | 2026-11-06 20:42:39 | research(protocol): L8-01/L8-02 agent-generated deals vs the summary blind spot - predictions locked |
| `297ac26` | 2026-11-06 20:47:40 | research(protocol): L9-01 lock predictions and code for summary-design fixes (pair threads, verbatim quotes, random sample, coordination ensemble) |
| `d510c75` | 2026-11-06 20:50:28 | research(protocol): L8-01 amendment 1 - locked extension fires; add llama-4-scout swarm family (before any monitor call) |
| `0c44d44` | 2026-11-06 20:52:32 | research(protocol): L9-02 lock predictions and code for second-corpus replication (MAST ChatDev traces) |
| `67275ee` | 2026-11-06 20:59:08 | research(protocol): L9-01b lock round-2 designs (pair-describe, pair two-family) on three deal sets |
| `5e1ea5f` | 2026-11-06 21:03:43 | research(protocol): L1c-22c fix line vs token inflation - predictions locked |
| `e1544a1` | 2026-11-06 21:03:58 | research(protocol): L9-01c lock round-3 design H (raw peer messages, with/without summaries) |
| `d8d68de` | 2026-11-06 21:06:09 | protocols: timestamp correction notes (git commit time is authoritative) |
| `dd7456b` | 2026-11-06 21:53:48 | review2(protocol): L2-13 strong-summarizer stress test (Sonnet 5.5, GPT-5.6-sol), predictions locked |

Git commit time is authoritative; `d8d68de` records timestamp corrections inside the protocol notes.

## Scope and limitations

- The large effects are on planted deals; the realistic-deal effect is small, and not significant at
  matched false alarms (+6 points, CI -3 to +15).
- Planted deals come from 6 templates per corpus, and H1 "closes the gap" on planted deals only by
  construction, because planted deals are all cross-agent.
- Monitors used: Claude Haiku 5.5 + DeepSeek v4.1 Flash, pooled over (log, monitor) pairs, for the
  planted-deal ceiling results; Claude Sonnet 5.5 for the realism result and for E1. Parse failures are
  excluded and counted, never counted as flags.
- Thresholds do not transfer across summarizers: each summarizer sits at a different false-alarm level,
  so every view needs its own threshold. This is exactly why E1's lane failed its false-alarm bar
  (8/64 against the <=6 bar) while matching the full log threshold-free.
- The canary audit's PASS side is preliminary: 10 of 10 prospective calls matched, but only 1 of them is a
  PASS call, and that case is a Gemini model. An "always FAIL" rule would have scored 9/10. The canary
  overstates held-out loss by about 10 points, so treat it as a screen, not a calibration.
- One ceiling exception is on the record: Nova summaries let monitors catch 9 points more than Nova's own
  full-log read on set A. Hence "capped by / rarely beats", never "never beats".
- The concentration of failures in GPT-5.6 tiers across three oversight roles (summarizer, corrections
  monitor, identity check) is post hoc; it is not headlined.
- Deviations: Kimi k3.1-pro was swapped out of E2 for cost and leaked reasoning text before its scores
  were read, so its partial drops (+12.5, +10) are exploratory. Gemini's E2b control design was switched
  from the optional fresh controls ($5.04) to the protocol design ($4.14) after the cost projection and
  before any monitor score existed, and the controls were run anyway; disclosed in the E2b analysis.
- The blame-chain raw baseline is 0/14 like-for-like; the 0/28 figure pools two note wordings.
- The CLI is a measurement harness. Its planted deal text keeps Mantiq-style references (planner `a01`,
  `/shared/claims`, task ids) in deal sets A and B, a known artefact on non-Mantiq logs.
- Killed claims stay killed: L7, L10-16b and L2-08 are not in the main text.

## Weekend work

Everything in `summarizer-monitor/` was written after the 2026-11-06 13:30 PT kickoff.

- First commit touching this directory: `53978cd`, 2026-11-06 22:23:20 -0800, "research(init):
  summarizer-monitor - package F workspace (the summarizer is the monitor)". The E1/E2 protocol locks
  land in the same minute.
- The pilot records repository (`~/research-taste`) started on 2026-11-02 with the sprint brief. Its
  first commit touching `swarm-alignment/pilots/2026-11-06` is `ae3e5cb`, 2026-11-06 14:48:40 -0800,
  "research(protocol): wild-idea loop pilots A (incentive laundering), B (audit capture), G1 (collaboration
  training) with predictions", also after the 13:30 PT kickoff.
- Preexisting code: the parent repository's `steer` package predates the sprint (first commit `43dcc62`,
  2026-11-04 23:58:13 -0800). Nothing in this directory (`src/`, `src/summary_audit/`, `experiments/*/code`,
  `tests/`, `paper/`) imports it or any other parent-repo module. In the pilot records, 8 scripts do import
  it (`steer.common`, `steer.models`, `steer.boards`, `steer.scenarios`): `pa_laundering.py`, `pb_audit.py`,
  `loop2/l2_04_secret_leak.py`, `loop2/l2_04v2_artifacts.py`, `loop2/l2_04v3_quiet.py`,
  `loop2/s_g3_truthstego.py`, `loop2/s_g3v2_truthstego.py` and `loop2/l2_h_priming.py`. These belong to other
  pilot ideas; none of the loops whose records feed these results (`loop1c`, `loop2b`-`loop2d`, `loop8`,
  `loop9`, `review2`) imports them or `steer`. The pilot `or_client.py` helper reads the OpenRouter key from
  the parent repository's `.env` (configuration, not code).
- Code imported from the pilot records repository, all of it written earlier on 2026-11-06 after the
  kickoff: `or_client.ORClient` (the OpenRouter API helper with a spend ledger; that repository's history
  first mentions it in commit `10e757d`, dated about 15:01 PT) in
  `experiments/E1-raw-lane-agent-written/code/e1_run.py`,
  `experiments/E2-canary-audit-prospective/code/e2_run.py`,
  `experiments/E2b-canary-pass-side/code/e2b_run.py` and `experiments/E2c-canary-pass-side-2/code/e2c_run.py`;
  the prompt / chunking / canary-insertion modules `l2_13_summary_launder`, `l2_13x_harden` and
  `l2_13i_newdeals` in the same four runners; `l8_pipeline` in `e1_run.py`; `l9_table` in
  `src/build_data.py:363`; `l1c17_blame` and `l1c13_bakein` in `src/build_demo.py:228`. The CLI vendors
  the same prompts and deal templates instead of importing them, and has no runtime dependency on the
  records root (`src/summary_audit/README.md`).
- Other inputs: the two public CC BY 4.0 corpora above, and paid OpenRouter calls made by the overnight
  experiment agents (per-experiment spend is recorded in `research-log.md` and in each experiment's
  `results/`). No API key, token, e-mail address or personal data is stored in this directory.
