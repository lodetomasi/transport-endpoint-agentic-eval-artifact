"""Minimal chat-completion + tool-calling client for the S1 mini-pilot agent.

Two interchangeable providers, selected by an explicit ``provider`` argument
(or the ``LLM_PROVIDER`` env var -- there is no silent default, since which
provider serves a run is an experimental decision, not a code default):

  - "databricks": Databricks pay-per-token serving endpoints, via the
    Databricks SDK's OpenAI-compatible client
    (``WorkspaceClient(profile=...).serving_endpoints.get_open_ai_client()``).
    Verified tool-capable endpoints (2026-08-09): databricks-qwen35-122b-a10b,
    databricks-gpt-oss-120b, databricks-claude-haiku-4-5.
    Do NOT use `databricks serving-endpoints query` from the CLI -- it does
    not support the `tools` field. Do NOT create clusters or jobs; this
    module only ever calls already-provisioned serving endpoints.

  - "bedrock": AWS Bedrock via the Converse API (works uniformly across
    model families, unlike the Anthropic-only InvokeModel envelope).

Public API (KISS: one function, one config file, no framework):

    chat(messages, tools=None, model=..., max_tokens=..., temperature=None,
         provider=None) -> ChatResult

Message format (always OpenAI-style, regardless of provider -- the Bedrock
path converts internally):

    [{"role": "system", "content": "..."},
     {"role": "user", "content": "..."},
     {"role": "assistant", "content": "...", "tool_calls": [...]},   # optional
     {"role": "tool", "tool_call_id": "...", "content": "..."}]      # optional

Tool format (always OpenAI-style function-calling schema):

    [{"type": "function",
      "function": {"name": "...", "description": "...", "parameters": {...}}}]

Use `ChatResult.to_assistant_message()` and `tool_result_message(...)` to
build the next turn's messages without hand-rolling the OpenAI envelope.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_CONFIG_DIR = Path(__file__).parent / "configs"
# Le tariffe stanno in configs/ del PROGETTO, non accanto al client: sono una
# decisione dello studio (quale endpoint, quale SKU, con quale fonte), non una
# proprieta' del codice. C2_PRICING per un progetto che le tiene altrove.
_PRICING_PATH = Path(os.environ.get(
    "C2_PRICING",
    Path(__file__).resolve().parents[2] / "configs" / "pricing.json"))

_DEFAULT_DATABRICKS_PROFILE = "<profilo-databricks>"  # only known-working profile on this host (SPEC-mini-pilot.md)
_DEFAULT_BEDROCK_REGION = "us-east-1"
_DEFAULT_AZURE_API_VERSION = "2025-04-01-preview"  # the version the transport probe ran on


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ChatResult:
    """Normalized response shape, identical across providers."""

    content: str
    tool_calls: list[ToolCall]
    usage: dict[str, int]  # {"input_tokens": int, "output_tokens": int}
    model: str
    provider: str
    cost_usd: float
    is_cost_estimate: bool  # True if the pricing entry used is marked as a guess
    raw: Any = field(repr=False)  # provider-native response object/dict, for audit

    def to_assistant_message(self) -> dict[str, Any]:
        """Build the OpenAI-style assistant message to append to history.

        NOTA (bug reale osservato il 2026-08-09 su databricks-gpt-oss-120b): i modelli
        di reasoning possono restituire un turno con SOLO blocchi di reasoning, quindi
        `content` vuoto e nessuna tool call. Rimandare indietro un messaggio del genere
        fa fallire la richiesta successiva con
        `400 BAD_REQUEST: Message must contain either 'content' or a 'tool_call'`,
        e il run intero veniva registrato come pass_rate=0 — indistinguibile da un
        fallimento genuino dell'agente, cioe' esattamente la corruzione silenziosa dei
        dati che il mini-pilot deve evitare. Si sostituisce con un placeholder esplicito
        cosi' la conversazione resta valida e la traccia resta onesta.
        """
        content = self.content or None
        if not content and not self.tool_calls:
            content = "(nessun output testuale in questo turno)"
        msg: dict[str, Any] = {"role": "assistant", "content": content}
        if self.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                }
                for tc in self.tool_calls
            ]
        return msg


def tool_result_message(tool_call_id: str, content: str) -> dict[str, Any]:
    """Build the OpenAI-style 'tool' message carrying a tool's output."""
    return {"role": "tool", "tool_call_id": tool_call_id, "content": content}


