#!/usr/bin/env python3
"""Emette le celle dello Studio 03 scese sotto n=8 dopo il filtro di qualita'.

Una riga per gruppo, campi separati da '|':
    tag|modello|turni|run_mancanti|id1,id2,...|extra_args
(gli id sono separati da virgola: il campo resta uno solo, cosi' `cut` non sbaglia)

Serve a `chiudi_studio03.sh`. Non decide niente: applica la regola di completezza gia'
scritta nella pre-registrazione (§6) — le celle si completano, non si scartano, perche'
scartare i binari su cui un guasto ha morso e' una selezione.
"""
from __future__ import annotations

import collections
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from qualita_run import SUFFISSI_RIESECUZIONE, e_misurazione  # noqa: E402

N = 8

# Bracci che l'ENDPOINT rifiuta di eseguire, non che il modello sbaglia. Non si riprovano:
# ogni tentativo torna identico, e 4 passate x 315 run sarebbero 1.260 richieste per lo
# stesso 400. La distinzione conta: un fallimento di capacita' si completa riprovando, un
# rifiuto di piattaforma no.
#
#   s03_gemma12b_N12 — databricks-gemma-3-12b, 2026-08-12:
#     400 BAD_REQUEST: "The current request/model does not support multi-turn tool calls."
#     43 righe su 45 con quel codice. Il braccio mono dello stesso modello gira 360/360,
#     quindi non e' il modello: e' che l'endpoint non ammette una SECONDA tool call.
#     Le 2 righe senza errore sono run che hanno inviato al primo turno e non ne hanno
#     mai fatta una seconda: non sono la condizione N=12, sono N=1 travestito, e per
#     questo il braccio non e' completabile invece che solo incompleto.
#
# analyze_studio03.py (congelato prima dei dati) tiene la famiglia a m=4 e non testa un
# modello incompleto: Gemma resta fuori dai test con le soglie di Holm degli altri
# INVARIATE. E' la lettura conservativa, ed e' voluta — togliere un modello dalla famiglia
# a dati visti abbasserebbe le soglie dei sopravvissuti.
NON_ESEGUIBILI = {
    "s03_gemma12b_N12": "endpoint 400: multi-turn tool calls non supportate",
}

ARMI = [
    ("s03_gemma12b_mono_uncapped", "databricks-gemma-3-12b", "0",
     "--mono-funcs 999 --mono-chars 400000"),
    ("s03_gemma12b_N12", "databricks-gemma-3-12b", "12", ""),
    ("s03_gptoss20b_mono_uncapped", "databricks-gpt-oss-20b", "0",
     "--mono-funcs 999 --mono-chars 400000"),
    ("s03_gptoss20b_N12", "databricks-gpt-oss-20b", "12", ""),
    ("s03_llama3370b_mono_uncapped", "databricks-meta-llama-3-3-70b-instruct", "0",
     "--mono-funcs 999 --mono-chars 400000"),
    ("s03_llama3370b_N12", "databricks-meta-llama-3-3-70b-instruct", "12", ""),
    ("s03_haiku45_mono_uncapped", "databricks-claude-haiku-4-5", "0",
     "--mono-funcs 999 --mono-chars 400000"),
    ("s03_haiku45_N12", "databricks-claude-haiku-4-5", "12", ""),
]
# I 45 binari held-out: prog16..prog60. Una cella assente conta come 8 run mancanti.
ATTESI = None


def binari_attesi() -> set:
    d = os.path.join(os.path.dirname(__file__), "decomp_stripped")
    fuori = set()
    for f in sorted(os.listdir(d)):
        if not f.endswith("_flat.json"):
            continue
        bid = f[: -len("_flat.json")]
        n = "".join(c for c in bid.split("_")[0] if c.isdigit())
        if n and 16 <= int(n) <= 60:
            fuori.add(bid)
    return fuori


def validi(tag: str) -> dict:
    conta = collections.defaultdict(int)
    for suff in list(SUFFISSI_RIESECUZIONE) + ["_redo1", "_redo2", "_redo3"]:
        p = os.path.join(os.path.dirname(__file__), "results", f"{tag}{suff}.csv")
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p)):
            if e_misurazione(r) and r.get("n_tests") == "5" and r.get("pass_rate"):
                conta[r["binary_id"]] += 1
    return conta


def main() -> int:
    attesi = binari_attesi()
    for tag, modello, turni, extra in ARMI:
        if tag in NON_ESEGUIBILI:
            print(f"# SALTATO {tag}: {NON_ESEGUIBILI[tag]}", file=sys.stderr)
            continue
        conta = validi(tag)
        # una cella mai partita e' incompleta quanto una a meta'
        gruppi = collections.defaultdict(list)
        for b in sorted(attesi):
            manca = N - conta.get(b, 0)
            if manca > 0:
                gruppi[manca].append(b)
        for manca, ids in sorted(gruppi.items()):
            # a blocchi di 12 binari per non generare regex sterminate
            for i in range(0, len(ids), 12):
                blocco = ids[i:i + 12]
                print(f"{tag}|{modello}|{turni}|{manca}|{','.join(blocco)}|{extra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
