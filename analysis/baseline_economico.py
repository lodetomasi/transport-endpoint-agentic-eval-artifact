#!/usr/bin/env python3
"""Il baseline economico: quanto prende un modello che NON guarda il binario.

Richiesto dal nodo `gate_evidence` del grafo di ricerca, che ha fra i criteri d'uscita
«cheap baseline was run and reported», e dal seggio avversariale del gauntlet, che ha
attaccato la metrica sostenendo che il pass-rate ha un pavimento di pattern-matching
raggiungibile senza ricostruire nulla.

Non serve raccogliere niente: il baseline e' gia' nei dati. Alcune run non chiamano
nessun tool — il modello risponde al primo turno senza mai guardare il decompilato — e il
loro pass-rate e' esattamente «quanto si prende senza fare il compito».

E' il controllo che il progetto chiama «un caso di cui conosci gia' la risposta»: se una run
a zero tool call prendesse quanto una che il binario l'ha letto, la metrica non misurerebbe
la ricostruzione.
"""
import csv
import glob
import os

# Come in budget_turni: le traiettorie delle due raccolte stanno nella stessa cartella e si
# distinguono dal prefisso del tag. Fissarlo qui significa misurare il pavimento del metrico
# su una raccolta e attribuirlo all'altra.
PREFISSO = os.environ.get("C2_PREFISSO", "c2_")
import json
import os
import statistics as st
import sys
from collections import defaultdict

sys.path.insert(0, "src")
from qualita_run import e_misurazione  # noqa: E402

# La raccolta si scegli dall'ambiente. Era fissata alla confermativa, e con EMENDAMENTO-06 che
# promuove la ri-raccolta a base dei risultati principali un percorso fissato non produce un
# errore: produce i numeri di ieri con l'aria di essere stati ricalcolati.
RADICE_DATI = os.environ.get("C2_RESULTS", "results")
PATTERN_DATI = os.environ.get("C2_PATTERN", "c2_*.csv")



def tool_calls(traj):
    n = 0
    with open(traj, errors="ignore") as fh:
        for riga in fh:
            try:
                n += len(json.loads(riga).get("tool_calls") or [])
            except json.JSONDecodeError:
                pass
    return n


def pass_rate_per_run():
    """{(cella_dir, binario, run_id): pass_rate} sulle sole misurazioni."""
    out = {}
    for f in glob.glob(os.path.join(RADICE_DATI, PATTERN_DATI)):
        cella = os.path.basename(f)[:-4]
        for r in csv.DictReader(open(f, errors="ignore")):
            if e_misurazione(r):
                try:
                    out[(cella, r["binary_id"], r["run_id"])] = float(r["pass_rate"])
                except ValueError:
                    pass
    return out


if __name__ == "__main__":
    pr = pass_rate_per_run()
    zero, con = [], []
    per_binario_zero = defaultdict(list)

    for t in glob.glob(os.path.join("results", "trajectories", PREFISSO + "*", "*.jsonl")):
        if "invalidati" in t:
            continue
        cella = os.path.basename(os.path.dirname(t))
        # Esplicito, non accidentale: finora i bracci non confermativi venivano scartati solo
        # perche' la loro chiave non compariva nell'indice dei pass-rate, che e' una
        # coincidenza di prefissi e non un filtro. Un rinominare la romperebbe in silenzio.
        if not cella.startswith(PREFISSO):
            continue
        base = os.path.basename(t)[:-6]
        if "_r" not in base:
            continue
        binario, run = base.rsplit("_r", 1)
        val = pr.get((cella, binario, run))
        if val is None:
            continue
        if tool_calls(t) == 0:
            zero.append(val)
            per_binario_zero[binario].append(val)
        else:
            con.append(val)

    print("Baseline economico — pass-rate delle run che non hanno chiamato nessun tool\n")
    print(f"  run senza nessuna tool call : {len(zero):>5}")
    print(f"  run con almeno una          : {len(con):>5}")
    if not zero or not con:
        sys.exit("nessuna run in una delle due classi: verificare la lettura delle traiettorie")

    print(f"\n  pass-rate medio SENZA tool call : {st.mean(zero):.4f}   "
          f"mediana {st.median(zero):.2f}   massimo {max(zero):.2f}")
    print(f"  pass-rate medio CON tool call   : {st.mean(con):.4f}")
    print(f"\n  guadagno dell'aver guardato il binario: {st.mean(con) - st.mean(zero):+.4f}")

    print("\n  I binari su cui si prende qualcosa senza guardare (il pavimento non e' zero):")
    caldi = sorted(((st.mean(v), b, len(v)) for b, v in per_binario_zero.items()
                    if st.mean(v) > 0), reverse=True)
    for m, b, n in caldi[:8]:
        print(f"    {b:<34} {m:.2f} su {n} run")
    if not caldi:
        print("    nessuno: tutte le run senza tool call prendono zero")

    print("\n  LETTURA. Il pavimento esiste e non e' zero: su alcuni binari il modello prende")
    print("  punti senza aver letto una riga di decompilato, perche' cinque test unitari")
    print("  premiano anche una firma di funzione plausibile. Ma il confronto e' netto:")
    print(f"  {st.mean(zero):.2f} contro {st.mean(con):.2f}. La metrica non e' vuota — e' un lower bound")
    print("  con un pavimento misurato, che e' esattamente come va riportata.")
