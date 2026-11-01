import json
import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import agents  # noqa: E402

KEYS = {"type", "title", "content", "rationale", "depends_on_node_ids"}
SECRET = "sk-test-SECRET-123"


def ctx(pos="Cheap", aud="College students", drop=None):
    nodes = [
        {"id": "r1", "label": "Target users", "text": aud},
        {"id": "r2", "label": "Positioning", "text": pos},
        {"id": "r3", "label": "Hero message", "text": "Hero"},
        {"id": "r4", "label": "Persona messaging", "text": "Persona"},
        {"id": "r5", "label": "Demo page", "text": "Demo"},
    ]
    return {"version": 1, "requirement": {"text": "x", "version": 1},
            "nodes": [n for n in nodes if n["id"] != drop]}


GOOD_HTML = ("<!DOCTYPE html><html><head><style>body{font-family:Arial}</style></head><body>"
             + "<h1>Hi</h1>" * 30 + "</body></html>")


class Fake:
    """Replaces agents._call_llm; records the prompts it was given."""
    def __init__(self, reply):
        self.reply, self.calls = reply, []

    def __call__(self, system, user):
        self.calls.append((system, user))
        return self.reply


def reply_for(agent, **over):
    content = "P" * 80 if agent == "atlas" else GOOD_HTML
    d = {"title": "T", "content": content, "rationale": "Because cheap."}
    d.update(over)
    return json.dumps(d)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for k in ("LLM_MODE", "LLM_API_KEY"):
        monkeypatch.delenv(k, raising=False)


@pytest.mark.parametrize("agent,typ,deps", [
    ("atlas", "persona", ["r1", "r2", "r4"]), ("nova", "demo_html", ["r3", "r5"])])
def test_shape(monkeypatch, agent, typ, deps):
    monkeypatch.setattr(agents, "_call_llm", Fake(reply_for(agent)))
    out = agents.generate_with_llm(agent, ctx(), None)
    assert set(out) == KEYS and out["type"] == typ and out["depends_on_node_ids"] == deps
    assert all(isinstance(out[k], str) for k in ("title", "content", "rationale"))


def test_prompts_differ_and_labels_stripped(monkeypatch):
    f = Fake(reply_for("atlas"))
    monkeypatch.setattr(agents, "_call_llm", f)
    agents.generate_with_llm("atlas", ctx("Positioning: cheap", "Target users: college students"), None)
    agents.generate_with_llm("atlas", ctx("Positioning: fast and trusted"), None)
    p1, p2 = f.calls[0][1], f.calls[1][1]
    assert p1 != p2
    assert '"cheap"' in p1 and '"college students"' in p1
    assert "Positioning:" not in p1 and "Target users:" not in p1


def test_code_fences_stripped(monkeypatch):
    monkeypatch.setattr(agents, "_call_llm", Fake("```json\n" + reply_for("atlas") + "\n```"))
    assert agents.generate_with_llm("atlas", ctx(), None)["title"] == "T"


@pytest.mark.parametrize("bad", ["not json", "[]", reply_for("atlas", title=""),
                                 reply_for("atlas", content="short")])
def test_bad_output_raises(monkeypatch, bad):
    monkeypatch.setattr(agents, "_call_llm", Fake(bad))
    with pytest.raises(agents.LLMError):
        agents.generate_with_llm("atlas", ctx(), None)


@pytest.mark.parametrize("drop", ["r1", "r2"])
def test_missing_node_raises(monkeypatch, drop):
    monkeypatch.setattr(agents, "_call_llm", Fake(reply_for("atlas")))
    with pytest.raises(agents.LLMError):
        agents.generate_with_llm("atlas", ctx(drop=drop), None)


def test_unknown_agent():
    with pytest.raises(ValueError):
        agents.generate_with_llm("bob", ctx(), None)


@pytest.mark.parametrize("snippet", [
    "<script>x</script>", '<link rel="stylesheet" href="a.css">', "<iframe></iframe>",
    '<img src="http://x/y.png">', "<style>@import 'a.css';</style>",
    "<div style=\"background:url(http://x/a.png)\"></div>", '<a href="http://x">x</a>',
    '<div onclick="x()">x</div>'])
