"""Smoke test for llm_client.py -- run before trusting it in the harness.

Exercises, for each model in MODELS below:
  (a) a plain chat call with no tools
  (b) a chat call with one fictitious tool, checking the model emits a
      well-formed tool_call (id, name, JSON-parsed arguments)
  (c) prints the estimated cost of both calls

This spends real money (a few cents total). Run with:
    python3 smoke_test.py
"""
from __future__ import annotations

import json
import sys

import llm_client as lc

FICTITIOUS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a named city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name, e.g. 'Paris'."}},
            "required": ["city"],
        },
    },
}

MODELS = [
    ("databricks", "databricks-qwen35-122b-a10b"),
    ("databricks", "databricks-gpt-oss-120b"),
]


def run_one(provider: str, model: str) -> bool:
    ok = True
    print(f"\n{'=' * 70}\n{provider}:{model}\n{'=' * 70}")

    # (a) plain chat, no tools
    # NOTE: max_tokens=1024, not a small number. DISCOVERED (2026-08-09):
    # databricks-qwen35-122b-a10b always reasons before responding (reasoning
    # cannot be disabled -- per Databricks model docs) and the reasoning
    # trace counts against max_tokens. With max_tokens=200 the model spent
    # the entire budget on reasoning and returned finish_reason="length"
    # with an EMPTY final-answer text block. Budget max_tokens generously
    # for reasoning models in the harness (task #5), not just for the
    # expected answer length.
    print("\n-- (a) plain chat, no tools --")
    try:
        result = lc.chat(
            messages=[{"role": "user", "content": "Reply with exactly one short sentence: what is 2+2?"}],
            tools=None,
            model=model,
            provider=provider,
            max_tokens=1024,
        )
        print(f"content: {result.content!r}")
        print(f"usage: {result.usage}")
        print(f"cost_usd: {result.cost_usd:.6f} (is_estimate={result.is_cost_estimate})")
        if not result.content.strip():
            print("FAIL: empty content on plain chat")
            ok = False
    except Exception as e:
        print(f"FAIL: plain chat raised {e!r}")
        return False

    # (b) chat with a fictitious tool
    print("\n-- (b) chat with a fictitious tool --")
    try:
        result = lc.chat(
            messages=[
                {
                    "role": "system",
                    "content": "You must use the get_weather tool to answer any question about weather. Do not answer from your own knowledge.",
                },
                {"role": "user", "content": "What's the weather like in Paris right now?"},
            ],
            tools=[FICTITIOUS_TOOL],
            model=model,
            provider=provider,
            max_tokens=500,
        )
        print(f"content: {result.content!r}")
        print(f"tool_calls: {result.tool_calls!r}")
        print(f"usage: {result.usage}")
        print(f"cost_usd: {result.cost_usd:.6f} (is_estimate={result.is_cost_estimate})")

        if not result.tool_calls:
            print("FAIL: no tool_call emitted")
            ok = False
        else:
            tc = result.tool_calls[0]
            if not tc.id or not tc.name:
                print(f"FAIL: malformed tool_call (missing id or name): {tc!r}")
                ok = False
            elif tc.name != "get_weather":
                print(f"FAIL: wrong tool name called: {tc.name!r}")
                ok = False
            elif "city" not in tc.arguments:
                print(f"FAIL: tool_call arguments missing 'city': {tc.arguments!r}")
                ok = False
            else:
                print(f"OK: well-formed tool_call id={tc.id!r} name={tc.name!r} arguments={tc.arguments!r}")
    except Exception as e:
        print(f"FAIL: tool-calling chat raised {e!r}")
        return False

    return ok


def main() -> int:
    results = {f"{p}:{m}": run_one(p, m) for p, m in MODELS}
    print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")
    all_ok = True
    for key, ok in results.items():
        print(f"{key}: {'PASS' if ok else 'FAIL'}")
        all_ok = all_ok and ok
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
