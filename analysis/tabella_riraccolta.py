#!/usr/bin/env python3
"""La tabella «originale contro ri-raccolta» del paper, generata dai dati.

PERCHE' E' UN FILE A PARTE. I criteri stanno in `confronto_riraccolta.py`, che e' congelato per
hash (la precedenza esatta del congelamento sta in HASH-CONGELATI.md: 1,9% delle righe esisteva
all'mtime, 73,4% al commit, e la differenza fra le due cifre e' cio' che un terzo puo' verificare). Ho provato ad aggiungere lo stesso il
formato LaTeX li' dentro, ragionando che «cambio solo l'output, i criteri restano»: la guardia
degli hash mi ha preso con una divergenza muta, e aveva ragione. Un file congelato non si tocca
perche' la modifica sembra innocua — e' esattamente il giudizio che il congelamento toglie di
mezzo. Il criterio e la sua presentazione sono due cose, e ora vivono in due file.

Questo script IMPORTA i criteri e non li ridefinisce: soglie, contrasti e regola di lettura
restano quelle congelate, e se qualcuno le cambiasse la guardia se ne accorgerebbe.

    python3 analysis/tabella_riraccolta.py > paper/tables/riraccolta.tex
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from analyze_c2 import carica  # noqa: E402
from confronto_riraccolta import (OTTO, SOGLIA_SEGNI, SOGLIA_COPERTURA,  # noqa: E402
                                  contrasto, segno)

# Sovrascrivibili da ambiente: e' l'unico modo di collaudare la catena su dati costruiti
# senza scrivere dentro results/, che e' append-only. I default sono i percorsi veri.
VECCHIA = os.environ.get("C2_VECCHIA", os.path.join(os.path.dirname(QUI), "results"))
NUOVA = os.environ.get("C2_NUOVA", os.path.join(os.path.dirname(QUI), "results", "riraccolta"))


if __name__ == "__main__":
    if not os.path.isdir(NUOVA):
        sys.exit("la ri-raccolta non ha ancora prodotto dati")
    vecchie, _ = carica(VECCHIA)
    nuove, _ = carica(NUOVA)
    if not nuove:
        sys.exit("nessuna misurazione nella ri-raccolta")

    righe, concordi, dentro, identici = [], 0, 0, 0
    for eti, tipo, mod in OTTO:
        nv, mv, lov, hiv, _, _ = contrasto(vecchie, tipo, mod)
        nn, mn, _lon, _hin, _, _ = contrasto(nuove, tipo, mod)
        if nv < 2 or nn < 2:
            continue
        cop = lov <= mn <= hiv
        concordi += segno(mv) == segno(mn)
        dentro += cop
        identici += abs(mv - mn) < 1e-9
        righe.append((eti, mod, mv, lov, hiv, mn, cop))

    if len(righe) < 8:
        sys.exit(f"solo {len(righe)}/8 contrasti calcolabili: la ri-raccolta non e' completa, "
                 "e una tabella su un braccio parziale stima i binari facili")
    # La soglia non e' «almeno uno». Su 45 binari due raccolte possono produrre la stessa
    # media per un contrasto senza che nulla sia rotto, e un collaudo su dati simulati mi ha
    # mostrato che la versione precedente di questo controllo si rifiutava di generare la
    # tabella per quel caso del tutto plausibile. E' la coincidenza SISTEMATICA a denunciare
    # che si sta leggendo due volte la stessa cartella, non una singola.
    if identici >= 4:
        sys.exit(f"{identici}/8 contrasti identici fra le due raccolte: su un apparato non "
                 "deterministico questa non e' conferma, e' il sospetto che si stia leggendo "
                 "due volte la stessa cartella. Verificare prima di generare la tabella.")
    if identici:
        print(f"% Attenzione: {identici}/8 contrasti coincidono a meno di 1e-9. Plausibile su "
              "45 binari, ma vale la pena guardarlo.", file=sys.stderr)

    print("% Generata da analysis/tabella_riraccolta.py — non modificare a mano.")
    print("\\begin{table}[t]")
    print("\\centering")
    print("\\caption{The same eight contrasts measured twice: the original collection, and an "
          "independent re-collection on workspaces isolated per cell. Differences in percentage "
          "points; the last column states whether the re-collected effect falls inside the "
          "original 95\\% interval. The criteria and their "
          "thresholds were written before the comparison could be computed; their timing is "
          "stated precisely in \\S\\ref{sec:threats}, where it is weaker than the "
          "pre-registration's.}")
    print("\\label{tab:riraccolta}")
    print("\\footnotesize")
    print("\\setlength{\\tabcolsep}{5pt}")
    print("\\begin{tabular}{@{}llrrc@{}}")
    print("\\toprule")
    print(" & model & orig. & re-coll. & in CI \\\\")
    print("\\midrule")
    for eti, mod, mv, _lov, _hiv, mn, cop in righe:
        print(f"{eti} & {mod} & ${100*mv:+.1f}$ & ${100*mn:+.1f}$ & "
              f"{'yes' if cop else 'no'} \\\\")
    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\end{table}")
    print(f"\n% criterio 1, segni concordi: {concordi}/8 (soglia {SOGLIA_SEGNI}) -> "
          f"{'invariato' if concordi >= SOGLIA_SEGNI else 'diverge'}")
    print(f"% criterio 3, copertura IC95: {dentro}/8 (soglia {SOGLIA_COPERTURA}) -> "
          f"{'invariato' if dentro >= SOGLIA_COPERTURA else 'diverge'}")