def _load_pricing() -> dict[str, Any]:
    with open(_PRICING_PATH) as f:
        return json.load(f)


def get_pricing_entry(provider: str, model: str) -> dict[str, Any]:
    """Raise if the (provider, model) pair has no entry -- fail loud, not silent."""
    pricing = _load_pricing()
    key = f"{provider}:{model}"
    entry = pricing.get(key)
    if entry is None:
        raise KeyError(
            f"No pricing entry for {key!r} in {_PRICING_PATH}. "
            "Add one (with a cited source, or is_estimate=true) before running "
            "paid calls against this model -- costs must never be silently unknown."
        )
    return entry


def estimate_cost_usd(model: str, provider: str, input_tokens: int, output_tokens: int) -> tuple[float, bool]:
    """Return (usd_cost, is_estimate) for the given token usage.

    is_estimate mirrors the "is_estimate" flag on the pricing.json entry --
    True means the price is a documented guess, not a confirmed rate.
    """
    entry = get_pricing_entry(provider, model)
    if entry["kind"] == "dbu":
        usd_per_dbu = _load_pricing()["_meta"]["databricks_usd_per_dbu"]
        in_price = entry["input_dbu_per_mtok"] * usd_per_dbu
        out_price = entry["output_dbu_per_mtok"] * usd_per_dbu
    elif entry["kind"] == "usd_direct":
        in_price = entry["input_usd_per_mtok"]
        out_price = entry["output_usd_per_mtok"]
    else:
        raise ValueError(f"unknown pricing entry kind {entry['kind']!r} for {provider}:{model}")
    usd = input_tokens / 1_000_000 * in_price + output_tokens / 1_000_000 * out_price
    return usd, bool(entry.get("is_estimate", False))


def chat(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float | None = None,
    provider: str | None = None,
) -> ChatResult:
    """Single chat-completion call, normalized across providers.

    `provider` and `model` are required, either as arguments or via the
    LLM_PROVIDER / LLM_MODEL env vars -- there is no default model, since
    silently picking one would be an unrecorded experimental decision.
    """
    provider = provider or os.environ.get("LLM_PROVIDER")
    if not provider:
        raise ValueError(
            "provider is required: pass provider='databricks'|'bedrock', "
            "or set the LLM_PROVIDER env var. No default is assumed."
        )
    model = model or os.environ.get("LLM_MODEL")
    if not model:
        raise ValueError(
            "model is required: pass model=..., or set the LLM_MODEL env var. "
            f"See {_PRICING_PATH} for models with a known pricing entry."
        )

    # The pricing check runs BEFORE the call, not after it. It used to sit next to
    # estimate_cost_usd below, which meant a model with no declared tariff was billed
    # for one call and only then refused -- measured at 4.51s against
    # databricks-claude-opus-5, i.e. the round trip happened. A guard that fires after
    # the money is spent is a report, not a guard, and the distinction is invisible
    # from the outside because both spellings raise the same KeyError.
    get_pricing_entry(provider, model)

    if provider == "databricks":
        content, tool_calls, usage, raw = _chat_databricks(messages, tools, model, max_tokens, temperature)
    elif provider == "bedrock":
        content, tool_calls, usage, raw = _chat_bedrock(messages, tools, model, max_tokens, temperature)
    elif provider == "azure":
        content, tool_calls, usage, raw = _chat_azure(messages, tools, model, max_tokens, temperature)
    else:
        raise ValueError(
            f"unknown provider {provider!r}; must be 'databricks', 'bedrock' or 'azure'"
        )

    cost_usd, is_estimate = estimate_cost_usd(model, provider, usage["input_tokens"], usage["output_tokens"])

    return ChatResult(
        content=content,
        tool_calls=tool_calls,
        usage=usage,
        model=model,
        provider=provider,
        cost_usd=cost_usd,
        is_cost_estimate=is_estimate,
        raw=raw,
    )


