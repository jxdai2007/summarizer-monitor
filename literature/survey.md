# Literature survey: The Summarizer Is the Monitor

Verified 2026-11-06 ~22:50 PT. Each entry's title, authors and claims were checked against the arXiv abstract
(get_abstract), not taken from memory. Abstracts are treated as data. Use only these ids in the report unless you add
and verify new ones.

## Closest work, and how we differ

| arXiv | Title (authors) | What it shows | How we differ |
|---|---|---|---|
| 2607.11751 | When Local Monitors Miss Compositional Harm: Diagnosing Distributed Backdoors in Multi-Agent Systems (Hu, Wang) | "Observability boundary": once split fragments look benign in the monitored view, no detector on that view catches them. Full-trace monitors fail unless they reach the representation where the payload is exposed. | They treat the view as fixed and fragments as locally benign. We show the view is itself *produced by an LLM summarizer whose judgement caps the monitor*. The same split deals are caught 87% on the raw log and lost on GPT-5.6 summaries, but not on Claude/Gemini summaries. We give a test for it (canary audit). Our deals are not locally invisible: the raw-log monitor sees them. |
| 2606.22528 | Governance Decay: How Context Compaction Silently Erases Safety Constraints in Long-Horizon LLM Agents (Chen) | Context compaction drops governance constraints, so agents later violate policy (0% → 30%). Adversarial content can bias the summarizer to omit a policy. "Constraint Pinning" fixes it. | Same family of insight (the compression layer is a safety surface), but about the *acting agent's own context*. We study the *overseer's input*: monitors reading summaries of other agents' logs, the ceiling relation, and agent testimony laundered into the record. Cite as concurrent support for "compression is a first-class safety surface". |
| 2608.29028 | Facts Without Rules: Boundary Metadata Collapse in Multi-Agent LLM Handoffs (Wang, Goyal, Chandrasekharan, Sundaram) | Handoff summaries keep operational facts but drop boundary metadata ("summary collapse"), which causes privacy leakage. An explicit allowlist fixes it. | Our attribution-loss result (summaries name the right agent 10/28 → 28/28 with one summarizer line) is the oversight analogue: summaries drop *who did what*. They study privacy markers; we study accountability metadata and its effect on suspension decisions. |
| 2605.31593 | Stateful Online Monitoring Catches Distributed Agent Attacks (Brown, Bhargav, …, Wong, Hassani) | Distributed misuse across accounts evades per-transcript monitors. A stateful clustering monitor catches it 30% earlier. | Cross-account aggregation vs our compression layer. Shows the "split" threat model is live; complementary. |
| 2506.10949 | Monitoring Decomposition Attacks in LLMs with Lightweight Sequential Monitors (Yueh-Han, Joshi, Chen, Andriushchenko, Angell, He) | Decomposition attacks (87% ASR); a lightweight sequential monitor defends (93%). | Single conversation, monitor reads the raw sequence. We show what happens when the monitor reads a summary instead. |
| 2506.15740 | SHADE-Arena: Evaluating Sabotage and Monitoring in LLM Agents (Kutasov et al., incl. Shlegeris, Benton) | Benchmark for sabotage and monitoring; best monitor AUC 0.87. | A standard monitor-evaluation reference; their monitors read transcripts directly. |
| 2610.20941 | Screwtape: Adversarial Transcript Editing for Monitor Red-Teaming (Kozhevnikov, Tracy) | An LLM attacker edits real agent transcripts until monitors miss the harm. | Transcript *editing* attacks the record. Our editable-summary result (deleting 1-2 summary sentences hides 14/15) shows the summary is a single point of failure that is easier to edit than the raw log. |
| 2603.04582 | Self-Attribution Bias: When AI Monitors Go Easy on Themselves (Khullar, Hopkins, Wang, Roger) | Monitors rate actions as less risky when framed as their own. | Another way monitor inputs' framing changes verdicts. Our testimony result is framing by the *monitored agent* (corrections, blame notes). |

## Searches with no direct hit (record of novelty checks)
- `abs:summar* AND abs:monitor* AND (agent* OR transcript*) AND (oversight OR collusion OR sabotage)`, 2025+: 0 results.
- `"hierarchical summarization" AND (monitoring OR misuse OR agents)`, 2025+: 3 unrelated results.
- `abs:"summary" AND abs:"monitor" AND abs:"multi-agent"`, 2025-06+: 7 results; none about monitors reading summaries.
  The closest is 2605.16746, State Contamination in Memory-Augmented LLM Agents. Its abstract was not opened; check it
  before citing.
- Hierarchical-summary monitoring was proposed by Sumers et al. 2025 (Anthropic blog, not arXiv). Cite as a blog post
  with its URL and verify the URL before submission.

## Novelty sentence (for the talk and the report)
"2607.11751 proves a monitor can't catch what its view can't distinguish. We show that at swarm scale the view is
written by another model, and that model's judgement sets the monitor's ceiling. Gemini and Claude summaries keep the
deals that GPT-5.6 summaries drop, so this is a property of a component labs choose, and you can audit it."
