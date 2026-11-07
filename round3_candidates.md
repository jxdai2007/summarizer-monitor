# Round 3: needle-moving experiments for submission 1 (2026-11-07 ~09:45 PT)

Bar: each candidate must change a deployer decision or answer a judge's top critique, not just add measurement.
Constructive and defensive only.

**Columns.**
- Impact (1-10): would a judge's score move?
- Feas (1-10): runs by Sunday on the Mac Studio local model plus ≤ $15 of API.

| # | Idea | Critique it answers | Frameworks | Impact | Feas | Risk |
|---|---|---|---|---|---|---|
| N1 | **Audit the summary prompts that agent frameworks actually ship.** Take the verbatim default summarization / memory / compaction prompts from popular open-source frameworks (LangChain, LlamaIndex, AutoGen/AG2, CrewAI, LangMem, …), put them through the canary audit, then test a one-sentence oversight addendum to each. | "You told the summarizer to judge"; no real-world grounding. Our neutral prompt gave 0/32, so default prompts are probably much worse than our safety-aware one. | Reformulation (change the object), What-changed | 8.5 | 9 | Prior art on compaction (Chen 2026, Wang 2026), but those study the acting agent, not the overseer |
| N2 | **Canary-guided prompt repair.** Use set A as a training signal to search for summarizer-prompt variants that keep planted deals at zero false alarms; validate on held-out set B and ChatDev. | "The fix is a one-liner that moves little" (E5) | Negation (the audit becomes a repair tool) | 8 | 7 | Overfitting; held-out sets control for it |
| N7 | **Canaries in production.** Power analysis from existing records: how many injected canaries does it take to detect a silent summarizer swap (e.g. Opus → luna) mid-deployment? | Operational value; reusable procedure | Analogy (statistical process control) | 7 | 10 ($0) | Simulation from existing flags |
| N3 | More agent-written sessions from a local swarm (bigger n for realism) | Realism | — | 6 | 5 | Slow locally; may confirm the small effect |
| N4 | Offline audit with a local monitor (E11, drafted) | Labs can't share logs | — | 6.5 | 9 | Measurement |
| N9 | Fine-tune a small summarizer on canaries (depends on Jollen's Adaption credits) | Fix | — | 8 | ? | Credits unknown; memory 13% free |
| — | Killed: evidence-ledger summaries (L9-01 already failed), ensemble routing (L2d-10 null), adaptive-attacker tests (out of scope here) | | | | | |

**Order.** N1 first: biggest critique, real-world grounding, cheap-fix pattern. N7 in parallel ($0). Then N2 if time
allows.
