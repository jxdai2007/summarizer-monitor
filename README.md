# The Summarizer Is the Monitor

**When an AI monitor checks a team of AI agents for cheating, it usually reads a summary, not the full log. I found that the AI writing that summary decides what the monitor catches.**

Swarm Alignment Hackathon 2026 · Track 4 (oversight) · Jollen Dai, UCLA, with Apart Research

[Report (PDF)](paper/main.pdf) · [Slides (PDF)](to_human/slides.pdf) · [Full details](DETAILS.md)

![A real summary: the summarizer saw the cheating, called it "potentially gaming", then told the monitor there was "no evidence of coordinated deception". The monitor's risk score fell from 95 to 5.](to_human/video_slides/s4.png)

## The problem

When many AI agents work together, a second AI, the **monitor**, checks them for cheating. The agents write far more than the monitor can read, so a third AI, the **summarizer**, shortens the logs first, and the monitor only sees the summary. Monitors are usually tested on full logs, but in practice they read summaries, and the summarizer itself is rarely tested.

## What I did

I took real logs from a team of 18 AI coding agents (plus a second set of logs from ChatDev) and hid fake cheating plans in them: two agents secretly agree to game their tests, spread over four messages that each look innocent. Then the same monitors read either the full log or a summary written by one of 17 different summarizer models. Only the summarizer changed.

## What I found

1. **The summarizer decides what gets caught.** Switching only the summarizer took the monitor from catching 87% of the cheating to 48% (with GPT-5.6-luna summaries). Other summarizers, like Gemini and Claude Opus, did *better* than the full log. Across 17 summarizers, results ranged from 21 points better to 69 points worse.
2. **Popular tools fail.** The ready-made summary instructions that come with LangChain, LlamaIndex, LangMem and CrewAI failed in all 24 model-and-instruction combinations I tested.
3. **A cheap check works.** Hide cheating you already know about, summarize the logs, and count how much the monitor still catches. It costs under $6 per summarizer, and in my first round of tests it sorted all 12 summarizers correctly into safe and unsafe.

![Detection change for 17 summarizers, from 21 points better than the full log to 69 points worse.](to_human/video_slides/s5.png)

## Limits

- When the agents wrote their own cheating plans instead of my planted ones, the summary made only a small difference (6 points, not statistically significant).
- When a summarizer lands close to the pass line, the check is unreliable (right 3 times out of 6).
- I tested the tools' summary instructions, not the full tools.

## What's next

Test this on real-world agent systems, and against agents that deliberately try to fool the summarizer.

## Try the check

The demo below runs offline with fake models, so it needs no API key. It shows the whole pipeline end to end.

```bash
git clone https://github.com/jxdai2007/summarizer-monitor
cd summarizer-monitor/src
pip install openai matplotlib numpy
python -m summary_audit run --dry-run --format mantiq --run practice_07 --n-canaries 6 --out /tmp/demo
```

To test a real summarizer, see [src/summary_audit/README.md](src/summary_audit/README.md). The report calls this check a "canary audit".

## What's in the repo

| Folder | What it holds |
|---|---|
| `paper/` | the report (`main.pdf`) and its source |
| `src/summary_audit/` | the check, as a command-line tool |
| `experiments/` | one folder per experiment: the plan written before running it, the code and the results |
| `data/` | the logs and model outputs behind every number |
| `to_human/` | slides, figures and an offline demo page |

## Prior work

No code, data or results in this repository predate the sprint. Everything was written during the hackathon, after the kickoff on Friday 6 November 2026 at 13:30 PT (the first commit is 22:23 PT that day). My only pre-sprint code was for a different idea; it is not in this repository and no result uses it. Details are in [DETAILS.md, "Weekend work"](DETAILS.md#weekend-work) and in the report's "Preexisting code" appendix.

This repository was split out of my private hackathon repository with its history kept. Commit IDs quoted in the docs refer to that original repository.

## License

Code: MIT. Data from the two public log collections keeps its CC BY 4.0 license. All planted cheating and test logs are fictional.
