"""Contract tests for the multi-provider LLM fallback chain.

Guards the behaviour added after DeepSeek hit "Insufficient Balance" and
every agent failed for ten consecutive runs with no fallback path. The
properties that matter:

- a healthy primary is not bypassed (we are draining a funded balance on
  purpose, so the chain order is the drain order);
- an exhausted provider degrades to the next rather than failing;
- total failure still refuses to write trades.json, so the stale-trades
  guard keeps Account 1 out of the market.
"""
import importlib
import sys
from pathlib import Path

import litellm
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROLE_CHAIN = ("deepseek/deepseek-v4-flash,gemini/gemini-2.5-flash,"
              "anthropic/claude-haiku-4-5")
PM_CHAIN = ("deepseek/deepseek-v4-pro,anthropic/claude-sonnet-5,"
            "gemini/gemini-2.5-flash")

INSUFFICIENT = ('litellm.BadRequestError: DeepseekException - '
                '{"error":{"message":"Insufficient Balance"}}')


@pytest.fixture
def agents(monkeypatch):
    """llm_agents reloaded with known chains and no real network."""
    monkeypatch.setenv("RISK_MODELS", ROLE_CHAIN)
    monkeypatch.setenv("TECH_MODELS", ROLE_CHAIN)
    monkeypatch.setenv("MACRO_MODELS", ROLE_CHAIN)
    monkeypatch.setenv("PM_MODELS", PM_CHAIN)
    monkeypatch.delenv("MOCK_LLM", raising=False)

    module = importlib.import_module("src.llm_agents")
    importlib.reload(module)
    return module


@pytest.fixture
def calls(monkeypatch):
    """Record every model attempted; fail the ones in `failing`."""
    attempted = []
    failing = set()

    class _Message:
        def __init__(self, content):
            self.content = content

    class _Choice:
        def __init__(self, content):
            self.message = _Message(content)

    class _Response:
        def __init__(self, content):
            self.choices = [_Choice(content)]

    def fake_completion(model=None, messages=None, **kwargs):
        attempted.append(model)
        if model in failing:
            raise Exception(INSUFFICIENT)
        return _Response(f"report from {model}")

    monkeypatch.setattr(litellm, "completion", fake_completion)
    return attempted, failing


def test_healthy_primary_is_not_bypassed(agents, calls):
    """Chain order is the drain order - do not skip a funded provider."""
    attempted, _ = calls
    content, model = agents.run_agent_chain("Risk", "p", agents.RISK_MODELS, "c")

    assert model == "deepseek/deepseek-v4-flash"
    assert attempted == ["deepseek/deepseek-v4-flash"], \
        "a working primary must cost exactly one call"


def test_exhausted_primary_degrades_to_next(agents, calls):
    attempted, failing = calls
    failing.add("deepseek/deepseek-v4-flash")

    content, model = agents.run_agent_chain("Risk", "p", agents.RISK_MODELS, "c")

    assert model == "gemini/gemini-2.5-flash"
    assert content == "report from gemini/gemini-2.5-flash"
    assert attempted == ["deepseek/deepseek-v4-flash",
                         "gemini/gemini-2.5-flash"], \
        "must stop at the first success, not keep walking"


def test_chain_is_walked_in_declared_order(agents, calls):
    attempted, failing = calls
    failing.update(["deepseek/deepseek-v4-flash", "gemini/gemini-2.5-flash"])

    _, model = agents.run_agent_chain("Risk", "p", agents.RISK_MODELS, "c")

    assert model == "anthropic/claude-haiku-4-5"
    assert attempted == list(agents.RISK_MODELS)


def test_total_failure_returns_none(agents, calls):
    attempted, failing = calls
    failing.update(agents.RISK_MODELS)

    content, model = agents.run_agent_chain("Risk", "p", agents.RISK_MODELS, "c")

    assert (content, model) == (None, None)
    assert len(attempted) == 3, "every provider should have been tried"


def test_role_agents_return_empty_list_on_total_failure(agents, calls):
    _, failing = calls
    failing.update(agents.RISK_MODELS)

    assert agents.run_role_agents("Risk", "p", agents.RISK_MODELS, "c") == []


def test_role_agents_tag_the_surviving_model(agents, calls):
    _, failing = calls
    failing.add("deepseek/deepseek-v4-flash")

    reports = agents.run_role_agents("Risk", "p", agents.RISK_MODELS, "c")

    assert [r["model"] for r in reports] == ["gemini/gemini-2.5-flash"], \
        "the report must name the model that actually produced it"


def test_pm_chain_is_independent_of_the_role_chain(agents, calls):
    """The PM tier must not silently inherit a cheap role model."""
    _, failing = calls
    failing.add("deepseek/deepseek-v4-pro")

    _, model = agents.run_agent_chain("PM", "p", agents.PM_MODELS, "c")

    assert model == "anthropic/claude-sonnet-5"
    assert "flash" not in model, "PM fell through to a role-tier model"


def test_a_provider_failure_does_not_propagate(agents, calls):
    """run_agent swallows provider errors so the chain can continue."""
    _, failing = calls
    failing.add("deepseek/deepseek-v4-flash")

    assert agents.run_agent("Risk", "p", "deepseek/deepseek-v4-flash",
                            "c") is None