# ---------------------------------------------------------------------------
# Databricks: OpenAI-compatible client via the Databricks SDK.
# ---------------------------------------------------------------------------


def _chat_databricks(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None,
    model: str,
    max_tokens: int,
    temperature: float | None,
) -> tuple[str, list[ToolCall], dict[str, int], Any]:
    try:
        from databricks.sdk import WorkspaceClient
    except ImportError as e:
        raise RuntimeError("databricks-sdk is required for provider='databricks' (pip install databricks-sdk).") from e

    profile = os.environ.get("DATABRICKS_PROFILE", _DEFAULT_DATABRICKS_PROFILE)
    w = WorkspaceClient(profile=profile)
    oc = w.serving_endpoints.get_open_ai_client()

    kwargs: dict[str, Any] = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if temperature is not None:
        kwargs["temperature"] = temperature
    if tools:
        kwargs["tools"] = tools

    response = oc.chat.completions.create(**kwargs)
    choice = response.choices[0]
    msg = choice.message
    content = _extract_databricks_content(msg.content)

    tool_calls: list[ToolCall] = []
    for tc in msg.tool_calls or []:
        raw_args = tc.function.arguments or "{}"
        try:
            args = json.loads(raw_args)
        except json.JSONDecodeError:
            # Model emitted malformed JSON in a tool call -- surface it, don't
            # silently drop the call or crash the whole response.
            args = {"_unparsed_arguments": raw_args}
        tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))

    usage = response.usage
    usage_dict = {
        "input_tokens": int(usage.prompt_tokens) if usage else 0,
        "output_tokens": int(usage.completion_tokens) if usage else 0,
    }

    raw = response.model_dump() if hasattr(response, "model_dump") else response
    return content, tool_calls, usage_dict, raw


