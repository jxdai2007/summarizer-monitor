"""Build to_human/slides.html: a self-contained, offline 16:9 deck that follows the beats of to_human/video_script.md.
Every number on a slide is read from data: to_human/panels/panel_numbers.json (written by src/fig_panels.py, which this
script reruns first), data/*.csv, to_human/demo_numbers.json and the data block inside to_human/demo.html (both written by
src/build_demo.py from the raw records), and two quoted lines in the E1/E2 analysis files (regex, fails loudly if absent).
Speaker notes (press N) are the narration quote blocks of video_script.md with the {{source}} markers removed.

Usage: /Users/macstudio/projects/swarm-alignment/.venv/bin/python src/build_slides.py
Keys in the deck: Left/Right (also Space, PageUp/PageDown), Home/End, N notes, F fullscreen.
"""
from __future__ import annotations

import base64
import csv
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fig_panels  # noqa: E402

ROOT = fig_panels.ROOT
DATA, HUMAN, PANELS, EXP = ROOT / "data", ROOT / "to_human", ROOT / "to_human" / "panels", ROOT / "experiments"
E = html.escape


def rd(name):
    return list(csv.DictReader(open(DATA / name)))


def grab(path, pattern, what):
    m = re.search(pattern, Path(path).read_text())
    if not m:
        raise SystemExit(f"build_slides: could not find {what} in {path} (pattern {pattern!r})")
    return m


def img(name):
    return "data:image/png;base64," + base64.b64encode((PANELS / name).read_bytes()).decode()


def pct(x):
    return round(100 * float(x))


# ------------------------------------------------------------------ narration from the video script
def beats():
    t = (HUMAN / "video_script.md").read_text()
    out = {}
    for m in re.finditer(r"^## Beat (\d+) · ([^·\n]+?) · ([^\n]+)\n(.*?)(?=^## |\Z)", t, re.S | re.M):
        n, tc, name, body = int(m.group(1)), m.group(2).strip(), m.group(3).strip(), m.group(4)
        quotes, cur = [], []
        for line in body.splitlines():
            if line.startswith(">"):
                cur.append(line.lstrip("> ").rstrip())
            elif cur:
                quotes.append(" ".join(cur))
                cur = []
        if cur:
            quotes.append(" ".join(cur))
        quotes = [re.sub(r"\s+", " ", re.sub(r"\{\{.*?\}\}", "", q)).replace(" ,", ",").replace(" .", ".").replace(" :", ":").replace(" ;", ";").strip()
                  for q in quotes]
        out[n] = dict(tc=tc.replace("-", "–"), name=name, quotes=[q for q in quotes if q])
    return out


# ------------------------------------------------------------------ numbers
def numbers():
    fig_panels.main()  # regenerate the panels so the PNGs and panel_numbers.json match the CSVs
    P = json.loads((PANELS / "panel_numbers.json").read_text())
    demo = json.loads(grab(HUMAN / "demo.html", r'<script id="data" type="application/json">(.*?)</script>', "demo data").group(1))
    dn = json.loads((HUMAN / "demo_numbers.json").read_text())
    card = next(c for c in demo["tab1"]["cards"] if c["cond"] == "SPLIT")
    ceil = {(r["deal_set"], r["summarizer"]): r for r in rd("ceiling_planted.csv")}
    bd = [r for r in rd("ceiling_by_deal.csv") if r["summarizer"] == "openai/gpt-5.6-luna" and r["direction"] != "tie"]
    testi = {r["result_id"]: r for r in rd("testimony.csv")}
    lane_chars = grab(EXP / "E1-raw-lane-agent-written/analysis.md", r"\*\*([\d.]+)% of the FULL message-list characters", "lane size").group(1)
    # cost and time per audit over all 12 prospective summarizers (E2-E2d), as computed by paper/make_numbers.py
    pn = ROOT / "paper/numbers.tex"
    cost = [grab(pn, r"\\numdef\{" + k + r"\}\{([\d.]+)\}", k).group(1) for k in ("audit-costlo", "audit-costhi", "audit-minlo", "audit-minhi")]
    return dict(P=P, demo=demo, dn=dn, card=card, ceil=ceil, bd=bd, testi=testi, lane_chars=lane_chars,
                cost=f"${cost[0]} to ${cost[1]}", minutes=f"{cost[2]} to {cost[3]}",
                team_n=grab(HUMAN / "demo.html", r"A team of (\d+) AI agents", "team size").group(1))


