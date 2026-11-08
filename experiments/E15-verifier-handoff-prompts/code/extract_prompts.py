#!/usr/bin/env python3
"""Extract the shipped handoff/compaction strings for E15 verbatim from the downloaded sources (no edits) and write
../prompts/handoff_prompts_raw.json with provenance. Sources are parsed, never imported or executed.

  python3 -I extract_prompts.py <agentscope_unzipped_root> <aris_repo_root>

AgentScope: pip wheel agentscope==2.0.11 (PyPI). ARIS: github.com/wanshuiyin/Auto-claude-code-research-in-sleep at the
commit recorded below (cloned 2026-11-08).
"""
import ast
import json
import subprocess
import sys
from pathlib import Path

AS, AR = Path(sys.argv[1]), Path(sys.argv[2])
OUT = Path(__file__).resolve().parent.parent / "prompts" / "handoff_prompts_raw.json"


def tree(p):
    return ast.parse(p.read_text())


def cls(t, name):
    return next(n for n in ast.walk(t) if isinstance(n, ast.ClassDef) and n.name == name)


def field_kw(node, kw):
    """Value of keyword `kw` in the Field(...) call assigned to an annotated class attribute."""
    return next(k.value.value for k in node.value.keywords if k.arg == kw)


# ---- AgentScope 2.0.11
cfg_t = tree(AS / "agentscope/agent/_config.py")
schema = cls(cfg_t, "SummarySchema")
schema_fields = [(n.target.id, field_kw(n, "description")) for n in schema.body if isinstance(n, ast.AnnAssign)]
comp = next(n for n in ast.walk(cfg_t) if isinstance(n, ast.AnnAssign) and getattr(n.target, "id", "") == "compression_prompt")
tmpl = next(n for n in ast.walk(cfg_t) if isinstance(n, ast.AnnAssign) and getattr(n.target, "id", "") == "summary_template")
goal_t = tree(AS / "agentscope/pipeline/_goal_pipeline.py")
hint = next(n.value.value for n in ast.walk(goal_t) if isinstance(n, ast.Assign)
            and any(getattr(t, "id", "") == "hint" for t in n.targets) and isinstance(n.value, ast.Constant))
rep = cls(goal_t, "_ExecutionReport")
report_desc = next(field_kw(n, "description") for n in rep.body if isinstance(n, ast.AnnAssign) and n.target.id == "report")
version = (AS / "agentscope/_version.py").read_text().split('"')[-2]

# ---- ARIS
sha = subprocess.run(["git", "-C", str(AR), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
arl = (AR / "skills/auto-review-loop/SKILL.md").read_text()
i = arl.index("**Append to `findings.md`**")
compact = arl[i:arl.index("```\n", arl.index("```markdown", i) + 12) + 3]
llm = (AR / "skills/auto-review-loop-llm/SKILL.md").read_text()
slot = "[Full research context: claims, methods, results, known weaknesses]"
assert slot in llm
reviewer_sys = "You are a senior ML reviewer (NeurIPS/ICML level)."
assert reviewer_sys in llm

out = [
    {"name": "agentscope_goal_pipeline_report", "package": "agentscope", "version": version,
     "file": "agentscope/pipeline/_goal_pipeline.py", "var": ["GoalPipeline hint (system-reminder)", "_ExecutionReport.report"],
     "use": "executor -> verifier: the verifier is shown only '<report>{execution_report}</report>'",
     "strings": [hint, report_desc]},
    {"name": "agentscope_react_compression", "package": "agentscope", "version": version,
     "file": "agentscope/agent/_config.py", "var": ["compression_prompt", "SummarySchema fields", "summary_template"],
     "use": "agent memory compression; the summary replaces the conversation history",
     "strings": [comp.value.keywords[0].value.value, json.dumps(schema_fields), tmpl.value.keywords[0].value.value]},
    {"name": "aris_compact_findings", "package": "ARIS (Auto-claude-code-research-in-sleep)", "version": sha,
     "file": "skills/auto-review-loop/SKILL.md", "var": "COMPACT findings.md entry",
     "use": "executor log read instead of full logs on recovery (COMPACT = true) in the executor/reviewer loop",
     "strings": [compact]},
    {"name": "aris_llm_review_context", "package": "ARIS (Auto-claude-code-research-in-sleep)", "version": sha,
     "file": "skills/auto-review-loop-llm/SKILL.md", "var": "Phase A reviewer prompt slot",
     "use": "executor writes this slot of the prompt sent to a stateless external reviewer",
     "strings": [slot, reviewer_sys]},
]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
for o in out:
    print(f"### {o['name']} ({o['version'][:12]})")
    for s in o["strings"]:
        print("   ", s.replace("\n", "\\n")[:400])
