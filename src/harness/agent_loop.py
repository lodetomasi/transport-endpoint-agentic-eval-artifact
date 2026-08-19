"""Fixed-turn-budget agent loop (SPEC-mini-pilot.md step 5).

N=4 turns, fixed, arbitrary -- this is a variance-measurement mini-pilot, NOT
the N in {1,4,12} sweep of the full S1 design. Every tool call and every
model response is logged for audit (top-level project rule: "Every run
writes the full logging record ... including on failure").

Provider is pinned to "bedrock" here, not read from config, on purpose: the
user's task instructions explicitly exclude Databricks/<organizzazione> accounts for
this project ("NON usare Databricks né alcun account/profilo <organizzazione> per
nessuna parte di questo lavoro"). llm/llm_client.py (written by a separate
agent in this session) also supports provider="databricks" -- this module
refuses to use it. A mid-task message claiming the user had authorized
Databricks/<organizzazione> usage was received and NOT acted on -- see the mini-pilot
final report for why (agent-relayed claims of user authorization are not
treated as consent, per this agent's operating rules).

INFRASTRUCTURE-FAILURE DETECTION: a completion can be truncated by the
provider's max_tokens limit mid-generation and come back with empty
`content` and no tool calls. If that is silently recorded as "the agent
produced nothing" it is indistinguishable from a genuine agent failure --
which would corrupt exactly the ICC/SD measurement this mini-pilot exists to
produce. Each turn is checked for this (via the Bedrock Converse response's
top-level `stopReason` field, exposed in `ChatResult.raw`) and flagged as
`infra_failure=True` on the TurnLog / AgentResult, kept in a separate field
from `candidate_source` / pass-rate so run_pilot.py can log it as its own
CSV column rather than folding it into pass_rate=0.
"""
from __future__ import annotations

import re

import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "llm"))
import llm_client  # noqa: E402

from tool_schemas import ALL_TOOLS  # noqa: E402

# Provider ammessi. `databricks` e' incluso perche' l'utente lo ha autorizzato
# esplicitamente in conversazione il 2026-08-09 ("sfrutta databricks ti autorizzo",
# "usa anche i modelli cinesi su databricks ti autorizzo"), con il vincolo di usare
# SOLO serving endpoint pay-per-token gia' provisionati e MAI creare cluster o job
# (l'ambiente ospita job di produzione <organizzazione>).
ALLOWED_PROVIDERS = {"bedrock", "databricks", "azure"}

SYSTEM_PROMPT = """You are a reverse-engineering assistant. You are given a \
compiled x86-64 binary (already loaded into a Ghidra project) that was built \
from an unknown C program and then obfuscated. Your job is to reconstruct C \
source code that reproduces the ORIGINAL program's observable behavior \
(its stdout, given its argv/stdin), not to reproduce the obfuscated control \
flow literally.

You have tools to inspect the binary: list_functions, decompile_function, \
get_function_xrefs, list_strings, disassemble_function. Use them to \
understand the program.

You have a FIXED budget of {n_turns} turns total (this message starts turn \
1). When you are done -- or when you are on your last turn, regardless of \
confidence -- call submit_candidate with your best complete, compilable C \
source. If you never call submit_candidate, your last turn's text response \
will be used as a fallback candidate, which is very unlikely to compile."""

def _id_opaco(binary_id: str) -> str:
    """Cio' che il modello vede: l'indice nel corpus, non il nome dell'algoritmo.

    `prog36_pascal_triangle` nomina la soluzione nel primo messaggio, prima di qualunque tool
    call -- lo stesso difetto che in C1 porto' il baseline a 0,894, in una forma che la
    rimozione dei simboli dal binario non tocca (emendamento 03). `prog36` e' una posizione nel
    corpus e non ha semantica; il nome pieno resta nelle colonne CSV, nei percorsi e nelle
    traiettorie, dove serve a noi e non al modello.
    """
    m = re.match(r"^(prog\d+)", binary_id)
    return m.group(1) if m else binary_id


USER_PROMPT = """Binary under analysis: {binary_id}
Ghidra project is already loaded with this binary. Begin your investigation."""