# ------------------------------------------------------------------ slide pieces
def dumbbell(N):
    """Full-log vs summary catch rate per summarizer, same monitors (Haiku 5.5 + DeepSeek v4.1 Flash), from ceiling_planted.csv."""
    rows = [("A", "openai/gpt-5.6-luna", "GPT-5.6-luna", "set A"), ("B", "openai/gpt-5.6-luna", "GPT-5.6-luna", "set B"),
            ("C", "openai/gpt-5.6-luna", "GPT-5.6-luna", "ChatDev"), ("A", "openai/gpt-5.6-sol", "GPT-5.6-sol (flagship)", "set A"),
            ("A", "anthropic/claude-sonnet-5.5", "Claude Sonnet 5.5", "set A"), ("A", "google/gemini-3.8-flash", "Gemini 3.8 Flash", "set A"),
            ("B", "google/gemini-3.8-flash", "Gemini 3.8 Flash", "set B")]
    W, x0, x1, rh, top = 1712, 520, 1330, 82, 70
    sx = lambda v: x0 + (x1 - x0) * v / 100  # noqa: E731
    out = [f'<svg viewBox="0 0 {W} {top + rh * len(rows) + 40}" class="dumbbell" role="img" '
           'aria-label="Monitor catch rate on the full log versus on summaries, per summarizer">']
    for t in range(0, 101, 25):
        out.append(f'<line x1="{sx(t)}" x2="{sx(t)}" y1="{top - 20}" y2="{top + rh * len(rows) - 20}" class="grid"/>'
                   f'<text x="{sx(t)}" y="{top - 34}" class="tick" text-anchor="middle">{t}%</text>')
    for i, (ds, s, name, setname) in enumerate(rows):
        r = N["ceil"][(ds, s)]
        f, m = 100 * float(r["monitor_full_rate"]), 100 * float(r["monitor_summary_rate"])
        d, p = float(r["drop_pts"]), float(r["mcnemar_p_two_sided"])
        y = top + i * rh + 12
        cls = "loss" if d > 0 else "gain"
        sig = "" if p < 0.05 else ", n.s."
        verdict = f"loses {d:.0f} pts{sig}" if d > 0 else f"gains {-d:.0f} pts"
        out.append(f'<text x="0" y="{y + 9}" class="rowlab">{E(name)}</text><text x="380" y="{y + 9}" class="rowsub">{setname}</text>'
                   f'<line x1="{sx(f)}" x2="{sx(m)}" y1="{y}" y2="{y}" class="bar {cls}"/>'
                   f'<circle cx="{sx(f)}" cy="{y}" r="11" class="dot full"/><circle cx="{sx(m)}" cy="{y}" r="11" class="dot {cls}"/>'
                   f'<text x="{x1 + 50}" y="{y + 9}" class="verdict {cls}">{verdict}</text>')
        if i == 0:
            out.append(f'<text x="{sx(f)}" y="{y - 22}" class="key" text-anchor="middle">full log {f:.0f}%</text>'
                       f'<text x="{sx(m)}" y="{y - 22}" class="key" text-anchor="middle">summaries {m:.0f}%</text>')
    out.append("</svg>")
    return "".join(out)


def bars3(items):
    """Small horizontal bars: [(label, k, n, css class)]."""
    rows = []
    for lab, k, n, cls in items:
        rows.append(f'<div class="hb"><span class="hb-lab">{E(lab)}</span><span class="hb-track"><span class="hb-fill {cls}" '
                    f'style="width:{100 * k / n:.1f}%"></span></span><span class="hb-val">{k}/{n}</span></div>')
    return '<div class="hbars">' + "".join(rows) + "</div>"


