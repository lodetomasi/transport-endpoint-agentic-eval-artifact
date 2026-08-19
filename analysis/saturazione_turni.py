#!/usr/bin/env python3
"""SPEC-16 — la saturazione del budget di turni, per cella, misurata invece che supposta.

PERCHE' ESISTE. La colonna `n_turns` dei CSV vale 12 su ogni riga perche' registra il budget
CONFIGURATO, non i turni usati: `run_minipilot` la scrive da `args.turns`. Una tabella che la
riporta come mediana osservata sta stampando una costante di configurazione. I turni davvero
consumati stanno nelle traiettorie, una riga per turno.

Convenzione: il budget e' 12 turni di esplorazione PIU' un turno finale di sola sottomissione
(`agent_loop.total_iterations = n_turns + 1`), quindi una traiettoria da 13 righe e' una che ha
esaurito il budget. `turni_usati` qui e' il numero di righe.

CONTROLLO A RISPOSTA NOTA, nei due sensi:
  - nessuna traiettoria puo' superare le 13 righe (il ciclo non lo permette): deve valere per tutte;
  - il conteggio al budget deve coincidere con `run_al_budget` di numeri_paper.py sullo stesso
    braccio, che e' 68 sulla ri-raccolta e 55 sull'originale.

    python3 analysis/saturazione_turni.py [--braccio riraccolta|confermativo|ablazione]
"""
import argparse, collections, glob, json, os, statistics as st, sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUDGET = 13  # 12 turni di esplorazione + il turno finale di sottomissione
# I prefissi sono quelli dichiarati dal progetto: c2_ confermativo, c2a_ ablazione, c2r_
# ri-raccolta. «ablazione» come stringa letterale corrispondeva a tre directory di scarto
# (`ablazione`, `ablazione2`, `ablazione3`, un file ciascuna) e IGNORAVA le cinque celle vere:
# tre traiettorie lette invece di 1.085, con il controllo a risposta nota verde e exit 0.
# Trovato da una code review che ha eseguito lo script invece di leggerlo.
PREFISSO = {"riraccolta": "c2r_", "confermativo": "c2_", "ablazione": "c2a_"}


def celle(prefisso):
    """Le traiettorie per cella, unendo la catena dei suffissi: c2r_X e c2r_X_redo sono la
    STESSA cella, e tenerle separate spezzerebbe il denominatore in due meta'."""
    fuori = collections.defaultdict(list)
    base = os.path.join(RADICE, "results", "trajectories")
    for d in sorted(os.listdir(base)):
        if not d.startswith(prefisso):
            continue
        if prefisso == "c2_" and d.startswith("c2r_"):
            continue
        nome = d
        for suf in ("_redo3", "_redo2", "_redo"):
            if nome.endswith(suf):
                nome = nome[: -len(suf)]
                break
        fuori[nome].extend(sorted(glob.glob(os.path.join(base, d, "*.jsonl"))))
    return fuori


def profilo(percorsi):
    turni, motivi = [], collections.Counter()
    for p in percorsi:
        righe = [json.loads(l) for l in open(p) if l.strip()]
        if not righe:
            continue
        turni.append(len(righe))
        ultimo = righe[-1]
        if len(righe) >= BUDGET:
            motivi["budget esaurito"] += 1
        elif any(c.get("name") == "submit_candidate"
                 for r in righe for c in (r.get("tool_calls") or [])):
            motivi["sottomissione via tool"] += 1
        elif ultimo.get("infra_failure"):
            motivi["fallimento infrastruttura"] += 1
        else:
            motivi["turno finale di sottomissione"] += 1
    if not turni:
        return None
    turni.sort()
    q = st.quantiles(turni, n=4) if len(turni) >= 4 else [turni[0]] * 3
    return {"N": len(turni), "mediana": st.median(turni), "Q1": q[0], "Q3": q[2],
            "al_budget": sum(1 for t in turni if t >= BUDGET),
            "max": turni[-1], "motivi": motivi}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--braccio", default="riraccolta", choices=sorted(PREFISSO))
    ap.add_argument("--tsv")
    a = ap.parse_args()

    righe, tot, tot_budget, oltre = [], 0, 0, 0
    for cella, percorsi in sorted(celle(PREFISSO[a.braccio]).items()):
        p = profilo(percorsi)
        if not p:
            continue
        tot += p["N"]; tot_budget += p["al_budget"]; oltre += p["max"] > BUDGET
        motivo = ", ".join("%s %d" % (k, v) for k, v in p["motivi"].most_common())
        righe.append((cella, p["N"], p["mediana"], p["Q1"], p["Q3"],
                      100.0 * p["al_budget"] / p["N"],
                      100.0 * (p["N"] - p["al_budget"]) / p["N"], motivo))

    intest = ("cell", "N", "median_turns", "Q1", "Q3", "pct_reaching_budget",
              "pct_early_termination", "termination_reason")
    print("\t".join(intest))
    for r in righe:
        print("%s\t%d\t%.1f\t%.1f\t%.1f\t%.2f\t%.2f\t%s" % r)
    if tot:
        print("\nTOTALE\t%d traiettorie\t%d al budget (%.2f%%)"
              % (tot, tot_budget, 100.0 * tot_budget / tot))

    print("\nCONTROLLO a risposta nota")
    print("  nessuna traiettoria oltre %d righe: %s" % (BUDGET, "ok" if oltre == 0 else "FALLITO"),
          file=sys.stderr if oltre else sys.stdout)
    if not tot:
        print("  nessuna traiettoria letta: il prefisso non corrisponde a nessuna cella")
        return 1
    atteso = {"riraccolta": 68, "confermativo": 55, "ablazione": 0}.get(a.braccio)
    if atteso is not None:
        esito = "ok" if tot_budget == atteso else "FALLITO"
        print("  al budget atteso %d, ottenuto %d: %s" % (atteso, tot_budget, esito))
        if esito != "ok":
            return 1
    if oltre:
        return 1
    if a.tsv:
        with open(a.tsv, "w") as fh:
            fh.write("\t".join(intest) + "\n")
            for r in righe:
                fh.write("%s\t%d\t%.1f\t%.1f\t%.1f\t%.2f\t%.2f\t%s\n" % r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
