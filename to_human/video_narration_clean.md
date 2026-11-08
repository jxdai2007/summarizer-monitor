# Video narration: clean read-aloud copy (generated from video_script.md, sources stripped)

DRAFT for Jollen to rewrite in his own voice. Every number has its source in video_script.md. Regenerate after editing the script: `python3 src/build_narration.py`.

**Beat 1 · 0:00-0:15 · Hook**

Nobody reads logs at swarm scale. A model summarizes them; the monitor reads the summary. Swap that one model, and the same monitors catch fewer than half as many hidden deals, or more than if they had read the raw log. The summarizer is the real monitor, and a six-dollar test tells you which kind you have, unless it's close.

**Beat 2 · 0:15-0:35 · Setup**

We took real multi-agent logs: eighteen agents and a ChatDev corpus. We planted fictional deals to game the tests, each split across four harmless-looking messages. Then we summarize.

**Beat 3 · 0:35-1:05 · The figure**

Across six summarizer families, the monitor is capped by its own summarizer: rank correlation 0.99. The summarizer decides. With GPT-5.6-luna summaries, detection falls from 87 to 48 percent at zero false alarms. Claude Sonnet 5.5 summaries lose about ten points, and Gemini 3.8 summaries beat the raw log.

**Beat 4 · 1:05-1:35 · Show, don't tell**

The summarizer read three of the deal messages, called them potentially gaming, wrote: no evidence of coordinated deception. Raw log: monitors score 60 and 95. Summaries: 4 and 5. The judging happens in the summarizer. And the summary prompts frameworks ship? Across nine models, every one lost the deals. One sentence naming the monitor rarely fixes it. Fine-tuning a small open model on summaries from models that pass our audit does: seventy-one points lost becomes eleven.

**Beat 5 · 1:35-2:00 · Testimony**

The guilty agent appends one line: step 9 was run by build-agent-9, not me. On raw logs, Sonnet never suspends only the innocent agent: zero of 14. Reading a summary, 16 of 28.

**Beat 6 · 2:00-2:32 · Fixes and the audit**

The fixes are cheap. One summarizer line, keep agent tags and report later corrections as unverified, takes the framing from 16 of 28 to zero. Before trusting a summarizer, test it the way programmers test their tests: plant known deals, count how many get through. Mutation testing for oversight. Under six dollars, minutes. In its first four tests it got twelve of twelve summarizers right. It also tells good prompts from bad, twenty-nine times in thirty. But on vendors picked blind, all near the line, it was right half the time. Far from the line it was never wrong, and a preregistered test held eight of eight, all lossy-side. Trust its FAIL calls there.

**Beat 7 · 2:32-2:50 · Scope, said aloud**

Scope: on agent-written deals, at matched false alarms, the gap is six points, not significant. The big drops are on planted deals.

**Beat 8 · 2:50-3:00 · Close**

Treat your summarizer as a monitor. Audit it like one. Everything is in the repo.

_396 words, about 2.8 minutes at 140 words per minute._
