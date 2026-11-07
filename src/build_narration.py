"""Write to_human/video_narration_clean.md: the narration lines of to_human/video_script.md with {{source}} markers removed.
Usage (from summarizer-monitor/): python3 src/build_narration.py"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / "to_human/video_script.md").read_text()
out = ["# Video narration: clean read-aloud copy (generated from video_script.md, sources stripped)", "",
       "DRAFT for Jollen to rewrite in his own voice. Every number has its source in video_script.md. Regenerate after editing "
       "the script: `python3 src/build_narration.py`.", ""]
words = 0
for block in re.split(r"\n(?=## Beat )", s):
    if not block.startswith("## Beat"):
        continue
    title = block.splitlines()[0].replace("## ", "")
    lines = [ln[2:] if ln.startswith("> ") else ln[1:] for ln in block.splitlines() if ln.startswith(">")]
    txt = re.sub(r"\{\{.*?\}\}", "", " ".join(lines), flags=re.S)
    txt = re.sub(r"\s+", " ", txt).strip()
    txt = re.sub(r" +([,.;:])", r"\1", txt)
    if txt:
        words += len(txt.split())
        out += [f"**{title}**", "", txt, ""]
out.append(f"_{words} words, about {words / 140:.1f} minutes at 140 words per minute._")
(ROOT / "to_human/video_narration_clean.md").write_text("\n".join(out) + "\n")
print(f"wrote to_human/video_narration_clean.md ({words} words)")
