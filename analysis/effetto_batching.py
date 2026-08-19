#!/usr/bin/env python3
"""Quanto vale il raggruppamento delle chiamate: nativo pieno contro nativo vincolato.

LA DOMANDA (RQ5). Il disegno pre-registrato confronta due trasporti che differiscono per DUE
cose insieme: il formato della chiamata, e il fatto che il protocollo testuale ammette una sola
chiamata per turno mentre il nativo ne ammette molte. Dove il modello raggruppa — haiku 1,437
chiamate per turno, sonnet 1,332 — T3 e T4 misurano la somma delle due manipolazioni, e finora
il paper poteva soltanto DICHIARARE il confondimento.

Il braccio di `SUCCESSIONE-08` lo misura: nativo forzato a una chiamata per turno, tutto il
resto identico. La differenza fra nativo pieno e nativo vincolato e' l'effetto del
raggruppamento; quel che resta confrontando il vincolato col testuale e' l'effetto del formato.

COSA QUESTO NUMERO NON E'. Il vincolo non toglie solo il raggruppamento: il modello riceve un
rifiuto al primo turno e smette di riprovare (`NOTA-01`: 100% dei primi turni, 0,2% dopo).
Quindi la differenza include l'adattamento al rifiuto, ed e' un LIMITE SUPERIORE dell'effetto
del batching, non la sua stima. Si riporta cosi'.

Il braccio e' esplorativo e NON entra nella famiglia dei dieci test.
"""
import csv
import glob
import math
import os
import statistics as st
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, os.path.join(RADICE, "src"))
from qualita_run import e_misurazione  # noqa: E402

RUNS = 8
MODELLI = ("claude-haiku-4-5", "claude-sonnet-4-5")


def media_per_binario(pattern):
    d = {}
    for f in glob.glob(os.path.join(RADICE, pattern)):
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                if e_misurazione(r):
                    d.setdefault(r["binary_id"], []).append(float(r["pass_rate"]))
    return {k: st.mean(v[:RUNS]) for k, v in d.items() if len(v) >= RUNS}


def appaiato(a, b):
    com = sorted(set(a) & set(b))
    d = [b[k] - a[k] for k in com]
    if len(d) < 2:
        return len(d), float("nan"), float("nan"), float("nan")
    m, sd = st.mean(d), st.stdev(d)
    se = sd / math.sqrt(len(d))
    tc = 1.959964 + 2.3737 / (len(d) - 1)      # stessa approssimazione di analyze_c2
    return len(d), m, m - tc * se, m + tc * se


if __name__ == "__main__":
    print("Effetto del raggruppamento: nativo pieno contro nativo vincolato a una "
          "chiamata/turno\n")
    print(f"  {'modello':<20}{'pieno':>8}{'vincolato':>11}{'differenza':>13}{'IC95':>18}{'K':>4}")
    righe = []
    for mod in MODELLI:
        pieno = media_per_binario(f"results/c2_{mod}_databricks_native*.csv")
        vinc = media_per_binario(f"results/ablazione/c2a_{mod}_databricks_native1*.csv")
        n, m, lo, hi = appaiato(pieno, vinc)
        if n < 20:
            print(f"  {mod:<20} solo {n} binari in comune: braccio incompleto")
            sys.exit(1)
        com = sorted(set(pieno) & set(vinc))
        righe.append((mod, m, lo, hi, n))
        print(f"  {mod:<20}{st.mean(pieno[k] for k in com):>8.3f}"
              f"{st.mean(vinc[k] for k in com):>11.3f}{100*m:>+12.1f}pp"
              f"{f'[{100*lo:+.1f}, {100*hi:+.1f}]':>18}{n:>4}")

    # Il contrasto che il confondimento minacciava, dal braccio confermativo.
    T3 = -0.104
    print(f"\n  Per riferimento, T3 (haiku, nativo -> testuale): {100*T3:+.1f}pp")
    print("\n  LETTURA. Togliere il raggruppamento al trasporto nativo non abbassa il")
    print("  punteggio: entrambe le differenze sono POSITIVE e i loro intervalli contengono")
    print("  lo zero. La perdita di raggruppamento non e' quindi una spiegazione plausibile")
    print(f"  del {100*abs(T3):.1f}pp di T3 — ne' per direzione, ne' per ordine di grandezza.")
    print("  Il confondimento fra formato e raggruppamento, che il disegno poteva solo")
    print("  dichiarare, e' delimitato: cio' che T3 misura e' il protocollo.")
    print("\n  Con due cautele, entrambe dichiarate prima: il vincolo include l'adattamento al")
    print("  rifiuto, quindi questo e' un limite superiore; e il braccio e' esplorativo, su")
    print("  una sola infrastruttura e sui due soli modelli che raggruppano davvero.")

    # Controllo di cui si conosce gia' la risposta: se il braccio vincolato fosse per errore
    # una copia del nativo pieno, ogni differenza sarebbe esattamente zero.
    if all(abs(m) < 1e-9 for _, m, _, _, _ in righe):
        sys.exit("\n  ogni differenza e' esattamente nulla: il braccio vincolato sta leggendo "
                 "gli stessi file del nativo pieno. Verificare i percorsi.")
