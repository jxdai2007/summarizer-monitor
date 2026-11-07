"""Log adapters (jsonl / mantiq / chatdev), canary planting, chunking.

Canonical message: {"agent": str, "to": str|None, "text": str, "t": number|str|None}.
"""
import hashlib
import json
import random
import re
from importlib import resources
from pathlib import Path

from . import prompts

MIN_PLANT_MSGS = 3  # an agent must appear in >= 3 messages to be a plant candidate (as in loop2d `workers`)


def rng_for(*parts):
    """Same seeded-rng helper as loop2c (sha256 of the joined parts)."""
    return random.Random(int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:12], 16))


def data_path(name):
    return Path(str(resources.files("summary_audit").joinpath("data", name)))


def _canon(m):
    agent = m.get("agent", m.get("from"))
    if agent is None or "text" not in m:
        raise ValueError(f"message needs 'agent' and 'text': {str(m)[:120]}")
    return {"agent": str(agent), "to": (str(m["to"]) if m.get("to") is not None else None), "text": str(m["text"]),
            "t": m.get("t"), "inj": False}


def make_log(log_id, msgs, fmt_name, team=None, candidates=None):
    agents = sorted({m["agent"] for m in msgs} | {m["to"] for m in msgs if m["to"]})
    return {"id": log_id, "msgs": msgs, "planted": False, "deal": None, "pair": None, "format": fmt_name,
            "team": team, "agents": agents, "candidates": candidates}


# ---------------------------------------------------------------- adapters
def load_jsonl(path, name=None):
    msgs = []
    with open(path) as f:
        for i, line in enumerate(f, 1):
            if line.strip():
                try:
                    msgs.append(_canon(json.loads(line)))
                except (ValueError, json.JSONDecodeError) as e:
                    raise SystemExit(f"{path}:{i}: bad message line ({e})")
    if len(msgs) < 10:
        raise SystemExit(f"{path}: only {len(msgs)} messages; need a log long enough to plant a 4-message deal")
    return [make_log(name or Path(path).stem, msgs, "jsonl")]


def load_mantiq(path=None, runs=None):
    path = path or data_path("mantiq_real_messages.json")
    real = json.load(open(path))
    runs = runs or [next(iter(real))]
    out = []
    for r in runs:
        key = r if r in real else next((k for k in real if k.endswith(r) or r in k), None)
        if key is None:
            raise SystemExit(f"mantiq run '{r}' not found; available: {', '.join(real)}")
        msgs = [_canon(m) for m in real[key]["messages"]]
        roles = real[key].get("roles", {})
        cand = sorted(a for a, role in roles.items() if role == "worker") or None
        out.append(make_log(key, msgs, "mantiq", team=prompts.MANTIQ_TEAM, candidates=cand))
    return out


# ChatDev / MAST raw trace parser, vendored from loop9/corpus2_scripts/convert_chatdev.py
_H = re.compile(r'^\[[\d\- :]+ INFO\] ([^:\n]{2,40}): \*\*(.+?)\*\*[ \t]*$', re.M)
_TS = re.compile(r'^\[[\d\- :]+ INFO\]', re.M)
_FENCE = re.compile(r'```[^\n]*\n(.*?)```', re.S)
_MAXLEN = 600


def _collapse_code(t):
    def rep(m):
        lines = m.group(1).rstrip().split('\n')
        return '```\n' + '\n'.join(lines[:2]) + ('\n...' if len(lines) > 2 else '') + '\n```'
    return _FENCE.sub(rep, t)


def parse_mast_trace(tr):
    """Raw ChatDev trajectory text -> [(speaker, to, body)]."""
    msgs = []
    for m in _H.finditer(tr):
        spk, hdr = m.group(1), m.group(2)
        if spk == 'System' or ' on : ' not in hdr:
            continue
        pair = hdr.split(' on : ')[0].split('<->')
        if len(pair) != 2 or spk not in pair:
            continue
        to = pair[1] if pair[0] == spk else pair[0]
        nxt = _TS.search(tr, m.end())
        body = tr[m.end(): nxt.start() if nxt else len(tr)].strip()
        if body.startswith('['):
            k = body.find(']\n\n')
            body = body[k + 3:] if k >= 0 else ''
        body = _collapse_code(body.strip())
        if body.strip():
            msgs.append((spk, to, body))
    return msgs


def _chatdev_team(team, roles):
    ids = ", ".join(f"{a} = {r.replace(' (overseer)', '')}" for a, r in roles.items())
    return f"{team} Agent ids: {ids}. Agents talk in two-party dialogues."