def test_bad_html_rejected(monkeypatch, snippet):
    html = GOOD_HTML.replace("</body>", snippet + "</body>")
    monkeypatch.setattr(agents, "_call_llm", Fake(reply_for("nova", content=html)))
    with pytest.raises(agents.LLMError):
        agents.generate_with_llm("nova", ctx(), None)


def test_html_must_start_with_doctype(monkeypatch):
    monkeypatch.setattr(agents, "_call_llm", Fake(reply_for("nova", content="<div>" + "x" * 300 + "</div>")))
    with pytest.raises(agents.LLMError):
        agents.generate_with_llm("nova", ctx(), None)


def test_instruction_in_prompt_and_rationale(monkeypatch):
    f = Fake(reply_for("nova", rationale="Cheap, with warmer tone as asked."))
    monkeypatch.setattr(agents, "_call_llm", f)
    out = agents.generate_with_llm("nova", ctx(), "make it warmer")
    assert "make it warmer" in f.calls[0][1] and "warmer" in out["rationale"]


def test_key_never_logged(monkeypatch, caplog):
    monkeypatch.setenv("LLM_API_KEY", SECRET)
    monkeypatch.setattr(agents, "_call_llm", Fake("garbage"))
    with caplog.at_level(logging.DEBUG), pytest.raises(agents.LLMError):
        agents.generate_with_llm("atlas", ctx(), None)
    assert SECRET not in caplog.text


@pytest.mark.parametrize("agent", ["atlas", "nova"])
def test_mock_mode_no_key(monkeypatch, agent):
    monkeypatch.setenv("LLM_MODE", "mock")
    monkeypatch.setattr(agents, "_call_llm", lambda *a: pytest.fail("API called"))
    cheap = agents.generate_with_llm(agent, ctx("Cheap"), None)
    fast = agents.generate_with_llm(agent, ctx("fast and trusted"), None)
    assert set(cheap) == KEYS and cheap["content"] != fast["content"]
    assert "instr-steer" in agents.generate_with_llm(agent, ctx(), "instr-steer")["rationale"]


def test_no_key_no_mock_raises():
    with pytest.raises(agents.LLMError):
        agents.generate_with_llm("atlas", ctx(), None)


# ------------------------------------------------------------------ retries
class FakeResp:
    def __init__(self, status, headers=None):
        self.status_code = status
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeHttpx:
    def __init__(self, *statuses):
        self.statuses = list(statuses)
        self.calls = 0

    def post(self, url, **kw):
        self.calls += 1
        s = self.statuses.pop(0)
        return FakeResp(s[0], s[1]) if isinstance(s, tuple) else FakeResp(s)


@pytest.fixture
def sleeps(monkeypatch):
    waited = []
    monkeypatch.setattr(agents.time, "sleep", waited.append)
    return waited


def test_retry_503_then_success(sleeps):
    h = FakeHttpx(503, 503, 200)
    assert agents._post_with_retry(h, "u").status_code == 200
    assert h.calls == 3 and len(sleeps) == 2
    assert 1.0 <= sleeps[0] < 1.3 and 2.0 <= sleeps[1] < 2.3  # exponential backoff


def test_retry_gives_up_after_max_attempts(sleeps):
    h = FakeHttpx(503, 503, 503)
    with pytest.raises(RuntimeError, match="503"):
        agents._post_with_retry(h, "u")
    assert h.calls == agents.MAX_ATTEMPTS


@pytest.mark.parametrize("status", [400, 401, 403, 404])
def test_no_retry_on_client_errors(sleeps, status):
    h = FakeHttpx(status)
    with pytest.raises(RuntimeError):
        agents._post_with_retry(h, "u")
    assert h.calls == 1 and not sleeps


def test_retry_after_header_is_capped(sleeps):
    h = FakeHttpx((429, {"retry-after": "60"}), 200)
    agents._post_with_retry(h, "u")
    assert agents.RETRY_MAX_DELAY <= sleeps[0] < agents.RETRY_MAX_DELAY + 0.3


def test_no_retry_when_budget_spent(sleeps, monkeypatch):
    monkeypatch.setattr(agents, "RETRY_BUDGET_SECONDS", 0.5)  # first backoff (>=1s) exceeds it
    h = FakeHttpx(503, 200)
    with pytest.raises(RuntimeError, match="503"):
        agents._post_with_retry(h, "u")
    assert h.calls == 1 and not sleeps