def _extract_databricks_content(content: Any) -> str:
    """Normalize `message.content` to a plain string.

    DISCOVERED (2026-08-09, smoke test): the reasoning-capable Databricks
    endpoints (databricks-qwen35-122b-a10b, databricks-gpt-oss-120b) do NOT
    return a plain string in `message.content` as the OpenAI chat schema
    specifies. Instead they return a list of content blocks, e.g.
    [{"type": "reasoning", "summary": [...]}, {"type": "text", "text": "..."}]
    -- the model's chain-of-thought surfaced as a separate block alongside
    the actual answer. This is not documented OpenAI-compatible behaviour;
    it is provider-specific. We keep only "text"-typed blocks for `content`
    (the reasoning trace is still available for audit in `raw`).
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = [block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"]
        return "\n".join(text_parts)
    raise TypeError(f"unexpected message.content type from Databricks: {type(content)!r}")


# ---------------------------------------------------------------------------
# Azure AI Foundry: the OpenAI reference implementation, reached through a
# deployment name rather than a model id.
#
# The third serving infrastructure exists so that the same model can be
# measured on two of them. With one endpoint, model and infrastructure are
# perfectly confounded and every observation is attributable to both: the
# -10.7pp that separates the two tool-call transports for Haiku is, on a single
# provider, equally a property of Haiku and a property of that provider's
# OpenAI-compatible shim. The overlap that makes the difference readable is the
# open-weights one -- gpt-oss-120b, Llama-3.3-70B -- because each cloud hosts
# those weights itself, so a null result means the infrastructures agree rather
# than that they are the same infrastructure wearing two names.
# ---------------------------------------------------------------------------


def _chat_azure(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None,
    model: str,
    max_tokens: int,
    temperature: float | None,
) -> tuple[str, list[ToolCall], dict[str, int], Any]:
    """`model` is the DEPLOYMENT name, not the model id.

    Azure addresses a model by what the account called it when it was deployed,
    so two accounts can serve the same weights under different names and one
    account can serve two versions under one name. The deployment name is
    therefore not sufficient provenance on its own: the resolved model and
    version come back in `raw` and belong in the result record.
    """
    try:
        from openai import AzureOpenAI
    except ImportError as e:
        raise RuntimeError("openai is required for provider='azure' (pip install openai).") from e

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    if not endpoint or not api_key:
        raise RuntimeError(
            "provider='azure' needs AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY. "
            "Read them from the account -- they are never committed:\n"
            "  az cognitiveservices account show -n <account> -g <rg> "
            "--query properties.endpoint -o tsv\n"
            "  az cognitiveservices account keys list -n <account> -g <rg> --query key1 -o tsv"
        )

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", _DEFAULT_AZURE_API_VERSION),
    )

    # MEASURED 2026-08-13 on agentic-eval-we-01, westeurope, api-version
    # 2025-04-01-preview: `gpt-5.1` rejects `max_tokens` with HTTP 400, while
    # gpt-oss-120b, Llama-3.3-70B and Llama-4-Maverick-FP8 accept both spellings.
    # `max_completion_tokens` is therefore the one form that works everywhere,
    # and it is sent unconditionally. A try-one-then-the-other fallback would
    # make the request that was actually issued depend on an error path, which
    # is precisely the kind of thing that stops being visible in a result file.
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": max_tokens,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature
    if tools:
        kwargs["tools"] = tools

    response = client.chat.completions.create(**kwargs)
    choice = response.choices[0]
    msg = choice.message
    # Same normalization as Databricks: reasoning-capable endpoints return
    # content blocks instead of a string. Whether a given model does that HERE
    # and not THERE is a finding rather than a nuisance, so the untouched
    # response stays in `raw`.
    content = _extract_databricks_content(msg.content)

    tool_calls: list[ToolCall] = []
    for tc in msg.tool_calls or []:
        raw_args = tc.function.arguments or "{}"
        try:
            args = json.loads(raw_args)
        except json.JSONDecodeError:
            args = {"_unparsed_arguments": raw_args}
        tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))

    usage = response.usage
    usage_dict = {
        "input_tokens": int(usage.prompt_tokens) if usage else 0,
        "output_tokens": int(usage.completion_tokens) if usage else 0,
    }

    raw = response.model_dump() if hasattr(response, "model_dump") else response
    return content, tool_calls, usage_dict, raw


# ---------------------------------------------------------------------------
# Bedrock: Converse API (uniform across model families, unlike the
# Anthropic-only InvokeModel envelope).
# ---------------------------------------------------------------------------


def _chat_bedrock(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None,
    model: str,
    max_tokens: int,
    temperature: float | None,
) -> tuple[str, list[ToolCall], dict[str, int], Any]:
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, NoCredentialsError
    except ImportError as e:
        raise RuntimeError("boto3 is required for provider='bedrock' (pip install boto3).") from e

    region = os.environ.get("AWS_REGION", _DEFAULT_BEDROCK_REGION)
    session_kwargs: dict[str, Any] = {"region_name": region}
    if os.environ.get("AWS_PROFILE"):
        session_kwargs["profile_name"] = os.environ["AWS_PROFILE"]

    try:
        session = boto3.Session(**session_kwargs)
        session.client("sts").get_caller_identity()  # fail fast if creds are missing
    except (NoCredentialsError, BotoCoreError) as e:
        raise RuntimeError(f"AWS credentials not usable (region={region!r}): {e!r}") from e

    client = session.client("bedrock-runtime")

    system_blocks, converse_messages = _to_converse_messages(messages)

    kwargs: dict[str, Any] = {
        "modelId": model,
        "messages": converse_messages,
        "inferenceConfig": {"maxTokens": max_tokens},
    }
    if temperature is not None:
        kwargs["inferenceConfig"]["temperature"] = temperature
    if system_blocks:
        kwargs["system"] = system_blocks
    # Converse ESIGE toolConfig se la storia contiene toolUse/toolResult, e non esiste un
    # toolChoice che dichiari i tool vietandoli (`none` non e' un valore valido: solo auto,
    # any, tool). Quindi il turno finale senza tool -- che il disegno richiede, perche' con la
    # lista ristretta gpt-oss-120b chiama comunque un tool non offerto -- NON e' esprimibile
    # su questa infrastruttura. Vedi SUCCESSIONE-05.
    #
    # Si dichiarano i soli nomi GIA' presenti nella storia, con schema vuoto: soddisfa l'API
    # senza offrire nulla che il modello non abbia gia' visto. Mandare la lista completa
    # offrirebbe su Bedrock quattro tool che su Databricks non ci sono, cioe' un'asimmetria
    # dentro l'ipotesi sull'infrastruttura.
    if not tools:
        usati = []
        for m in converse_messages:
            for blocco in m.get("content", []):
                nome = (blocco.get("toolUse") or {}).get("name")
                if nome and nome not in usati:
                    usati.append(nome)
        if usati:
            kwargs["toolConfig"] = {"tools": [
                {"toolSpec": {"name": n,
                              "description": "non disponibile in questo turno",
                              "inputSchema": {"json": {"type": "object", "properties": {}}}}}
                for n in usati
            ]}

    if tools:
        kwargs["toolConfig"] = {
            "tools": [
                {
                    "toolSpec": {
                        "name": t["function"]["name"],
                        "description": t["function"].get("description", ""),
                        "inputSchema": {"json": t["function"].get("parameters", {})},
                    }
                }
                for t in tools
            ]
        }

    response = client.converse(**kwargs)

    output_message = response.get("output", {}).get("message", {})
    text_parts: list[str] = []
    tool_calls: list[ToolCall] = []
    for block in output_message.get("content", []):
        if "text" in block:
            text_parts.append(block["text"])
        elif "toolUse" in block:
            tu = block["toolUse"]
            tool_calls.append(
                ToolCall(id=tu.get("toolUseId", ""), name=tu.get("name", ""), arguments=dict(tu.get("input") or {}))
            )

    usage = response.get("usage") or {}
    usage_dict = {
        "input_tokens": int(usage.get("inputTokens", 0)),
        "output_tokens": int(usage.get("outputTokens", 0)),
    }
    return "\n".join(text_parts), tool_calls, usage_dict, response


def _to_converse_messages(messages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Convert OpenAI-style chat history (incl. multi-turn tool calls/results)
    into Bedrock Converse's (system_blocks, messages) shape.

    OpenAI "tool" role messages become Converse `toolResult` blocks inside a
    "user" turn. Converse REQUIRES strictly alternating user/assistant roles
    (no two consecutive messages with the same role) -- so any run of
    same-role turns is merged into a single Converse message. This matters
    in practice: a "tool" message immediately followed by a plain "user"
    message (e.g. the harness injecting a tool result, then adding its own
    follow-up instruction in the same turn) both map to Converse role
    "user" and MUST be merged, or Bedrock rejects the request.
    """
    system_blocks: list[dict[str, str]] = []
    converse_messages: list[dict[str, Any]] = []

    def append(role: str, blocks: list[dict[str, Any]]) -> None:
        if converse_messages and converse_messages[-1]["role"] == role:
            converse_messages[-1]["content"].extend(blocks)
        else:
            converse_messages.append({"role": role, "content": blocks})

    for m in messages:
        role = m["role"]

        if role == "system":
            system_blocks.append({"text": m["content"]})
            continue

        if role == "tool":
            append(
                "user",
                [{"toolResult": {"toolUseId": m["tool_call_id"], "content": [{"text": m["content"]}]}}],
            )
            continue

        if role == "assistant":
            content_blocks: list[dict[str, Any]] = []
            if m.get("content"):
                content_blocks.append({"text": m["content"]})
            for tc in m.get("tool_calls") or []:
                args = tc["function"]["arguments"]
                parsed_args = json.loads(args) if isinstance(args, str) else args
                content_blocks.append(
                    {"toolUse": {"toolUseId": tc["id"], "name": tc["function"]["name"], "input": parsed_args}}
                )
            append("assistant", content_blocks or [{"text": ""}])
            continue

        if role == "user":
            append("user", [{"text": m["content"]}])
            continue

        raise ValueError(f"unknown message role {role!r} in Bedrock conversion")

    return system_blocks, converse_messages