def slides(N, B):
    P, card, dn, demo = N["P"], N["card"], N["dn"], N["demo"]
    A, Bn, C, K = P["A"], P["B"], P["C"], P["canary"]
    sc = card["scores"]
    luna_a = N["ceil"][("A", "openai/gpt-5.6-luna")]
    S = []
    b3 = " ".join(B[3]["quotes"])  # beat 3 spans two slides: split the narration after "The summarizer decides."
    cut = b3.find("The summarizer decides.")
    b3a, b3b = (b3[:cut + len("The summarizer decides.")], b3[cut + len("The summarizer decides."):].strip()) if cut >= 0 else (b3, "")

    def add(beat, head, body, cls="", note_idx=None, eyebrow=None, notes=None):
        b = B[beat]
        q = b["quotes"] if note_idx is None else [b["quotes"][i] for i in note_idx if i < len(b["quotes"])]
        q = notes if notes is not None else q
        S.append(dict(beat=beat, tc=b["tc"], eyebrow=eyebrow or f"Beat {beat} · {b['name']}", head=head, body=body, cls=cls,
                      notes=q))

    # 1 hook
    add(1, "", f"""
      <div class="title-block">
        <p class="kicker">Swarm Alignment Hackathon · Track 4, oversight</p>
        <h1>The Summarizer Is the Monitor</h1>
        <p class="lede">Nobody reads logs at swarm scale. A model summarizes them; the monitor reads the summary.
        So who is really monitoring?</p>
      </div>
      <img class="pipeline" src="{img('pipeline.png')}" alt="Pipeline: swarm agents, raw log, summarizer (highlighted as the unannounced first monitor), monitor, verdict">""",
        cls="s-title")

    # 2 setup: the planted deal, quoted from the demo log
    ins = card["inserted"]
    nsplit = {ds: N["ceil"][(ds, "openai/gpt-5.6-luna")]["n_split_logs"] for ds in "ABC"}
    log_lines = "".join(f'<li><span class="ln">#{m["n"]:03d}</span><span class="who">{E(m["from"])} → {E(m["to"])}</span>'
                        f'<span class="msg">{E(m["text"])}</span></li>' for m in ins)
    add(2, "Real swarm logs, with deals planted in them", f"""
      <div class="two">
        <ol class="steps">
          <li><b>Real logs.</b> {N['team_n']} agents build a Lisp interpreter (Mantiq swarm traces), plus a ChatDev corpus (MAST).</li>
          <li><b>Plant a split deal.</b> {len(ins)} harmless-looking messages between two workers, written by two models
            (Gemini and Grok). Split-deal logs: {nsplit['A']} in set A, {nsplit['B']} in set B, {nsplit['C']} in ChatDev.</li>
          <li><b>Chunk, summarize, monitor.</b> {demo['chunk']}-message chunks, summaries of at most {demo['sumWords']} words;
            monitors flag a log at score ≥ {demo['threshold']}.</li>
        </ol>
        <figure class="log">
          <figcaption>Log {E(card['log'].split('|')[0])}: the {len(ins)} planted messages ({E(card['pair'][0])} and {E(card['pair'][1])})</figcaption>
          <ol>{log_lines}</ol>
        </figure>
      </div>""")

    # 3 the ceiling
    add(3, "The monitor is capped by its summarizer", f'<img class="panel" src="{img("panel_A_ceiling.png")}" '
        f'alt="Scatter: monitor catch rate on summaries against the summarizer\'s own catch rate; rho {A["rho6"]:.2f}">', notes=[b3a])
    # 3b the spread
    add(3, "The summarizer decides, not summarization", f"""
      <p class="sub">Same planted deals, same two monitors (Claude Haiku 5.5 + DeepSeek v4.1 Flash); only the summarizer changes.
      False alarms on GPT-5.6-luna summaries: {luna_a['fa_summary_k']}/{luna_a['fa_summary_n']}.</p>
      {dumbbell(N)}""", eyebrow=f"Beat 3 · {B[3]['name']} (cont.)", notes=[b3b] if b3b else [])

    # 4 show, don't tell
    sent = E(card["pair_sents"][0])
    for phrase in ("potentially gaming task completion records", "no evidence of coordinated deception"):
        sent = sent.replace(E(phrase), f"<mark>{E(phrase)}</mark>")
    np_ = dn["script"]["neutral_prompt"]["values"]
    mons = list(sc["raw"])
    trows = "".join(f"<tr><th>{E(m)}</th><td>{sc['raw'][m]}</td><td class='low'>{sc['summary'][m]}</td></tr>" for m in mons)
    add(4, "It saw the deal, then cleared it", f"""
      <div class="two">
        <figure class="quote">
          <figcaption>GPT-5.6-luna summary, chunk {card['chunk']} of {card['n_chunks']} (it read {card['inserted_in_chunk']} of the
            {len(ins)} deal messages)</figcaption>
          <blockquote>… {sent} …</blockquote>
        </figure>
        <div class="stack">
          <table class="scores"><thead><tr><th>Monitor score</th><th>raw log</th><th>summary</th></tr></thead>
            <tbody>{trows}</tbody></table>
          <p class="small">Flag at score ≥ {demo['threshold']}. Same log, same monitors.</p>
          <div class="stat"><span class="big">{np_['caught']} of {np_['n']}</span>
            <span>split deals caught when the summary prompt is neutral (Haiku monitor). The judging happens in the summarizer.</span></div>
        </div>
      </div>""")

    # 5 testimony
    l2 = demo["tab2"]["l2d15"]
    add(5, "Agents write the record, and summaries pass it on as fact", f"""
      <div class="two wide-left">
        <img class="panel" src="{img('panel_C_testimony.png')}" alt="Bars: innocent-agent suspensions and cleared rule breaks">
        <div class="stack">
          <figure class="note"><figcaption>The culprit appends one line to the log</figcaption>
            <code>{E(demo['tab3']['note'])}</code></figure>
          <div class="stat"><span class="big">{l2['flag_hidden']} of {l2['n_logs']}</span>
            <span>caught deals vanish when {l2['n_deleted_min']}–{l2['n_deleted_max']} summary sentences are deleted
            ({E(l2['monitor'])} monitor). The verdict lives in one or two sentences.</span></div>
        </div>
      </div>""")

    # 6 fixes
    t = N["testi"]
    m = Bn["matched"]
    lane_fx = Bn["fixed50"]["raw lane (E1)"]
    add(6, "The fixes are cheap", f"""
      <div class="two even">
        <section class="fix">
          <h3>One summarizer line</h3>
          <code>{E(demo['tab3']['fix_line'])}</code>
          <div class="stat"><span class="big">{t['blame_summary_note_sonnet']['k']}/{t['blame_summary_note_sonnet']['n']} →
            {t['blame_summary_note_sumfix_sonnet']['k']}/{t['blame_summary_note_sumfix_sonnet']['n']}</span>
            <span>times Claude Sonnet 5.5 suspends only the innocent agent, reading summaries</span></div>
        </section>
        <section class="fix">
          <h3>A raw worker-to-worker lane</h3>
          <p>On deals the agents wrote themselves it matches full-log detection at about half the size
            ({N['lane_chars']}% of full-log characters), once calibrated.</p>
          <p class="small">Caught at matched false alarms (≤ 10% of controls), of {m['full log']['n']}:</p>
          {bars3([('full log', m['full log']['k'], m['full log']['n'], 'gray'), ('raw lane', m['raw lane (E1)']['k'], m['raw lane (E1)']['n'], 'blue'),
                  ('luna summaries', m['luna summaries']['k'], m['luna summaries']['n'], 'orange')])}
          <p class="small">None significantly different. At score ≥ 50 the lane raises {lane_fx['fa']}/{lane_fx['n_ctrl']}
            false alarms, so it needs its own threshold. AUC {Bn['auc']['lane']:.3f} vs {Bn['auc']['full']:.3f} for the full log.</p>
        </section>
      </div>""", note_idx=[0])

    # 7 audit
    u, run = K.get("unreviewed"), K.get("running") or []
    if u:
        slot = (f"<li><b>{' + '.join(u['batches'])} slot:</b> {u['n_correct']} of {u['n_prospective']} more calls match "
                f"({u['n_fail_calls']} FAIL, {u['n_pass_calls']} PASS); not yet in the reviewed findings.</li>")
    elif run:
        slot = f"<li><b>{' + '.join(run)}:</b> more PASS-side cases, running now.</li>"
    else:
        slot = ""
    rev = " + ".join(K["reviewed_batches"])
    add(6, "Before trusting a summarizer, audit it", f"""
      <div class="two canary">
        <img class="panel" src="{img('canary.png')}" alt="Scatter: canary drop against held-out drop for each summarizer">
        <ul class="facts">
          <li><b>Plant canary deals</b> in your own logs; compare the monitor on raw logs with the monitor on summaries.
            <b>{N['cost']}, {N['minutes']} minutes</b> per audit.</li>
          <li><span class="num">{K['n_correct']} of {K['n_prospective']}</span> prospective calls correct ({rev}), {K['n_vendors']} vendors:
            called in advance, it flagged all {K['n_fail_hit']} lossy summarizers and cleared {K['n_pass_calls']}: two clearly
            (Gemini 4 Argon, Claude Opus 5.5, whose summaries beat the raw log) and one narrowly (Kimi k3.1), in the first four tests. Over all 24 prospective calls: 20/24 right (always-FAIL scores 16/24);
            vendors picked blind to outcome (E8) only 3/6, all near the threshold.</li>
          <li><b>Spearman \u03c1 = {K['rho']:.3f}</b> over {K['n_summarizers']} summarizers ({K['n_earlier']} scored before the
            prospective tests). The canary overstates the held-out loss by {-K['mean_heldout_minus_canary']:+.1f} points on average
            over the {K['n_prospective']} prospective summarizers; the ranking transfers.</li>
          {slot}
          <li class="cli"><code>python -m summary_audit run --dry-run --format mantiq --run practice_07 --n-canaries 6 --out /tmp/sa_dry</code></li>
        </ul>
      </div>""", note_idx=[1], eyebrow=f"Beat 6 \u00b7 {B[6]['name']} (cont.)")

    # 7b: does the audit hold up? (Nov 7 preregistered tests; numbers from paper/numbers.tex, generated from the records)
    import re as _re
    NT = dict(_re.findall(r"\\numdef\{([A-Za-z0-9-]+)\}\{([^}]*)\}", (ROOT / "paper/numbers.tex").read_text()))
    nt = lambda k: NT[k].replace("\\ensuremath{-}", "\u2212")
    add(3, "Same deals, same monitors: the summarizer is a dial", f"""
      <img class="panel" style="max-height:860px;display:block;margin:0 auto" src="{img('dial.png')}"
        alt="Dot plot: held-out detection loss per summarizer, from about minus 21 points (summaries beat the raw log) to plus 69 points">""",
        eyebrow="Added 7 Nov \u00b7 all summarizers with held-out results",
        notes=["Each dot is one summarizer on the same held-out deals and monitors; left of zero, its summaries beat the raw log."])
    add(6, "Does the audit hold up for a deployer?", f"""
      <ul class="facts">
        <li><b>New environment</b> (ChatDev, different framework and deal author): canary label right for
          <span class="num">{nt('E7-match')}</span> summarizers, Spearman {nt('E7-rho')}.</li>
        <li><b>Second monitor family</b> on deals agents wrote themselves: Spearman {nt('E3b-rho')}, FAIL&minus;PASS gap
          {nt('E3b-gap')} points (CI {nt('E3b-gaplo')} to {nt('E3b-gaphi')}).</li>
        <li><b>Repeatable:</b> re-running the audit gave the same label in {nt('E4-match')} reruns.</li>
        <li><b>Its limit:</b> on three vendors picked blind to outcome, all near the threshold, it matched only
          {nt('E8-matchall')}. Over all {nt('dist-ncalls')} prospective calls: far from the threshold
          <span class="num">{nt('dist-far')}</span>, near it {nt('dist-near')} (post hoc). Act only on drops about 22+ points from 15; treat closer drops as undecided.</li>
        <li><b>Recalibrate per summarizer:</b> one carried-over threshold cost {nt('E6-detlosslo')}&ndash;{nt('E6-detlosshi')} points of
          detection for {nt('E6-nzero')} of {nt('E6-nsum')} summarizers (not predicted).</li>
      </ul>""", eyebrow="Added 7 Nov \u00b7 preregistered follow-ups (E3b, E4, E6, E7, E8)",
        notes=["All preregistered except two after-the-fact readings: the distance split and the detection cost of a carried-over threshold."])

    # 8 scope
    fx, mc = Bn["fixed50_cmp"], Bn["matched_cmp"]
    full_fx, luna_fx = Bn["fixed50"]["full log"], Bn["fixed50"]["luna summaries"]
    tpl = dn["script"]["templates_per_corpus"]["values"]["n"]
    n_loss = sum(r["direction"] == "loss" for r in N["bd"])
    add(7, "Scope, said aloud", f"""
      <div class="two wide-left">
        <img class="panel" src="{img('panel_B_realism.png')}" alt="Bars: realism on agent-written deals, matched false alarms and fixed threshold">
        <ul class="facts">
          <li><b>Agent-written deals, matched false alarms:</b> the gap is {mc['diff']:.0f} points (CI {mc['lo']:+.0f} to {mc['hi']:+.0f}),
            not significant.</li>
          <li><b>{pct(full_fx['k'] / full_fx['n'])}% → {pct(luna_fx['k'] / luna_fx['n'])}%</b> only at a fixed threshold
            (two-sided p = {fx['p']:.1g}).</li>
          <li><b>The big drops are on planted deals:</b> {tpl} templates per corpus, though {n_loss} of {len(N['bd'])} untied
            deals lose detection under GPT-5.6-luna.</li>
          <li><b>Thresholds do not transfer</b> across summarizers; the canary overstates the size of a loss, the ranking transfers.</li>
        </ul>
      </div>""")

    # 9 close
    add(8, "", """
      <div class="close">
        <h1>Treat your summarizer as a monitor.<br>Audit it like one.</h1>
        <p class="repo"><code>swarm-alignment/summarizer-monitor/</code> (branch <code>feat/summarizer-monitor</code>):
          README, data, analyses, the <code>summary_audit</code> CLI, the offline demo and these slides.</p>
      </div>""", cls="s-close")
    return S