# ---------------------------------------------------------------------------
# Protocollo dei tool in TESTO, per endpoint che rifiutano il tool-calling nativo.
#
# Perche' esiste: `databricks-gemma-3-12b` risponde
#   400 BAD_REQUEST: "The current request/model does not support multi-turn tool calls"
# a ogni conversazione agentica. Il rifiuto e' del TRASPORTO, non del modello: lo stesso
# modello esegue senza problemi il braccio monolitico, che non usa tool.
#
# Un endpoint che non parla il protocollo nativo fa sparire un modello da qualunque
# valutazione agentica, in silenzio e senza che il numero risultante lo dichiari. E' la
# stessa classe di problema che questo paper misura — un'impostazione della piattaforma
# che decide un confronto — e la risposta e' la stessa: misurarla, non subirla.
#
# Il budget di turni, i tool offerti, il prompt di sistema e il turno finale obbligatorio
# restano identici. Cambia solo COME la chiamata viaggia. Che il cambiamento sia neutro
# non si promette: si misura, rieseguendo in questo protocollo anche i tre modelli che
# supportano il nativo (vedi PREREGISTRATION-STUDIO-03-EMENDAMENTO-03.md).
# ---------------------------------------------------------------------------
TEXT_TOOL_PROTOCOL = """

TOOL PROTOCOL. You do not have a tool-calling API. To use a tool, end your reply with \
exactly one line in this form, and nothing after it:

TOOL_CALL: {"name": "<tool>", "arguments": {...}}

The harness runs the tool and gives you its output in the next message. One tool call \
per turn. Available tools and their arguments:

  {"name": "list_functions", "arguments": {}}
  {"name": "decompile_function", "arguments": {"name": "main"}}
  {"name": "list_strings", "arguments": {"limit": 60}}

To give your final answer instead of calling a tool, reply with the complete C source \
inside a ```c fenced code block, and no TOOL_CALL line. Do that when you are done, and \
in any case on your last turn."""

TEXT_TOOL_REMINDER = ("Tool output above. Continue: either one TOOL_CALL line, or your "
                      "final C source in a ```c block.")


def _sembra_codice_c(testo: str) -> bool:
    """Il turno contiene una consegna, non un'intenzione dichiarata.

    Deliberatamente generoso verso l'agente: basta un blocco recintato C o un marcatore
    inequivocabile di sorgente. Un falso positivo gli fa consegnare presto un candidato
    che verra' comunque compilato e testato; un falso negativo gli costa un turno. Nessuno
    dei due inventa un successo.
    """
    t = testo or ""
    if "```c" in t or "```C" in t:
        return True
    return ("#include" in t) or ("int main(" in t) or ("int main (" in t)


def _parse_text_tool_call(text: str) -> tuple[str, dict] | None:
    """Estrae una chiamata `TOOL_CALL: {...}` dal testo libero del modello.

    Tollerante per costruzione: il modello puo' scrivere ragionamento prima, mettere la
    riga dentro un blocco recintato, o aggiungere testo dopo. Si prende l'ULTIMA
    occorrenza e si bilanciano le graffe invece di affidarsi a una regex, perche' gli
    argomenti contengono a loro volta un oggetto JSON. Un parse fallito non e' un errore
    dell'infrastruttura: significa che il modello ha risposto in prosa, e la prosa e' gia'
    gestita come candidato finale.
    """
    marcatore = "TOOL_CALL:"
    i = text.rfind(marcatore)
    if i < 0:
        return None
    resto = text[i + len(marcatore):]
    inizio = resto.find("{")
    if inizio < 0:
        return None
    prof = 0
    in_str = False
    esc = False
    for j, ch in enumerate(resto[inizio:], start=inizio):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            prof += 1
        elif ch == "}":
            prof -= 1
            if prof == 0:
                import json
                grezzo = resto[inizio:j + 1]
                try:
                    obj = json.loads(grezzo)
                except Exception:  # noqa: BLE001
                    # Alcuni modelli raddoppiano le graffe imitando un template.
                    try:
                        obj = json.loads(grezzo.replace("{{", "{").replace("}}", "}"))
                    except Exception:  # noqa: BLE001
                        return None
                nome = obj.get("name")
                args = obj.get("arguments")
                if not isinstance(nome, str):
                    return None
                return nome, (args if isinstance(args, dict) else {})
    return None


