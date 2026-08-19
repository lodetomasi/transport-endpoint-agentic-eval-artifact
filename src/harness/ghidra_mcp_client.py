"""Thin HTTP client for the GhidraMCP plugin's REST-ish API.

GhidraMCP (github.com/LaurieWired/GhidraMCP) ships an MCP stdio/SSE bridge
(`bridge_mcp_ghidra.py`) that itself just does plain HTTP GET/POST calls
against a Ghidra plugin server (default `http://127.0.0.1:8080/`). Since our
agent loop already speaks OpenAI-style tool-calling directly to the LLM
client (see llm/llm_client.py), we skip the extra MCP protocol envelope and
call the same HTTP endpoints directly. Endpoint names/params below are taken
verbatim from bridge_mcp_ghidra.py (fetched 2026-08-09, GhidraMCP main
branch) so this client matches upstream exactly.

KNOWN BLOCKER (see ../docker/BLOCKERS.md): GhidraMCP's HTTP server is started
by a Ghidra GUI plugin (CodeBrowser tool). It is not activated in plain
`analyzeHeadless` mode (upstream issue LaurieWired/GhidraMCP#75). This client
has NOT been exercised against a live server in this environment. It is
written directly against the documented/observed endpoint contract so it is
ready to use once a server is reachable (interactive GUI under Xvfb, or a
headless-capable fork, per user's decision).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


class GhidraMCPError(RuntimeError):
    pass


@dataclass
class GhidraMCPClient:
    base_url: str = "http://127.0.0.1:8080/"
    timeout_s: float = 30.0

    def _get(self, endpoint: str, params: dict | None = None) -> list:
        url = urllib.parse.urljoin(self.base_url, endpoint)
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            url = f"{url}?{urllib.parse.urlencode(clean)}"
        try:
            with urllib.request.urlopen(url, timeout=self.timeout_s) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.URLError as e:
            raise GhidraMCPError(f"GET {url} failed: {e}") from e
        return body.splitlines() if body else []

    def _post(self, endpoint: str, data: dict | str) -> str:
        url = urllib.parse.urljoin(self.base_url, endpoint)
        payload = json.dumps(data).encode("utf-8") if isinstance(data, dict) else str(data).encode("utf-8")
        req = urllib.request.Request(url, data=payload, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.URLError as e:
            raise GhidraMCPError(f"POST {url} failed: {e}") from e

    # --- tool surface used by the mini-pilot harness (subset of GhidraMCP) ---

    def list_functions(self) -> list[str]:
        return self._get("list_functions")

    def decompile_function(self, name: str) -> str:
        return self._post("decompile", name)

    def get_function_xrefs(self, name: str, offset: int = 0, limit: int = 100) -> list[str]:
        return self._get("function_xrefs", {"name": name, "offset": offset, "limit": limit})

    def list_strings(self, offset: int = 0, limit: int = 2000, filter: str | None = None) -> list[str]:
        return self._get("strings", {"offset": offset, "limit": limit, "filter": filter})

    def disassemble_function(self, address: str) -> list[str]:
        return self._get("disassemble_function", {"address": address})

    def call(self, tool_name: str, arguments: dict) -> str:
        """Dispatch a tool-call by name (as emitted by the LLM) to the matching method."""
        dispatch = {
            "list_functions": lambda: self.list_functions(),
            "decompile_function": lambda: self.decompile_function(arguments["name"]),
            "get_function_xrefs": lambda: self.get_function_xrefs(
                arguments["name"], arguments.get("offset", 0), arguments.get("limit", 100)
            ),
            "list_strings": lambda: self.list_strings(
                arguments.get("offset", 0), arguments.get("limit", 2000), arguments.get("filter")
            ),
            "disassemble_function": lambda: self.disassemble_function(arguments["address"]),
        }
        if tool_name not in dispatch:
            raise GhidraMCPError(f"unknown tool {tool_name!r}")
        result = dispatch[tool_name]()
        return result if isinstance(result, str) else "\n".join(result)
