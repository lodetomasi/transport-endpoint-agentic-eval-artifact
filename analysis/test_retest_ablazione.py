#!/usr/bin/env python3
"""Due raccolte complete della stessa cella, a tre ore di distanza: quanto differiscono.

NON ERA PIANIFICATO. La cella `claude-haiku-4-5 / databricks / native` del braccio di ablazione
e' stata raccolta due volte per un difetto del driver (`NOTA-02`): 45 binari x 16 run invece di
8. Il difetto e' costato circa $8,70, e in cambio ha prodotto l'unica cosa che questo studio non
poteva comprare altrimenti — la stessa cella, stesso apparato, stesso protocollo, misurata due
volte a ore diverse.

E' la misura del RUMORE DI FONDO fra due raccolte: quanto si muove un numero quando non cambia
nulla. Serve per leggere la ri-raccolta di `EMENDAMENTO-06`, dove la domanda e' se la differenza
fra le due raccolte sia attribuibile all'apparato oppure al fatto che due raccolte differiscono
sempre. Senza questo numero quella domanda non ha un metro.

Vale per UNA cella e UN modello: haiku e' il piu' stabile del roster (98-100% dei binari con
otto run identiche), quindi questo e' un LIMITE INFERIORE del rumore, non una stima per il
resto della griglia. Si riporta cosi'.
"""
import csv
import glob
import os
import statistics as st
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, os.path.join(RADICE, "src"))
from qualita_run import e_misurazione  # noqa: E402

RUNS = 8
PRIMA = "results/ablazione/c2a_claude-haiku-4-5_databricks_native1_redo2.csv"
DOPO = "results/ablazione/c2a_claude-haiku-4-5_databricks_native1.csv"


def per_binario(percorso):
    d = {}
    with open(os.path.join(RADICE, percorso), errors="ignore") as fh:
        for r in csv.DictReader(fh):
            if e_misurazione(r):
                d.setdefault(r["binary_id"], []).append(float(r["pass_rate"]))
    return {k: st.mean(v[:RUNS]) for k, v in d.items() if len(v) >= RUNS}


def finestra(percorso):
    ts = [r.get("timestamp", "")[:19]
          for r in csv.DictReader(open(os.path.join(RADICE, percorso), errors="ignore"))
          if e_misurazione(r)]
    return (min(ts), max(ts)) if ts else ("?", "?")


if __name__ == "__main__":
    for p in (PRIMA, DOPO):
        if not os.path.exists(os.path.join(RADICE, p)):
            sys.exit(f"manca {p}")

    A, B = per_binario(PRIMA), per_binario(DOPO)
    com = sorted(set(A) & set(B))
    if len(com) < 20:
        sys.exit(f"solo {len(com)} binari in comune: una delle due raccolte non e' completa, "
                 "e un confronto su un prefisso stima i binari facili")

    fa, fb = finestra(PRIMA), finestra(DOPO)
    d = [B[k] - A[k] for k in com]
    ident = sum(1 for x in d if x == 0)

    print("Test-retest: la stessa cella raccolta due volte\n")
    print(f"  raccolta 1: {fa[0]} -> {fa[1]}")
    print(f"  raccolta 2: {fb[0]} -> {fb[1]}")
    print(f"  binari in entrambe: {len(com)}\n")
    print(f"  media 1                 {st.mean(A[k] for k in com):.4f}")
    print(f"  media 2                 {st.mean(B[k] for k in com):.4f}")
    print(f"  differenza              {st.mean(d):+.4f}  ({100*st.mean(d):+.2f}pp)")
    print(f"  binari identici         {ident}/{len(com)}")
    print(f"  scarto massimo          {max(abs(x) for x in d):.2f} su un binario")
    if len(d) > 1:
        print(f"  deviazione standard     {st.stdev(d):.4f}")

    # Il controllo di cui si conosce gia' la risposta: se il confronto stesse leggendo due volte
    # lo STESSO file, ogni binario coinciderebbe. 42 su 43 e' alta stabilita'; 43 su 43 sarebbe
    # il sospetto di un errore di lettura.
    if ident == len(com):
        print("\n  ATTENZIONE: tutti i binari coincidono. Verificare che i due percorsi siano")
        print("  file diversi prima di leggere questo numero come stabilita'.")
        sys.exit(1)

    print(f"\n  LETTURA. Fra due raccolte complete della stessa cella, separate da ore, il")
    print(f"  punteggio si muove di {100*abs(st.mean(d)):.2f}pp. E' il metro con cui va letta la")
    print("  ri-raccolta di EMENDAMENTO-06: una differenza di quest'ordine e' rumore, una di")
    print("  ordine superiore no. Vale per il modello piu' stabile del roster, quindi come")
    print("  limite inferiore del rumore e non come stima per l'intera griglia.")