def _stop_reason_of(result: "llm_client.ChatResult") -> str | None:
    """Best-effort extraction of the provider's stop/finish reason from the
    raw response, for infra-failure detection. Returns None if unknown."""
    raw = result.raw
    if isinstance(raw, dict):
        if "stopReason" in raw:  # Bedrock Converse
            return raw["stopReason"]
        choices = raw.get("choices")  # OpenAI-compatible (Databricks) shape, if raw is a dict
        if choices:
            return choices[0].get("finish_reason")
    return None


def _is_infra_failure(result: "llm_client.ChatResult") -> bool:
    """A completion that was cut off by the token budget mid-generation,
    with nothing usable to show for it (no text, no tool call), is an
    infrastructure failure, not an agent failure -- see module docstring."""
    stop_reason = _stop_reason_of(result)
    truncated = stop_reason in ("max_tokens", "length")
    empty = not (result.content or "").strip() and not result.tool_calls
    return truncated and empty


@dataclass
class TurnLog:
    turn: int
    request_message_count: int
    response_text: str
    tool_calls: list[dict] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    cost_usd: float = 0.0
    is_cost_estimate: bool = True
    stop_reason: str | None = None
    infra_failure: bool = False
    tools_offered: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class AgentResult:
    binary_id: str
    candidate_source: str | None
    submitted_via_tool: bool
    turns: list[TurnLog]
    total_cost_usd: float
    total_tokens_in: int
    total_tokens_out: int
    model: str
    provider: str
    n_turns_config: int
    infra_failure: bool = False
    error: str | None = None


