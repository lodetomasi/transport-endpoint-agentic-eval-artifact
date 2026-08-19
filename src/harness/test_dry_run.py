#!/usr/bin/env python3
"""test_dry_run.py -- integration smoke test for agent_loop.py WITHOUT any
network call (no Bedrock, no GhidraMCP). Stubs both llm_client.chat and
GhidraMCPClient so the harness's own bookkeeping (message history, turn
budget, submit_candidate handling, infra-failure detection, trajectory
logging) can be exercised and checked before either real blocker
(credentials, GhidraMCP-under-Docker) is resolved.

This does NOT validate that the real Bedrock/GhidraMCP integration works --
only that agent_loop.py's control flow is not obviously broken.

Run: python3 harness/test_dry_run.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "llm"))

import llm_client  # noqa: E402
from agent_loop import run_agent  # noqa: E402
from ghidra_mcp_client import GhidraMCPClient  # noqa: E402


class StubGhidraClient(GhidraMCPClient):
    def call(self, tool_name: str, arguments: dict) -> str:
        return f"[stub result for {tool_name}({arguments})]"


def make_stub_chat(scripted_responses):
    """Returns a stand-in for llm_client.chat that returns pre-scripted
    ChatResult objects in sequence, one per call, ignoring the actual args
    beyond recording call count."""
    calls = {"n": 0}

    def _stub_chat(messages, tools=None, model=None, max_tokens=1024, temperature=None, provider=None):
        idx = calls["n"]
        calls["n"] += 1
        if idx >= len(scripted_responses):
            raise AssertionError(f"stub chat called more times ({idx + 1}) than scripted ({len(scripted_responses)})")
        return scripted_responses[idx]

    return _stub_chat, calls


def chat_result(content="", tool_calls=None, stop_reason="end_turn", input_tokens=100, output_tokens=50):
    tool_calls = tool_calls or []
    raw = {"stopReason": stop_reason}
    return llm_client.ChatResult(
        content=content,
        tool_calls=tool_calls,
        usage={"input_tokens": input_tokens, "output_tokens": output_tokens},
        model="test-model",
        provider="bedrock",
        cost_usd=0.001,
        is_cost_estimate=True,
        raw=raw,
    )


def test_normal_submission_within_budget():
    """Agent calls a tool on turn 1, submits candidate on turn 2, budget is 4."""
    responses = [
        chat_result(
            content="Let me look at the functions.",
            tool_calls=[llm_client.ToolCall(id="t1", name="list_functions", arguments={})],
            stop_reason="tool_use",
        ),
        chat_result(
            content="",
            tool_calls=[
                llm_client.ToolCall(
                    id="t2", name="submit_candidate", arguments={"c_source": "int main(){return 0;}"}
                )
            ],
            stop_reason="tool_use",
        ),
    ]
    stub_chat, calls = make_stub_chat(responses)
    llm_client.chat = stub_chat  # monkeypatch the module-level function agent_loop imported

    result = run_agent(
        binary_id="prog01_bubble_sort",
        n_turns=4,
        model="test-model",
        provider="bedrock",
        max_tokens=4096,
        temperature=None,
        ghidra_client=StubGhidraClient(),
    )

    assert result.submitted_via_tool is True, "expected submit_candidate to be recorded"
    assert result.candidate_source == "int main(){return 0;}", result.candidate_source
    assert len(result.turns) == 2, f"expected loop to stop early at turn 2, got {len(result.turns)} turns"
    assert calls["n"] == 2
    assert result.infra_failure is False
    print("test_normal_submission_within_budget: PASS")


def test_fallback_when_budget_exhausted_without_submit():
    """Agent never calls submit_candidate; after n_turns=2, fallback to last text."""
    responses = [
        chat_result(content="thinking...", tool_calls=[], stop_reason="end_turn"),
        chat_result(content="int main(){return 1;}", tool_calls=[], stop_reason="end_turn"),
    ]
    stub_chat, calls = make_stub_chat(responses)
    llm_client.chat = stub_chat

    result = run_agent(
        binary_id="prog02_quicksort",
        n_turns=2,
        model="test-model",
        provider="bedrock",
        max_tokens=4096,
        temperature=None,
        ghidra_client=StubGhidraClient(),
    )

    assert result.submitted_via_tool is False
    assert result.candidate_source == "int main(){return 1;}"
    assert len(result.turns) == 2
    print("test_fallback_when_budget_exhausted_without_submit: PASS")


def test_infra_failure_truncated_empty_completion():
    """Completion truncated by max_tokens with no text and no tool call ->
    must be flagged infra_failure, not silently treated as pass_rate=0."""
    responses = [
        chat_result(content="", tool_calls=[], stop_reason="max_tokens", output_tokens=4096),
    ]
    stub_chat, calls = make_stub_chat(responses)
    llm_client.chat = stub_chat

    result = run_agent(
        binary_id="prog03_binary_search",
        n_turns=4,
        model="test-model",
        provider="bedrock",
        max_tokens=4096,
        temperature=None,
        ghidra_client=StubGhidraClient(),
    )

    assert result.infra_failure is True, "expected infra_failure to be detected"
    assert result.candidate_source is None
    assert calls["n"] == 1, "should stop immediately on infra failure, not burn remaining turns"
    print("test_infra_failure_truncated_empty_completion: PASS")


def test_provider_guard_rejects_databricks():
    """The harness must refuse provider='databricks' even if asked."""
    try:
        run_agent(
            binary_id="x",
            n_turns=1,
            model="whatever",
            provider="databricks",
            max_tokens=1024,
            temperature=None,
            ghidra_client=StubGhidraClient(),
        )
        raise AssertionError("expected ValueError for provider='databricks'")
    except ValueError as e:
        assert "not allowed" in str(e)
    print("test_provider_guard_rejects_databricks: PASS")


if __name__ == "__main__":
    test_normal_submission_within_budget()
    test_fallback_when_budget_exhausted_without_submit()
    test_infra_failure_truncated_empty_completion()
    test_provider_guard_rejects_databricks()
    print("\nAll dry-run tests passed (no network calls made).")
