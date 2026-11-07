"""Model access: OpenAI-compatible client with cost guard, and a deterministic offline fake for --dry-run.

The API key is read from the environment variable named by --api-key-env and is never printed, logged or written.
"""
import asyncio
import hashlib
import os
import re
from collections import defaultdict


class CapReached(Exception):
    pass


class CallResult:
    def __init__(self, text=None, cost=0.0, tin=0, tout=0, err=None, cost_known=True):
        self.text, self.cost, self.tin, self.tout, self.err, self.cost_known = text, cost, tin, tout, err, cost_known


class Budget:
    """Tracks spend; refuses a call when spend + in-flight estimates + this call's estimate would pass the cap."""

    def __init__(self, cap_usd, price_in=None, price_out=None):
        self.cap, self.pin, self.pout = cap_usd, price_in, price_out
        self.spent = 0.0
        self.reserved = 0.0
        self.by_model = defaultdict(lambda: {"usd": 0.0, "calls": 0, "tin": 0, "tout": 0})
        self.avg = {}  # (model, kind) -> (n, mean cost)
        self.gates = {}  # (model, kind) -> Event set after the first call completes (so we know a per-call cost)
        self.unknown_cost_calls = 0
        self.capped = False

    def estimate(self, model, kind, prompt, max_tokens):
        if self.pin is not None and self.pout is not None:
            return len(prompt) / 3.5 * self.pin / 1e6 + min(max_tokens, 1500) * self.pout / 1e6
        n, mean = self.avg.get((model, kind), (0, 0.0))
        return mean

    async def acquire(self, model, kind, prompt, max_tokens):
        key = (model, kind)
        have_price = self.pin is not None and self.pout is not None
        if not have_price and key not in self.avg:
            ev = self.gates.get(key)
            if ev is None:
                self.gates[key] = asyncio.Event()  # first caller probes alone
            else:
                await ev.wait()
        est = self.estimate(model, kind, prompt, max_tokens)
        if self.cap is not None and self.spent + self.reserved + est > self.cap:
            self.capped = True
            ev = self.gates.get(key)
            if ev:
                ev.set()
            raise CapReached(f"cost cap ${self.cap:.2f} (spent ${self.spent:.4f})")
        self.reserved += est
        return est

    def release(self, model, kind, est, res):
        self.reserved = max(0.0, self.reserved - est)
        key = (model, kind)
        if res.err is None:
            self.spent += res.cost
            b = self.by_model[model]
            b["usd"] += res.cost
            b["calls"] += 1
            b["tin"] += res.tin
            b["tout"] += res.tout
            if not res.cost_known:
                self.unknown_cost_calls += 1
            n, mean = self.avg.get(key, (0, 0.0))
            self.avg[key] = (n + 1, (mean * n + res.cost) / (n + 1))
        ev = self.gates.get(key)
        if ev:
            ev.set()


def redact(msg, secret):
    msg = str(msg)
    if secret:
        msg = msg.replace(secret, "[key]")
    return re.sub(r"(sk-|key[-_ ]?)[A-Za-z0-9_\-\*\.]{6,}", "[redacted]", msg)[:220]


class OpenAICompatLLM:
    def __init__(self, base_url, api_key_env, budget, concurrency=8, timeout=300, temperature=None):
        from openai import AsyncOpenAI
        key = os.environ.get(api_key_env or "")
        if not key:
            raise SystemExit(f"API key env var '{api_key_env}' is empty or unset (set it, or use --dry-run)")
        self._key = key
        self.client = AsyncOpenAI(base_url=base_url, api_key=key, timeout=timeout, max_retries=2)
        self.sem = asyncio.Semaphore(concurrency)
        self.budget = budget
        self.temperature = temperature

    async def complete(self, model, prompt, max_tokens, kind, temperature=None):
        est = await self.budget.acquire(model, kind, prompt, max_tokens)
        res = CallResult(err="unattempted")
        try:
            kw = {}
            t = self.temperature if temperature is None else temperature
            if t is not None:
                kw["temperature"] = t
            async with self.sem:
                r = await self.client.chat.completions.create(
                    model=model, messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens,
                    extra_body={"usage": {"include": True}}, **kw)
            u = r.usage
            tin = getattr(u, "prompt_tokens", 0) or 0
            tout = getattr(u, "completion_tokens", 0) or 0
            cost = None
            if u is not None:
                cost = getattr(u, "cost", None)
                if cost is None:
                    cost = (u.model_extra or {}).get("cost")
            known = cost is not None
            if cost is None:
                if self.budget.pin is not None and self.budget.pout is not None:
                    cost, known = (tin * self.budget.pin + tout * self.budget.pout) / 1e6, True
                else:
                    cost = 0.0
            res = CallResult(text=(r.choices[0].message.content or ""), cost=float(cost), tin=tin, tout=tout, cost_known=known)
        except Exception as e:  # noqa: BLE001
            res = CallResult(err=f"{type(e).__name__}: {redact(e, self._key)}")
            res.fatal = type(e).__name__ in ("NotFoundError", "AuthenticationError", "PermissionDeniedError", "BadRequestError")
        finally:
            self.budget.release(model, kind, est, res)
        return res


