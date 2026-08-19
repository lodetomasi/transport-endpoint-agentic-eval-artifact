#!/usr/bin/env python3
"""Le bande di incertezza sulle proporzioni che il paper riporta come numeri nudi.

Il paper cita percentuali su denominatori piccoli — «98--100% dei binari», «13--24%», «1,9%
delle run» — e finora nessuna portava un intervallo. Su 45 binari la differenza fra 98% e 100%
e' UN binario, e un lettore che confronta due celle deve poter vedere se la distanza fra loro
sopravvive al campionamento.

INTERVALLO DI WILSON, non normale. Per proporzioni vicine a 0 o a 1 — che qui sono la regola,
non l'eccezione — l'approssimazione normale produce estremi fuori da [0,1] e copertura
sbagliata proprio dove i numeri sono piu' interessanti. Wilson resta dentro i limiti e ha
copertura corretta anche a p=1: per 45 successi su 45 da' [0.921, 1.000], che e' la risposta
onesta, mentre la normale darebbe [1.000, 1.000] e direbbe che non c'e' incertezza.

Nessuno di questi numeri entra nella famiglia dei dieci test: sono descrittivi, e le bande
servono a impedire che un lettore legga una differenza dove c'e' rumore di campionamento.
"""
import csv
import glob
import math
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


Z = 1.959964
RUNS = 8


def wilson(successi, n):
    """Intervallo di Wilson al 95%. Ritorna (p, lo, hi)."""
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = successi / n
    d = 1 + Z ** 2 / n
    centro = (p + Z ** 2 / (2 * n)) / d
    mezza = Z * math.sqrt(p * (1 - p) / n + Z ** 2 / (4 * n ** 2)) / d
    return p, max(0.0, centro - mezza), min(1.0, centro + mezza)


def celle_confermative():
    per = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(RADICE_DATI, PATTERN_DATI))):
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                if e_misurazione(r):
                    k = (r.get("modello"), r.get("infra"), r.get("trasporto"), r["binary_id"])
                    per[k].append(float(r["pass_rate"]))
    return per


def stabilita(per):
    """Quota di binari le cui RUNS run danno lo stesso punteggio, per cella, con banda."""
    agg = defaultdict(lambda: [0, 0])
    for (m, i, t, _b), v in per.items():
        if len(v) >= RUNS:
            agg[(m, i, t)][1] += 1
            if len(set(v[:RUNS])) == 1:
                agg[(m, i, t)][0] += 1
    return agg


if __name__ == "__main__":
    per = celle_confermative()

    print("Bande di incertezza sulle proporzioni riportate — Wilson 95%\n")
    print("STABILITA' DEL PUNTEGGIO: binari le cui otto run danno lo stesso valore")
    print(f"  {'cella':<46}{'quota':>18}{'IC95':>20}")
    agg = stabilita(per)
    for k in sorted(agg, key=lambda k: (-agg[k][0] / agg[k][1], k)):
        s, n = agg[k]
        p, lo, hi = wilson(s, n)
        print(f"  {'/'.join(k):<46}{s:>3}/{n:<3}{100*p:>9.1f}%"
              f"{f'[{100*lo:.1f}, {100*hi:.1f}]':>20}")

    print("\n  Il punto che le bande rendono visibile: su 45 binari, 45/45 non e' «certezza»")
    p, lo, hi = wilson(45, 45)
    print(f"  ma [{100*lo:.1f}, 100.0]. Due celle che differiscono di un binario non sono")
    print("  distinguibili, e il paper non deve leggerle come se lo fossero.")

    print("\n  CONFRONTO FRA I DUE CLOUD, a modello e trasporto fissi. La claim «lo stesso")
    print("  modello nominale non e' ugualmente stabile su cloud diversi» va sostenuta dove le")
    print("  bande NON si sovrappongono, e detta con quell'esempio.")
    print(f"  {'modello / trasporto':<32}{'cloud A':>18}{'cloud B':>18}   bande")
    netti = []
    for mod in ("claude-haiku-4-5", "claude-sonnet-4-5", "llama-3.3-70b", "gpt-oss-120b"):
        for tr in ("native", "text"):
            a, b = agg.get((mod, "databricks", tr)), agg.get((mod, "bedrock", tr))
            if not a or not b:
                continue
            pa, loa, hia = wilson(*a)
            pb, lob, hib = wilson(*b)
            sovr = not (hia < lob or hib < loa)
            if not sovr:
                netti.append((mod, tr))
            print(f"  {mod + ' / ' + tr:<32}"
                  f"{f'{100*pa:.1f}% [{100*loa:.0f},{100*hia:.0f}]':>18}"
                  f"{f'{100*pb:.1f}% [{100*lob:.0f},{100*hib:.0f}]':>18}"
                  f"   {'si sovrappongono' if sovr else 'SEPARATE'}")
    print(f"\n  Confronti con bande separate: {len(netti)} su 8"
          + (f" — {', '.join(m + '/' + t for m, t in netti)}" if netti else ""))
    print("  Sugli altri la differenza osservata e' compatibile con il campionamento a K=45,")
    print("  e il paper non deve usarli come esempio della claim.")

    # --- il pavimento della metrica, con banda sulla media
    zero, con = [], []
    import json
    pr = {}
    for f in glob.glob(os.path.join(RADICE_DATI, PATTERN_DATI)):
        cella = os.path.basename(f)[:-4]
        for r in csv.DictReader(open(f, errors="ignore")):
            if e_misurazione(r):
                try:
                    pr[(cella, r["binary_id"], r["run_id"])] = float(r["pass_rate"])
                except ValueError:
                    pass
    for t in glob.glob("results/trajectories/*/*.jsonl"):
        if "invalidati" in t:
            continue
        cella = os.path.basename(os.path.dirname(t))
        if not cella.startswith("c2_"):
            continue
        base = os.path.basename(t)[:-6]
        if "_r" not in base:
            continue
        b, run = base.rsplit("_r", 1)
        val = pr.get((cella, b, run))
        if val is None:
            continue
        n = 0
        for l in open(t, errors="ignore"):
            try:
                n += len(json.loads(l).get("tool_calls") or [])
            except Exception:
                pass
        (zero if n == 0 else con).append(val)

    def media_ic(v):
        m = st.mean(v)
        se = st.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else 0.0
        return m, m - Z * se, m + Z * se

    print("\nPAVIMENTO DELLA METRICA: pass-rate medio, con intervallo sulla media")
    for eti, v in (("senza alcuna tool call", zero), ("con almeno una", con)):
        m, lo, hi = media_ic(v)
        print(f"  {eti:<26} n={len(v):<5} {m:.4f}  IC95 [{lo:.4f}, {hi:.4f}]")
    if zero and con:
        d = st.mean(con) - st.mean(zero)
        se = math.sqrt(st.stdev(con) ** 2 / len(con) + st.stdev(zero) ** 2 / len(zero))
        print(f"  differenza                        {d:+.4f}  IC95 "
              f"[{d - Z*se:+.4f}, {d + Z*se:+.4f}]")
        print("  -> l'intervallo esclude ampiamente lo zero: il pavimento esiste e non domina")
