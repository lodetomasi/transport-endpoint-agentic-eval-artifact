"""Baseline monolitico a prompt singolo, con parita' di informazione.

Perche' esiste (risultato del secondo mini-pilot, 2026-08-09): usare "N=1 turno" come
condizione di budget minimo e' confuso. A un solo turno di esplorazione l'agente riesce
al massimo a chiamare `list_functions` — che restituisce nomi di funzione e nient'altro —
e in 20 run su 45 non chiama alcun tool. Il candidato viene quindi prodotto **senza aver
mai visto il codice decompilato**, e il confronto N=1 vs N=12 misura l'accesso
all'informazione, non l'iterazione (+72pp osservati).

E' esattamente l'attacco #2 del methodologist nel dialectic: «se il baseline monolitico
non ha accesso ai tool, il confronto misura la disponibilita' di tool, non l'iterazione».

Questo baseline corregge il confondimento: **stessa informazione, zero iterazione**.
L'agente riceve nel prompt il decompilato delle funzioni principali e deve produrre il
candidato in una sola risposta, senza tool e senza turni successivi.
"""
from __future__ import annotations

import re

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "llm"))
import llm_client  # noqa: E402

from agent_loop import ALLOWED_PROVIDERS, AgentResult, TurnLog, _is_infra_failure, _stop_reason_of  # noqa: E402

SYSTEM_PROMPT = """You are a reverse-engineering assistant. Below is the decompiled \
output of a compiled x86-64 binary that was built from an unknown C program and then \
obfuscated with control-flow flattening.

Reconstruct C source code that reproduces the ORIGINAL program's observable behavior \
(its stdout, given its argv/stdin). Do not reproduce the obfuscated control flow \
literally -- recover the intent.

Answer with the complete, compilable C source only, no explanation."""

USER_TEMPLATE = """Binary: {binary_id}

Functions found: {func_list}

Decompiled code:
{decompiled}

Strings found in the binary:
{strings}

Produce the reconstructed C source now."""


def _seleziona_callgraph(funcs: list, max_funcs: int) -> list:
    """Ordina le funzioni per distanza dal punto di ingresso nel call graph.

    Baseline di retrieval "intelligente" chiesto in review: cosa ottiene un
    esperimento che spende zero turni ma sceglie bene, prendendo `main` e i suoi
    callee diretti invece delle prime N in ordine di dump?

    Il call graph si ricava dal solo dump, senza tool aggiuntivi: si cerca nel corpo
    decompilato di ciascuna funzione il nome delle altre. E' una euristica, non
    un'analisi esatta -- un nome che compare in un commento conta come chiamata -- ma
    e' deterministica, costa zero turni, ed e' il tipo di regola a buon mercato che un
    ricercatore metterebbe nel proprio baseline. Va riportata per quello che e'.
    """
    per_nome = {f.get("name"): f for f in funcs if f.get("name")}
    ingresso = next((n for n in ("main", "entry", "_start") if n in per_nome), None)
    if ingresso is None:
        return funcs[:max_funcs]

    def callee(nome):
        corpo = per_nome.get(nome, {}).get("decompiled") or ""
        return [m for m in per_nome
                if m != nome and re.search(r"\b" + re.escape(m) + r"\s*\(", corpo)]

    ordine, visti, frontiera = [], {ingresso}, [ingresso]
    while frontiera and len(ordine) < max_funcs:
        nuovi = []
        for n in frontiera:
            if len(ordine) >= max_funcs:
                break
            ordine.append(per_nome[n])
            for c in callee(n):
                if c not in visti:
                    visti.add(c)
                    nuovi.append(c)
        frontiera = nuovi
    for f in funcs:                      # completa con l'ordine nativo se serve
        if len(ordine) >= max_funcs:
            break
        if f not in ordine:
            ordine.append(f)
    return ordine[:max_funcs]


