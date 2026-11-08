"""Build to_human/teleprompter.html: the video narration, one block per beat, in large type, with the timecode, the
target length, and which slides of to_human/video_deck.html to show during that beat. Everything is read from
to_human/video_script.md (narration quote blocks, {{source}} markers removed) and slides.html (beat of each slide),
so re-running after a script change keeps the teleprompter in sync.

Usage: python3 src/build_teleprompter.py
Keys: Space start/stop scrolling, Up/Down speed, Left/Right jump a beat, +/- text size, M mirror.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUMAN = ROOT / "to_human"
E = html.escape


def beats():
    t = (HUMAN / "video_script.md").read_text()
    out = []
    for m in re.finditer(r"^## Beat (\d+) · ([^·\n]+?) · ([^\n]+)\n(.*?)(?=^## |\Z)", t, re.S | re.M):
        n, tc, name, body = int(m.group(1)), m.group(2).strip(), m.group(3).strip(), m.group(4)
        paras, cur = [], []
        for line in body.splitlines():
            if line.startswith(">"):
                cur.append(line.lstrip("> ").rstrip())
            elif cur:
                paras.append(" ".join(cur))
                cur = []
        if cur:
            paras.append(" ".join(cur))
        clean = [re.sub(r"\s+", " ", re.sub(r"\{\{.*?\}\}", "", p)).replace(" ,", ",").replace(" .", ".").strip() for p in paras]
        a, b = [sum(int(x) * 60 ** i for i, x in enumerate(reversed(s.split(":")))) for s in tc.split("-")]
        out.append(dict(n=n, tc=tc.replace("-", "–"), name=name, paras=[p for p in clean if p], secs=b - a))
    return out


def slide_map():
    s = (HUMAN / "video_deck.html").read_text()
    m = {}
    for k, b in enumerate(re.findall(r"Narration · beat (\d+)", s), start=1):
        m.setdefault(int(b), []).append(k)
    return m


def main():
    B, M = beats(), slide_map()
    total_w = sum(len(" ".join(b["paras"]).split()) for b in B)
    blocks = []
    for b in B:
        w = len(" ".join(b["paras"]).split())
        sl = M.get(b["n"], [])
        show = ("slide " if len(sl) == 1 else "slides ") + ", ".join(map(str, sl)) if sl else "no slide"
        paras = "".join(f"<p>{E(p)}</p>" for p in b["paras"])
        blocks.append(f'<section class="beat" id="b{b["n"]}"><div class="cue"><span>Beat {b["n"]} · {E(b["name"])}</span>'
                      f'<span>{E(b["tc"])} · {b["secs"]} s · {w} words · show {show}</span></div>{paras}</section>')
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Video Teleprompter</title>
<style>
:root {{ --bg:#111; --ink:#f4f1ea; --cue:#e0a84a; --muted:#8a867e; --size:44px; }}
html,body {{ margin:0; background:var(--bg); color:var(--ink); font:400 var(--size)/1.45 Georgia, serif; }}
main {{ max-width:1100px; margin:0 auto; padding:40vh 48px 70vh; }}
.mirror main {{ transform:scaleX(-1); }}
.beat {{ margin-bottom:1.6em; }}
.cue {{ display:flex; justify-content:space-between; gap:1em; font:600 20px/1.3 system-ui, sans-serif; color:var(--cue);
        border-bottom:1px solid #333; padding-bottom:6px; margin-bottom:.4em; flex-wrap:wrap; }}
p {{ margin:.2em 0 .6em; }}
#hud {{ position:fixed; top:10px; right:14px; font:13px system-ui, sans-serif; color:var(--muted); }}
#line {{ position:fixed; left:0; right:0; top:38vh; border-top:2px solid rgba(224,168,74,.35); pointer-events:none; }}
header {{ font:15px/1.5 system-ui, sans-serif; color:var(--muted); max-width:1100px; margin:0 auto; padding:20px 48px 0; }}
@media (max-width:700px) {{ :root {{ --size:30px; }} main, header {{ padding-left:16px; padding-right:16px; }} }}
</style></head>
<body>
<header>{total_w} spoken words, target 3:00 (about {round(total_w / 3)} words per minute). Space start/stop · ↑/↓ speed ·
←/→ previous/next beat · +/− size · M mirror. Slides: open to_human/video_deck.html, press F, use → to advance.</header>
<div id="line"></div><div id="hud"></div>
<main>{''.join(blocks)}</main>
<script>
let run=false, speed=1.2, size=44, acc=0;
const hud=document.getElementById('hud');
const show=()=>hud.textContent=(run?'scrolling':'paused')+' · speed '+speed.toFixed(1)+' · size '+size;
function tick(){{ if(run){{ acc+=speed; if(acc>=1){{ window.scrollBy(0,Math.floor(acc)); acc-=Math.floor(acc); }} }} requestAnimationFrame(tick); }}
const beats=[...document.querySelectorAll('.beat')];
function jump(d){{ const y=window.scrollY+window.innerHeight*0.38+5; let i=beats.findIndex(b=>b.offsetTop>y)-1;
  if(i<-1) i=beats.length-1; const t=Math.max(0,Math.min(beats.length-1,(d>0?i+1:i-(beats[Math.max(i,0)].offsetTop>=y-10?1:0))));
  window.scrollTo(0,beats[t].offsetTop-window.innerHeight*0.38+10); }}
addEventListener('keydown',e=>{{
  if(e.key===' '){{ run=!run; e.preventDefault(); }}
  else if(e.key==='ArrowUp'){{ speed=Math.min(6,speed+0.2); e.preventDefault(); }}
  else if(e.key==='ArrowDown'){{ speed=Math.max(0.2,speed-0.2); e.preventDefault(); }}
  else if(e.key==='ArrowRight'){{ jump(1); e.preventDefault(); }}
  else if(e.key==='ArrowLeft'){{ jump(-1); e.preventDefault(); }}
  else if(e.key==='+'||e.key==='='){{ size+=4; document.documentElement.style.setProperty('--size',size+'px'); }}
  else if(e.key==='-'){{ size=Math.max(20,size-4); document.documentElement.style.setProperty('--size',size+'px'); }}
  else if(e.key==='m'||e.key==='M'){{ document.body.classList.toggle('mirror'); }}
  show(); }});
show(); tick();
</script></body></html>
"""
    out = HUMAN / "teleprompter.html"
    out.write_text(page)
    print(f"wrote {out.relative_to(ROOT)}: {len(B)} beats, {total_w} words, slide map {M}")


if __name__ == "__main__":
    main()