# --------------------------------------------------------------------------- offline fake (--dry-run)
def _h(*parts):
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


_KW = None


def deal_keywords():
    """Words (>=5 letters) that occur in the planted deal templates but never in the bundled real Mantiq messages."""
    global _KW
    if _KW is None:
        import json
        from .logs import data_path, load_templates
        real = json.load(open(data_path("mantiq_real_messages.json")))
        corpus = " ".join(m["text"].lower() for r in real.values() for m in r["messages"])
        have = set(re.findall(r"[a-z][a-z\-']{4,}", corpus))
        words = set()
        for t in load_templates("all"):
            for m in t["messages"]:
                words |= set(re.findall(r"[a-z][a-z\-']{4,}", m["text"].lower()))
        _KW = frozenset(words - have)
    return _KW


def _hits(text):
    return len(set(re.findall(r"[a-z][a-z\-']{4,}", text.lower())) & deal_keywords())


class FakeLLM:
    """Deterministic offline model. Summarizer: lossy digest that drops/shortens most deal-keyword lines (keep rate depends on
    the model name). Monitor: score grows with the number of distinct deal keywords visible."""

    def __init__(self, budget, price_in=None, price_out=None):
        self.budget = budget

    async def complete(self, model, prompt, max_tokens, kind, temperature=None):
        est = await self.budget.acquire(model, kind, prompt, max_tokens)
        text = self._summarize(model, prompt) if kind == "summarize" else self._monitor(model, prompt)
        tin, tout = len(prompt) // 4, len(text) // 4
        pin, pout = self.budget.pin or 0.0, self.budget.pout or 0.0
        res = CallResult(text=text, cost=(tin * pin + tout * pout) / 1e6, tin=tin, tout=tout)
        self.budget.release(model, kind, est, res)
        return res

    @staticmethod
    def _summarize(model, prompt):
        seg = prompt.split("SEGMENT:", 1)[1].split("\n", 1)[1]
        keep_p = 0.85 if "keeper" in model else 0.15 + 0.4 * _h("keep", model)
        out = []
        for line in seg.splitlines():
            m = re.match(r"\[(\d+)\] (\S+) -> (\S+): (.*)", line)
            if not m:
                continue
            k, a, b, txt = m.groups()
            if _hits(txt) >= 1:
                if _h("deal", model, line) < keep_p:  # kept, but neutralized to its first words
                    out.append(f"{a} and {b} exchanged status: " + " ".join(txt.split()[:9]))
            elif _h("plain", model, line) < 0.25:
                out.append(f"{a} told {b}: " + " ".join(txt.split()[:8]))
        return "Segment summary. " + " ".join(out[:14]) + "\nNo further notes."

    @staticmethod
    def _monitor(model, prompt):
        body = prompt.split("MESSAGES:", 1)[1] if "\nMESSAGES:\n" in prompt else prompt.split("SUMMARY OF MESSAGES", 1)[-1]
        h = _hits(body)
        score = min(95, 4 + 11 * h + int(6 * _h("mon", model, body[:200])))
        return f"Fake monitor saw {h} deal keywords.\nAGENTS: none\nSCORE: {score}"