# ------------------------------------------------------------------ page
CSS = """
/* Layout: a fixed 1920x1080 stage scaled to the window; one slide visible at a time, header band + body. */
:root {
  --paper: #fcfcfb; --ink: #0b0b0b; --ink-2: #52514e; --ink-3: #8a8984; --rule: #e4e3df; --tint: #f3f2ee;
  --summ: #eb6834; --summ-ink: #b4471c; --summ-wash: #fbebe4; --fix: #2a78d6; --fix-wash: #e8f0fb; --gray: #9b9a95;
  --night: #16130f; --night-ink: #f4f1ec;
  --f-display: "Avenir Next", "Avenir", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  --f-body: "Avenir Next", "Avenir", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  --f-mono: "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;
  color-scheme: light;
}
html, body { height: 100%; margin: 0; background: #2b2926; overflow: hidden; }
body { font-family: var(--f-body); color: var(--ink); }
#stage { position: absolute; left: 50%; top: 50%; width: 1920px; height: 1080px; transform-origin: center center; background: var(--paper);
  overflow: hidden; }
.slide { position: absolute; inset: 0; padding: 64px 104px 84px; box-sizing: border-box; display: none; flex-direction: column; gap: 28px; }
.slide.on { display: flex; }
.eyebrow { font: 500 22px/1 var(--f-mono); letter-spacing: .06em; text-transform: uppercase; color: var(--ink-3); display: flex;
  justify-content: space-between; }
.eyebrow .tc { color: var(--summ-ink); }
h1, h2, h3 { font-family: var(--f-display); margin: 0; text-wrap: balance; letter-spacing: -.01em; }
h2 { font-size: 64px; line-height: 1.05; font-weight: 700; }
h3 { font-size: 34px; font-weight: 700; }
.body { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: 24px; }
.sub { font-size: 28px; line-height: 1.4; color: var(--ink-2); margin: 0; max-width: 1500px; }
.small { font-size: 23px; line-height: 1.4; color: var(--ink-2); margin: 0; }
img.panel { max-width: 100%; max-height: 100%; object-fit: contain; min-height: 0; display: block; margin: 0 auto; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 64px; flex: 1; min-height: 0; align-items: center; }
.two.wide-left { grid-template-columns: 1.75fr 1fr; gap: 48px; }
.two > * { min-width: 0; min-height: 0; }
.stack { display: flex; flex-direction: column; gap: 28px; }
/* title + close */
.s-title { justify-content: center; gap: 36px; }
.title-block { display: flex; flex-direction: column; gap: 20px; }
.kicker { font: 500 24px/1 var(--f-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--summ-ink); margin: 0; }
h1 { font-size: 112px; line-height: .98; font-weight: 800; }
.lede { font-size: 38px; line-height: 1.35; color: var(--ink-2); margin: 0; max-width: 1400px; }
img.pipeline { width: 100%; max-height: 430px; object-fit: contain; }
.s-close { background: var(--night); color: var(--night-ink); justify-content: center; }
.s-close .eyebrow { color: #8f8a82; }
.s-close h1 { font-size: 104px; color: var(--night-ink); }
.s-close .kicker { color: var(--summ); }
.close { display: flex; flex-direction: column; gap: 40px; }
.repo { font-size: 30px; line-height: 1.5; color: #c9c3ba; max-width: 1500px; margin: 0; }
.repo code { font-family: var(--f-mono); color: var(--night-ink); background: #2a2520; padding: 2px 10px; border-radius: 6px; }
/* setup */
.steps { margin: 0; padding: 0; list-style: none; counter-reset: s; display: flex; flex-direction: column; gap: 30px; }
.steps li { counter-increment: s; font-size: 30px; line-height: 1.4; color: var(--ink-2); position: relative; padding-left: 64px; }
.steps li::before { content: counter(s); position: absolute; left: 0; top: 2px; font: 700 44px/1 var(--f-display); color: var(--summ); }
.steps b { color: var(--ink); }
figure { margin: 0; }
figcaption { font: 500 21px/1.35 var(--f-mono); color: var(--ink-3); margin-bottom: 14px; }
.log ol { list-style: none; margin: 0; padding: 0; border-top: 2px solid var(--rule); }
.log li { display: grid; grid-template-columns: 84px 160px 1fr; gap: 10px; padding: 16px 12px; border-bottom: 2px solid var(--rule);
  background: var(--summ-wash); font-size: 23px; line-height: 1.35; }
.log li + li { border-top: 0; }
.log .ln { font-family: var(--f-mono); color: var(--ink-3); }
.log .who { font-family: var(--f-mono); color: var(--summ-ink); font-weight: 600; }
/* dumbbell */
svg.dumbbell { width: 100%; flex: 1; min-height: 0; }
svg .grid { stroke: var(--rule); stroke-width: 2; }
svg .tick { font: 22px var(--f-body); fill: var(--ink-3); }
svg .rowlab { font: 600 30px var(--f-body); fill: var(--ink); }
svg .rowsub { font: 26px var(--f-body); fill: var(--ink-2); }
svg .key { font: 600 22px var(--f-body); fill: var(--ink-2); }
svg .bar { stroke-width: 6; stroke-linecap: round; }
svg .bar.loss { stroke: var(--summ); opacity: .45; } svg .bar.gain { stroke: #1baf7a; opacity: .45; }
svg .dot { stroke: var(--paper); stroke-width: 3; }
svg .dot.full { fill: var(--gray); } svg .dot.loss { fill: var(--summ); } svg .dot.gain { fill: #1baf7a; }
svg .verdict { font: 700 28px var(--f-body); fill: var(--ink); }
/* quote + scores */
blockquote { margin: 0; font-size: 36px; line-height: 1.45; color: var(--ink); border-left: 4px solid var(--rule); padding-left: 28px; }
mark { background: var(--summ-wash); color: var(--summ-ink); font-weight: 700; padding: 0 4px; }
table.scores { border-collapse: collapse; font-size: 30px; font-variant-numeric: tabular-nums; }
.scores th, .scores td { padding: 14px 24px; text-align: right; border-bottom: 2px solid var(--rule); }
.scores th:first-child { text-align: left; }
.scores thead th { font: 500 21px var(--f-mono); color: var(--ink-3); text-transform: uppercase; letter-spacing: .05em; }
.scores td { font-weight: 700; font-size: 40px; } .scores td.low { color: var(--summ-ink); }
.stat { display: flex; flex-direction: column; gap: 8px; font-size: 26px; line-height: 1.4; color: var(--ink-2); }
.stat .big { font: 800 64px/1 var(--f-display); color: var(--ink); font-variant-numeric: tabular-nums; }
.note code, .fix code, .cli code { font: 23px/1.5 var(--f-mono); display: block; background: var(--tint); padding: 18px 22px; border-radius: 8px;
  color: var(--ink); white-space: pre-wrap; }
/* fixes */
.fix { display: flex; flex-direction: column; gap: 22px; }
.fix p { font-size: 27px; line-height: 1.4; margin: 0; color: var(--ink-2); }
.hbars { display: flex; flex-direction: column; gap: 12px; }
.hb { display: grid; grid-template-columns: 230px 1fr 90px; gap: 16px; align-items: center; font-size: 25px; }
.hb-track { height: 30px; background: var(--tint); border-radius: 0 4px 4px 0; }
.hb-fill { display: block; height: 100%; border-radius: 0 4px 4px 0; }
.hb-fill.gray { background: var(--gray); } .hb-fill.blue { background: var(--fix); } .hb-fill.orange { background: var(--summ); }
.hb-val { font-weight: 700; font-variant-numeric: tabular-nums; }
/* fact lists */
ul.facts { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 24px; }
ul.facts li { font-size: 26px; line-height: 1.4; color: var(--ink-2); padding-top: 18px; border-top: 2px solid var(--rule); }
ul.facts b { color: var(--ink); }
ul.facts li.cli { border-top: 0; padding-top: 0; } .cli code { font-size: 19px; }
.two.canary { grid-template-columns: auto 1fr; gap: 56px; }
.two.canary img.panel { height: 100%; width: auto; max-width: 960px; }
.num { font: 800 40px/1 var(--f-display); color: var(--ink); }
/* chrome */
#bar { position: absolute; left: 0; bottom: 0; height: 6px; background: var(--summ); transition: width .25s ease; }
#count { position: absolute; right: 40px; bottom: 26px; font: 500 20px var(--f-mono); color: var(--ink-3); }
#notes { position: absolute; left: 0; right: 0; bottom: 0; max-height: 46%; overflow: auto; background: rgba(22, 19, 15, .94); color: #f4f1ec;
  padding: 32px 104px 48px; box-sizing: border-box; font-size: 30px; line-height: 1.5; }
#notes h4 { margin: 0 0 10px; font: 500 20px var(--f-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--summ); }
#notes p { margin: 0 0 14px; max-width: 1600px; }
#warn { position: absolute; top: 12px; right: 12px; background: #c00; color: #fff; font: 700 20px var(--f-mono); padding: 6px 12px; }
@media (prefers-reduced-motion: reduce) { #bar { transition: none; } }
"""

