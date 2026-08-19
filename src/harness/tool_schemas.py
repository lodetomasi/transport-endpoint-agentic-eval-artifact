"""OpenAI-style tool schemas offered to the LLM in the mini-pilot agent loop.

Matches the GhidraMCP endpoints implemented in ghidra_mcp_client.py, plus one
harness-local tool (`submit_candidate`) the agent must call to hand back its
final reconstructed C source. `submit_candidate` is not a Ghidra tool -- it
is how the harness captures the agent's answer without relying on parsing
free-text at the end of the last turn.
"""
from __future__ import annotations

GHIDRA_TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "list_functions",
            "description": "List all function names identified in the current binary.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "decompile_function",
            "description": "Decompile a named function and return its pseudocode (C-like).",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "Function name, e.g. 'main' or 'FUN_00101234'."}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_strings",
            "description": "List string constants found in the binary, optionally filtered by substring.",
            "parameters": {
                "type": "object",
                "properties": {
                    "offset": {"type": "integer", "default": 0},
                    "limit": {"type": "integer", "default": 2000},
                    "filter": {"type": "string"},
                },
            },
        },
    },
]

# NOTA (correzione del 2026-08-10, difetto F1 rilevato in review metodologica):
# `get_function_xrefs` e `disassemble_function` sono stati RIMOSSI da questo schema.
# Erano offerti all'agente ma, con GhidraStaticClient, restituivano SEMPRE un errore
# ("non disponibile nel dump statico"). Ogni loro invocazione bruciava un turno del
# budget N per zero informazione — un costo asimmetrico imposto ai soli bracci
# agentici, che riduceva il budget effettivo sotto quello nominale e falsava proprio
# il confronto su cui poggia la conclusione principale.
# Offrire un tool che non puo' funzionare non e' una limitazione di capacita': e' una
# trappola nel disegno sperimentale.

SUBMIT_CANDIDATE_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "submit_candidate",
        "description": (
            "Submit your final reconstructed C source for the whole program. "
            "Call this exactly once, when you are ready to give your final answer "
            "(you have a fixed budget of turns -- do not wait past the last one)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "c_source": {
                    "type": "string",
                    "description": "Complete, compilable C source implementing the program's observed behavior.",
                }
            },
            "required": ["c_source"],
        },
    },
}

ALL_TOOLS: list[dict] = GHIDRA_TOOLS + [SUBMIT_CANDIDATE_TOOL]