def _build_context(client, max_funcs: int = 6, max_chars: int = 40000,
                   select: str = "native", pad_to_chars: int = 0,
                   only_funcs: list | None = None,
                   include_strings: bool = True) -> tuple[str, str, str]:
    """Estrae dal client statico lo stesso materiale che l'agente otterrebbe via tool.

    CORREZIONE del 2026-08-10 (difetto F1, review metodologica).
    La versione precedente ordinava le funzioni per dimensione decrescente prima di
    troncare, con la motivazione che "main e le funzioni grandi portano la semantica".
    Quella e' conoscenza dello sperimentatore, non del sistema sotto test: il braccio
    monolitico riceveva cosi' una selezione CURATA che il braccio agentico doveva
    invece scoprire alla cieca dentro un binario flattened — esattamente il vantaggio
    che il confronto principale del paper pretendeva di aver eliminato.

    Ora l'ordine e' quello nativo del dump di Ghidra, identico a quello che
    `list_functions()` restituisce all'agente. Nessuna delle due condizioni riceve
    un ordinamento privilegiato.
    """
    func_lines = client.list_functions()
    func_list = ", ".join(f.split(" @ ")[0] for f in func_lines)

    funcs = list(client.data.get("functions", []))
    if select == "callgraph":
        funcs = _seleziona_callgraph(funcs, max_funcs)

    # Condizione APPAIATA ALLA TRAIETTORIA: invece di un numero di funzioni si passa
    # l'insieme ESATTO che una traiettoria agentica ha recuperato, nell'ordine nativo.
    # Serve a togliere l'accesso all'informazione dai gradi di liberta' del confronto:
    # non "la stessa quantita'" ma "esattamente le stesse funzioni". Il cap non si
    # applica, perche' l'insieme e' gia' quello che l'agente e' riuscito a ottenere.
    if only_funcs is not None:
        voluti = {n for n in only_funcs}
        funcs = [f for f in funcs if f.get("name") in voluti]
        max_funcs, max_chars = len(funcs), 10 ** 9

    def assembla(quante: int, limite: int) -> str:
        blocks, used = [], 0
        for f in funcs[:quante]:
            code = f.get("decompiled")
            if not code:
                continue
            if used + len(code) > limite:
                break
            blocks.append(f"/* --- {f['name']} @ {f['entry_point']} --- */\n{code}")
            used += len(code)
        return "\n\n".join(blocks) if blocks else "(nessuna funzione decompilata)"

    decompiled = assembla(max_funcs, max_chars)

    if pad_to_chars:
        # Il bersaglio e' la lunghezza del blocco NON troncato assemblato esattamente
        # come lo assembla il braccio non troncato, intestazioni per funzione incluse.
        # Pareggiare i soli caratteri di codice lascerebbe fuori quelle, e la
        # condizione di controllo resterebbe piu' corta di quella che deve eguagliare.
        bersaglio = len(assembla(len(funcs), 10 ** 9))
        if len(decompiled) < bersaglio:
            decompiled += _riempimento(bersaglio - len(decompiled))

    # L'agente riceve le stringhe SOLO se spende un turno a chiederle, e lo fa nel 47%
    # delle traiettorie. Un baseline appaiato alla traiettoria deve riprodurre anche
    # questo: dargliele sempre lo renderebbe di nuovo avvantaggiato sul canale che la
    # misura di copertura non contava.
    if include_strings:
        strings = "\n".join(client.list_strings(limit=60)) or "(nessuna stringa)"
    else:
        strings = "(non richieste)"
    return func_list, decompiled, strings


def _riempimento(quanti: int) -> str:
    """Testo irrilevante per pareggiare la LUNGHEZZA del prompt senza aggiungere
    informazione sul binario sotto analisi.

    Perche' esiste: togliere il cap aumenta insieme la quantita' di materiale e la
    lunghezza del prompt, e il paper non poteva separarle. Questa condizione tiene
    l'informazione al livello del braccio troncato e porta la lunghezza a quella del
    braccio non troncato. Se la pass-rate resta quella del troncato, l'effetto del cap
    e' informazione; se sale verso il non troncato, era lunghezza.

    Con COSA si riempie e' la scelta che decide se il controllo e' onesto. Codice
    decompilato di altri binari, non etichettato, trasformerebbe il compito in una
    ricerca fra distrattori: piu' difficile del troncato, non solo piu' lungo, e il
    bias andrebbe nella direzione che ci conviene. Si usa invece un blocco
    ESPLICITAMENTE dichiarato come non appartenente al binario, cosi' il modello puo'
    ignorarlo a costo zero e l'unica variabile che cambia e' il numero di caratteri.
    """
    intestazione = (
        "\n\n/* ----------------------------------------------------------------\n"
        "   REFERENCE MATERIAL BELOW. The following C code is NOT part of the\n"
        "   binary under analysis and is unrelated to it. It is included only\n"
        "   as background reference and can be ignored.\n"
        "   ---------------------------------------------------------------- */\n"
    )
    # Il riempimento deve pareggiare i TOKEN, non solo i caratteri: un blocco ripetitivo
    # si comprime molto meglio del decompilato vero (a parita' di caratteri dava 5.745
    # token contro 6.727), e un controllo che arriva all'85% della lunghezza vera lascia
    # aperta l'obiezione che voleva chiudere. Si genera quindi testo con la stessa
    # densita' del decompilato di Ghidra: identificatori diversi a ogni riga, costanti
    # esadecimali, cast, indici -- deterministico (nessun seme, nessuna casualita') ma
    # non compresso.
    rng = 0x2545F491
    fuori = [intestazione]
    lung = len(intestazione)
    i = 0
    while lung < quanti:
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        a, b, c = rng & 0xFFFF, (rng >> 7) & 0xFFF, (rng >> 13) & 0xFF
        blocco = (
            f"ulong ref_fn_{i:04x}(uint *param_1,long param_2,byte param_3)\n"
            f"{{\n"
            f"  uint uVar{c % 9 + 1};\n"
            f"  long lVar{b % 7 + 1};\n"
            f"  ulong uStack_{a:04x};\n"
            f"  uVar{c % 9 + 1} = *param_1 ^ 0x{rng:08x};\n"
            f"  lVar{b % 7 + 1} = param_2 + {a} * (long)(int)uVar{c % 9 + 1};\n"
            f"  uStack_{a:04x} = (ulong)(param_3 & 0x{c:02x}) << {b % 31 + 1};\n"
            f"  if (lVar{b % 7 + 1} < {rng % 100003}) {{\n"
            f"    uStack_{a:04x} = uStack_{a:04x} | (ulong)uVar{c % 9 + 1};\n"
            f"  }}\n"
            f"  return uStack_{a:04x} + 0x{b:03x};\n"
            f"}}\n\n"
        )
        fuori.append(blocco)
        lung += len(blocco)
        i += 1
    return "".join(fuori)[:quanti]