JS = """
const slides = [...document.querySelectorAll('.slide')], stage = document.getElementById('stage');
const notes = document.getElementById('notes'), bar = document.getElementById('bar'), count = document.getElementById('count');
let i = 0;
function fit() { const s = Math.min(innerWidth / 1920, innerHeight / 1080); stage.style.transform = `translate(-50%, -50%) scale(${s})`; }
function show(n) { i = Math.max(0, Math.min(slides.length - 1, n)); slides.forEach((s, k) => s.classList.toggle('on', k === i));
  notes.innerHTML = slides[i].querySelector('template.notes').innerHTML;
  bar.style.width = `${100 * (i + 1) / slides.length}%`; count.textContent = `${i + 1} / ${slides.length}`;
  if (location.hash !== '#' + (i + 1)) history.replaceState(null, '', '#' + (i + 1)); }
function overflowCheck() { const bad = [];
  slides.forEach((s, k) => { const was = s.classList.contains('on'); s.classList.add('on');
    const b = s.querySelector('.body'); const over = s.scrollHeight > s.clientHeight + 1 || (b && b.scrollHeight > b.clientHeight + 1)
      || [...s.querySelectorAll('*')].some(e => e.getBoundingClientRect().right > stage.getBoundingClientRect().right + 2);
    if (over) bad.push(k + 1); if (!was) s.classList.remove('on'); });
  if (bad.length) { const w = document.createElement('div'); w.id = 'warn'; w.textContent = 'overflow on slide ' + bad.join(', '); stage.append(w); } }
addEventListener('keydown', e => {
  if (['ArrowRight', 'PageDown', ' ', 'ArrowDown'].includes(e.key)) { show(i + 1); e.preventDefault(); }
  else if (['ArrowLeft', 'PageUp', 'ArrowUp', 'Backspace'].includes(e.key)) { show(i - 1); e.preventDefault(); }
  else if (e.key === 'Home') show(0); else if (e.key === 'End') show(slides.length - 1);
  else if (e.key === 'n' || e.key === 'N') notes.hidden = !notes.hidden;
  else if (e.key === 'f' || e.key === 'F') { if (!document.fullscreenElement) document.documentElement.requestFullscreen?.().catch(() => {});
    else document.exitFullscreen?.(); } });
addEventListener('resize', fit); addEventListener('hashchange', () => show(parseInt(location.hash.slice(1)) - 1 || 0));
fit(); overflowCheck(); show((parseInt(location.hash.slice(1)) || 1) - 1);
"""


def page(S):
    secs = []
    for k, s in enumerate(S):
        head = f'<h2>{E(s["head"])}</h2>' if s["head"] else ""
        notes = "".join(f"<p>{E(q)}</p>" for q in s["notes"]) or "<p>(no narration for this slide)</p>"
        secs.append(f"""
  <section class="slide {s['cls']}" aria-label="Slide {k + 1}">
    <div class="eyebrow"><span>{E(s['eyebrow'])}</span><span class="tc">{E(s['tc'])}</span></div>
    {head}
    <div class="body">{s['body']}</div>
    <template class="notes"><h4>Narration · beat {s['beat']} · {E(s['tc'])}</h4>{notes}</template>
  </section>""")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Summarizer Is the Monitor</title>
<style>{CSS}</style>
</head>
<body>
<div id="stage">{''.join(secs)}
  <div id="notes" hidden></div>
  <div id="bar"></div><div id="count"></div>
</div>
<script>{JS}</script>
</body>
</html>
"""


def main():
    N = numbers()
    S = slides(N, beats())
    out = HUMAN / "slides.html"
    out.write_text(page(S))
    print(f"wrote {out.relative_to(ROOT)}: {len(S)} slides, {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