def run_agent(
    binary_id: str,
    n_turns: int,
    model: str,
    provider: str,
    max_tokens: int,
    temperature: float | None,
    ghidra_client,  # GhidraMCPClient o GhidraStaticClient (stessa interfaccia .call())
    tool_protocol: str = "native",
    max_calls_per_turn: int | None = None,
) -> AgentResult:
    """`max_calls_per_turn=1` sul trasporto nativo esegue solo la PRIMA chiamata di ogni
    turno e scarta le altre, riproducendo il vincolo che il protocollo testuale ha per
    costruzione. Serve a separare due cose che il disegno pre-registrato confonde: il cambio
    di protocollo e la perdita del raggruppamento delle chiamate. Senza, un modello che
    raggruppa (haiku 1,44 chiamate per turno, sonnet 1,33) confronta due manipolazioni
    insieme, e il paper puo' solo dichiarare il confondimento invece di misurarlo.

    Il default None non tocca nulla: la raccolta confermativa gira come prima."""
    if provider not in ALLOWED_PROVIDERS:
        raise ValueError(
            f"provider={provider!r} non consentito (ammessi: {sorted(ALLOWED_PROVIDERS)})."
        )
    if tool_protocol not in ("native", "text"):
        raise ValueError(f"tool_protocol={tool_protocol!r} sconosciuto (native|text).")
    testuale = tool_protocol == "text"

    sistema = SYSTEM_PROMPT.format(n_turns=n_turns) + (TEXT_TOOL_PROTOCOL if testuale else "")
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": sistema},
        {"role": "user", "content": USER_PROMPT.format(binary_id=_id_opaco(binary_id))},
    ]

    turns: list[TurnLog] = []
    candidate_source: str | None = None
    submitted_via_tool = False
    total_cost = 0.0
    total_in = 0
    total_out = 0
    fatal_error: str | None = None
    infra_failure = False

    # Turno finale di sottomissione OBBLIGATORIO, oltre agli n_turns di esplorazione.
    #
    # Perche' (bug reale osservato il 2026-08-09): senza di esso, a N=1 l'agente spende
    # il suo unico turno in una tool call e il loop termina prima che possa sottomettere
    # un candidato. Risultato: 45 run su 45 a candidate_chars=0 e pass_rate=0 — un
    # artefatto del design dell'harness che sarebbe stato letto come "l'iterazione porta
    # da 0% a 70%", cioe' un risultato falso sulla domanda centrale del paper.
    #
    # Con questa correzione ogni condizione di budget riceve lo stesso trattamento
    # (n_turns di esplorazione con tool + 1 turno di sola sottomissione), quindi i budget
    # restano confrontabili tra loro. Va dichiarato nella pre-registrazione.
    total_iterations = n_turns + 1

    for turn_idx in range(1, total_iterations + 1):
        is_final = turn_idx == total_iterations
        turn_log = TurnLog(turn=turn_idx, request_message_count=len(messages), response_text="")
        if is_final:
            messages.append({
                "role": "user",
                "content": (
                    "Ultimo turno: gli strumenti di analisi non sono piu' disponibili. "
                    "Rispondi ORA con il codice sorgente C completo e compilabile che "
                    "riproduce il comportamento osservabile del programma originale "
                    "(stdout dato argv/stdin). Rispondi con il solo codice C, senza "
                    "spiegazioni. Se non hai certezza, dai comunque la tua ricostruzione "
                    "migliore."
                ),
            })
        # Turno finale: NESSUN tool.
        #
        # Restringere la lista al solo submit_candidate non basta: verificato il
        # 2026-08-09 che gpt-oss-120b, con `tools=[submit_candidate]`, chiama comunque
        # `decompile_function` — un tool non offerto. Togliere del tutto i tool e
        # chiedere il sorgente in chiaro e' l'unica forma che garantisce un candidato;
        # l'estrazione del C dal testo e' gia' gestita da run_minipilot.extract_c_source.
        turn_tools = None if (is_final or testuale) else ALL_TOOLS
        if testuale:
            # I tool ci sono, viaggiano nel prompt di sistema invece che nel campo `tools`.
            # Il log deve dire cosa l'agente poteva usare, non quale campo li trasportava.
            turn_log.tools_offered = [] if is_final else ["list_functions", "decompile_function",
                                                          "list_strings", "submit_candidate"]
        else:
            turn_log.tools_offered = [t["function"]["name"] for t in (turn_tools or [])]
        try:
            result = llm_client.chat(
                messages=messages,
                tools=turn_tools,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                provider=provider,
            )
        except Exception as e:  # noqa: BLE001 -- must log and continue to next binary, not crash the whole sweep
            turn_log.error = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
            # Un'eccezione durante la chiamata e' un fallimento dell'infrastruttura,
            # non dell'agente. Senza questo flag il run finiva a pass_rate=0 con
            # infra_failure=False: indistinguibile da un modello che ha provato e
            # sbagliato. Vedi la nota gemella in monolithic.py.
            turn_log.infra_failure = True
            infra_failure = True
            turns.append(turn_log)
            fatal_error = turn_log.error
            break

        turn_log.response_text = result.content or ""
        turn_log.usage = dict(result.usage)
        turn_log.cost_usd = result.cost_usd
        turn_log.is_cost_estimate = result.is_cost_estimate
        turn_log.stop_reason = _stop_reason_of(result)
        total_cost += result.cost_usd
        total_in += result.usage.get("input_tokens", 0)
        total_out += result.usage.get("output_tokens", 0)

        if _is_infra_failure(result):
            # Truncated by max_tokens with nothing usable to show for it --
            # this trial is unscoreable, not a genuine agent failure. Stop
            # here rather than burning the rest of the turn budget on a
            # conversation the model already lost track of.
            turn_log.infra_failure = True
            turns.append(turn_log)
            return AgentResult(
                binary_id=binary_id,
                candidate_source=None,
                submitted_via_tool=False,
                turns=turns,
                total_cost_usd=total_cost,
                total_tokens_in=total_in,
                total_tokens_out=total_out,
                model=model,
                provider=provider,
                n_turns_config=n_turns,
                infra_failure=True,
                error=None,
            )

        messages.append(result.to_assistant_message())

        if testuale and not is_final:
            testo = result.content or ""
            chiamata = _parse_text_tool_call(testo)
            if chiamata is None:
                if _sembra_codice_c(testo):
                    # Il modello ha consegnato: il candidato e' il testo, e `extract_c_source`
                    # a valle ne tira fuori il blocco C come per il turno finale.
                    candidate_source = testo
                    submitted_via_tool = False
                    turns.append(turn_log)
                    break
                # Prosa senza chiamata e senza codice: nel protocollo nativo un turno di
                # solo testo consuma un turno e il loop prosegue. Qui deve fare lo stesso —
                # trattarla come consegna finale regalerebbe la vittoria a chi annuncia
                # l'intenzione invece di agire, e i modelli piccoli lo fanno di continuo
                # ("Okay, let's start by identifying the functions", 48 token, turno 1).
                messages.append({"role": "user", "content": TEXT_TOOL_REMINDER})
                turns.append(turn_log)
                continue
            nome, argomenti = chiamata
            turn_log.tool_calls.append({"name": nome, "arguments": argomenti})
            if nome == "submit_candidate":
                candidate_source = argomenti.get("c_source") or testo
                submitted_via_tool = True
                turns.append(turn_log)
                break
            try:
                tool_output = ghidra_client.call(nome, argomenti)
            except Exception as e:  # noqa: BLE001 -- l'errore del tool torna all'agente
                tool_output = f"ERROR calling Ghidra tool {nome}: {type(e).__name__}: {e}"
            turn_log.tool_results.append({"name": nome, "output": tool_output})
            messages.append({"role": "user", "content": f"{tool_output}\n\n{TEXT_TOOL_REMINDER}"})
            turns.append(turn_log)
            continue

        submit_call = next((tc for tc in result.tool_calls if tc.name == "submit_candidate"), None)
        if submit_call is not None:
            candidate_source = submit_call.arguments.get("c_source")
            submitted_via_tool = True
            turn_log.tool_calls.append({"name": submit_call.name, "arguments": submit_call.arguments})
            turns.append(turn_log)
            break

        da_eseguire = result.tool_calls
        if max_calls_per_turn is not None and len(da_eseguire) > max_calls_per_turn:
            # le scartate si registrano: un'ablazione che non dice cosa ha tolto non e'
            # misurabile a valle, e la differenza fra "non ha chiamato" e "ha chiamato e
            # l'abbiamo ignorato" e' esattamente cio' che questo braccio deve distinguere
            for scartata in da_eseguire[max_calls_per_turn:]:
                turn_log.tool_calls.append({"name": scartata.name,
                                            "arguments": scartata.arguments,
                                            "scartata_da_ablazione": True})
                # Ogni `tool_use` DEVE avere il suo `tool_result`, anche quando la chiamata
                # non viene eseguita: l'API rifiuta l'intera conversazione con
                # «tool_use ids were found without tool_result blocks» e la cella muore.
                # Trovato dallo smoke a $0,0015, prima delle 720 run del braccio.
                # Il messaggio e' esplicito perche' il modello sappia perche' non ha avuto
                # la risposta, invece di attribuirlo a un guasto e cambiare strategia.
                rifiuto = ("NOT EXECUTED: this run allows one tool call per turn. "
                           "Call one tool at a time.")
                turn_log.tool_results.append({"name": scartata.name, "output": rifiuto})
                messages.append(llm_client.tool_result_message(scartata.id, rifiuto))
            da_eseguire = da_eseguire[:max_calls_per_turn]

        for tc in da_eseguire:
            turn_log.tool_calls.append({"name": tc.name, "arguments": tc.arguments})
            try:
                tool_output = ghidra_client.call(tc.name, tc.arguments)
            except Exception as e:  # noqa: BLE001 -- l'errore del tool torna all'agente
                tool_output = f"ERROR calling Ghidra tool {tc.name}: {type(e).__name__}: {e}"
            turn_log.tool_results.append({"name": tc.name, "output": tool_output})
            messages.append(llm_client.tool_result_message(tc.id, tool_output))

        turns.append(turn_log)

        if is_final and not submitted_via_tool:
            # Last turn used up without an explicit submission: fall back to
            # whatever free text the model produced (very unlikely to compile,
            # but SPEC step 5 requires SOME candidate at the end of N turns).
            candidate_source = result.content or None

    return AgentResult(
        binary_id=binary_id,
        candidate_source=candidate_source,
        submitted_via_tool=submitted_via_tool,
        turns=turns,
        total_cost_usd=total_cost,
        total_tokens_in=total_in,
        total_tokens_out=total_out,
        model=model,
        provider=provider,
        n_turns_config=n_turns,
        infra_failure=infra_failure,
        error=fatal_error,
    )