def run_monolithic(
    binary_id: str,
    model: str,
    provider: str,
    max_tokens: int,
    temperature: float | None,
    ghidra_client,
    max_funcs: int = 6,
    max_chars: int = 40000,
    select: str = "native",
    pad_to_chars: int = 0,
    only_funcs: list | None = None,
    include_strings: bool = True,
    extra_system: str = "",
) -> AgentResult:
    if provider not in ALLOWED_PROVIDERS:
        raise ValueError(f"provider={provider!r} non consentito.")

    func_list, decompiled, strings = _build_context(
        ghidra_client, max_funcs=max_funcs, max_chars=max_chars, select=select,
        pad_to_chars=pad_to_chars, only_funcs=only_funcs,
        include_strings=include_strings)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + (f"\n\n{extra_system}" if extra_system else "")},
        {"role": "user", "content": USER_TEMPLATE.format(
            binary_id=binary_id, func_list=func_list,
            decompiled=decompiled, strings=strings)},
    ]

    turn_log = TurnLog(turn=1, request_message_count=len(messages), response_text="")
    candidate = None
    err = None
    cost = tin = tout = 0
    infra = False
    try:
        result = llm_client.chat(
            messages=messages, tools=None, model=model,
            max_tokens=max_tokens, temperature=temperature, provider=provider,
        )
        turn_log.response_text = result.content or ""
        turn_log.usage = dict(result.usage)
        turn_log.cost_usd = result.cost_usd
        turn_log.stop_reason = _stop_reason_of(result)
        turn_log.infra_failure = _is_infra_failure(result)
        infra = turn_log.infra_failure
        candidate = result.content or None
        cost = result.cost_usd
        tin = result.usage.get("input_tokens", 0)
        tout = result.usage.get("output_tokens", 0)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
        turn_log.error = err
        # Un'eccezione durante la chiamata all'API e' per definizione un fallimento
        # dell'infrastruttura, non dell'agente: rate limit, timeout, credenziali,
        # tariffa mancante. Senza questa riga il run finiva registrato come
        # pass_rate=0 con infra_failure=False, indistinguibile da un modello che ha
        # provato e sbagliato. E' successo davvero, due volte in un giorno: 28 righe
        # della replica Qwen su un 429 e 89 righe del braccio llama su una guardia
        # dei prezzi. Entrambe deprimevano il pass-rate di un braccio e producevano
        # numeri che sembravano risultati.
        infra = True
        turn_log.infra_failure = True

    return AgentResult(
        binary_id=binary_id,
        candidate_source=candidate,
        submitted_via_tool=False,
        turns=[turn_log],
        total_cost_usd=cost,
        total_tokens_in=tin,
        total_tokens_out=tout,
        model=model,
        provider=provider,
        n_turns_config=0,  # 0 = monolitico, nessuna iterazione
        infra_failure=infra,
        error=err,
    )
