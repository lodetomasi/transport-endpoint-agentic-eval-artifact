#!/usr/bin/env python3
"""Quanti contrasti hanno una sensibilita' realizzata piu' grossolana di ciascuna delle DUE soglie.

Esistono due soglie e il testo le confondeva in una: la banda del falsificatore, ±3pp, fissata dalla
pre-registrazione prima di ogni dispersione; e l'MDE del disegno, 4,87pp, calcolato sulla SD ereditata.
Sono conteggi diversi -- 6 su 8 e 5 su 8 -- e attribuirne uno all'altra soglia e' un errore di fatto.

CONTROLLO A RISPOSTA NOTA: la soglia 0 deve dare 8 su 8, e una soglia oltre il massimo osservato 0 su 8.
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis"))
os.environ.setdefault("C2_RESULTS", "results/riraccolta")
os.environ.setdefault("C2_PATTERN", "c2r_*.csv")
import potenza_per_contrasto as pc  # noqa: E402

Z80 = 1.959964 + 0.841621
MDE = {t: 100 * Z80 * sd / math.sqrt(45) for t, _, sd in pc.SD}
oltre = lambda s: sum(1 for v in MDE.values() if v > s)

print("  MDE per contrasto (pp):",
      ", ".join(f"{t}={v:.2f}" for t, v in sorted(MDE.items(), key=lambda kv: kv[1])))
print(f"  oltre 3pp   : {oltre(3.0)} su {len(MDE)}   (la banda del falsificatore pre-registrata)")
print(f"  oltre 4,87pp: {oltre(4.87)} su {len(MDE)}   (l'MDE su cui il disegno e' stato dimensionato)")
print("\n  CONTROLLO a risposta nota")
print(f"    soglia 0 deve dare {len(MDE)}: {oltre(0)} -> {'ok' if oltre(0) == len(MDE) else 'FALLITO'}")
print(f"    soglia 100 deve dare 0: {oltre(100)} -> {'ok' if oltre(100) == 0 else 'FALLITO'}")
sys.exit(0 if oltre(0) == len(MDE) and oltre(100) == 0 else 1)