def load_chatdev(path=None, runs=None):
    path = path or data_path("chatdev_corpus2.json")
    d = json.load(open(path))
    out = []
    if isinstance(d, dict):  # corpus2.json style
        def junk(v):
            return sum(("[INST" in m["text"]) or m["text"].strip() == "<INFO>" for m in v["messages"]) / len(v["messages"])
        keys = runs or [next(k for k, v in d.items() if junk(v) < 0.10)]
        for r in keys:
            key = r if r in d else next((k for k in d if k.endswith(r) or r in k), None)
            if key is None:
                raise SystemExit(f"chatdev run '{r}' not found; available: {', '.join(d)}")
            v = d[key]
            out.append(make_log(key, [_canon(m) for m in v["messages"]], "chatdev",
                                team=_chatdev_team(v.get("team", "A simulated software company of LLM agents."), v["roles"])))
    else:  # raw MAST MAD_full_dataset.json: list of traces; --run = trace index
        if not runs:
            raise SystemExit("raw MAST file: pass --run TRACE_INDEX (index of a ChatDev trace in the list)")
        for r in runs:
            idx = int(re.sub(r"\D", "", r))
            x = d[idx]
            if x.get("mas_name") != "ChatDev":
                raise SystemExit(f"trace {r} is not a ChatDev trace")
            tr = x["trace"]["trajectory"]
            raw = parse_mast_trace(tr)
            order = []
            for s, t, _ in raw:
                for a in (s, t):
                    if a not in order:
                        order.append(a)
            ids = {a: 'a%02d' % (k + 1) for k, a in enumerate(order)}
            msgs = []
            for s, t, b in raw:
                if len(b) > _MAXLEN:
                    b = b[:_MAXLEN - 6].rstrip() + ' [...]'
                msgs.append({"agent": ids[s], "to": ids[t], "text": b, "t": None, "inj": False})
            task = re.search(r'\*\*task_prompt\*\*: (.+)', tr)
            team = ("A simulated ChatDev software company of LLM agents holds two-party phase dialogues to build: "
                    + (task.group(1).strip()[:200] if task else "a small program") + ".")
            roles = {ids[a]: a for a in order}
            out.append(make_log(f"chatdev_trace{idx}", msgs, "chatdev", team=_chatdev_team(team, roles)))
    return out


def load_logs(fmt, path=None, runs=None):
    if fmt == "jsonl":
        if not path:
            raise SystemExit("--format jsonl needs --input FILE.jsonl")
        return load_jsonl(path)
    if fmt == "mantiq":
        return load_mantiq(path, runs)
    if fmt == "chatdev":
        return load_chatdev(path, runs)
    raise SystemExit(f"unknown format {fmt}")


def write_jsonl(msgs, path):
    with open(path, "w") as f:
        for i, m in enumerate(msgs):
            f.write(json.dumps({"agent": m["agent"], "to": m["to"], "text": m["text"], "t": m["t"] if m["t"] is not None else i},
                               ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- planting
def load_templates(deal_set="both"):
    doc = json.load(open(data_path("deals.json")))
    want = {"A": "A", "B": "B", "C": "C", "both": "AB", "all": "ABC"}[deal_set]
    return [t for t in doc["templates"] if t["id"][0] in want]


def plant(log, template, a, b, seed, tag):
    """Return a planted copy of `log`: the template's 4 messages (A->B, B->A, A->B, B->A with A/B := a/b) inserted at 4 seeded
    random sorted positions in the 10-90% span (loop2c/loop2d insertion behaviour)."""
    base = log["msgs"]
    n = len(base)
    lo, hi = int(0.1 * n), int(0.9 * n)
    if hi - lo < 4:
        raise SystemExit(f"log {log['id']} has {n} messages; too short to plant 4 messages")
    pos = sorted(rng_for("pos", seed, log["id"], tag).sample(range(lo, hi), 4))
    msgs = [dict(m, inj=False) for m in base]
    for k, p in enumerate(reversed(pos)):
        tm = template["messages"][3 - k]
        frm, to = (a, b) if tm["from"] == "A" else (b, a)
        txt = tm["text"].replace("{A}", a).replace("{B}", b)
        msgs.insert(p, {"agent": frm, "to": to, "text": txt, "t": base[p - 1]["t"] if p else None, "inj": True})
    out = dict(log, msgs=msgs, planted=True, deal=template["id"], pair=[a, b], positions=pos,
               id=f"{log['id']}|canary{tag}|{template['id']}")
    return out


def make_canaries(log, n, seed, deal_set="both", exclude=()):
    """n planted copies of `log`, deterministic given seed. Deals cycle through a seeded shuffle of the template ids so a
    small n covers distinct deals; the agent pair is a seeded pair of agents that appear in the log."""
    cnt = {}
    for m in log["msgs"]:
        for x in (m["agent"], m["to"]):
            if x:
                cnt[x] = cnt.get(x, 0) + 1
    cand = log["candidates"] or sorted(cnt)
    cand = [x for x in cand if cnt.get(x, 0) >= MIN_PLANT_MSGS and x not in exclude]
    if len(cand) < 2:
        raise SystemExit(f"log {log['id']}: fewer than 2 plant-candidate agents (after excludes)")
    templates = load_templates(deal_set)
    by_id = {}
    for t in templates:
        if "fixed_pair" in t and not set(t["fixed_pair"]) <= set(cnt):
            continue
        by_id.setdefault(t["id"], []).append(t)
    ids = sorted(by_id)
    if not ids:
        raise SystemExit(f"no deal template in set '{deal_set}' fits log {log['id']} (set C needs ChatDev agent ids a04/a05/a06)")
    order = list(ids)
    rng_for("order", seed, log["id"]).shuffle(order)
    out = []
    for i in range(n):
        did = order[i % len(order)]
        r = rng_for("canary", seed, log["id"], i)
        t = r.choice(by_id[did])
        if "fixed_pair" in t:
            a, b = t["fixed_pair"]
        else:
            a, b = r.sample(cand, 2)
        out.append(plant(log, t, a, b, seed, i))
    return out


# ---------------------------------------------------------------- chunking
def chunks_of(msgs, chunk=50):
    """loop2c chunks_of: consecutive chunks; a final chunk shorter than 0.4*chunk (20 for 50) is merged into the previous one."""
    n = len(msgs)
    bounds = list(range(0, n, chunk)) + [n]
    segs = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]
    if len(segs) > 1 and segs[-1][1] - segs[-1][0] < int(chunk * 0.4):
        a, _ = segs[-2]
        segs = segs[:-2] + [(a, n)]
    return segs
