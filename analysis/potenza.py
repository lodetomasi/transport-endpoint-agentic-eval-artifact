#!/usr/bin/env python3
"""Calcolo di potenza per C2, dalla varianza MISURATA del contrasto che C2 misura.

Il sigma da usare non e' quello di C1. C1 confrontava bracci diversi su binari diversi;
C2 confronta due trasporti sullo STESSO binario, quindi la quantita' rilevante e' la SD
della differenza appaiata per binario, e l'appaiamento toglie la varianza fra binari che
domina il numero di C1 (0,211 o 0,274 secondo il pooling). Prendere quello sbagliato non
fallisce: produce un K plausibile e sbagliato.

I dati vengono dai bracci s03 (trasporto nativo) e s03t (trasporto testuale) di C1, che
hanno girato sugli stessi 45 binari con gli stessi due modelli.

    python3 analysis/potenza.py [--s1 <percorso ai results di C1>]
"""
import argparse
import collections
import csv
import glob
import math
import os
import statistics as st
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(QUI), "src"))
from qualita_run import e_misurazione  # noqa: E402

# I due modelli per cui C1 ha girato ENTRAMBI i trasporti sugli stessi binari.
# GPT-OSS-20B e' escluso di proposito: al turno 1 il suo output arriva sul canale
# `reasoning`, che il trasporto testuale non legge, quindi la sua differenza fra trasporti
# misura un difetto di lettura e non il trasporto. Gemma e' escluso perche' il braccio
# nativo non e' eseguibile (400 sul multi-turno), quindi la coppia non esiste.
COPPIE = [
    ("llama-3.3-70b", "s03_llama3370b_N12*.csv", "s03t_llama3370b_N12*.csv"),
    ("haiku-4-5", "s03_haiku45_N12*.csv", "s03t_haiku45_N12*.csv"),
]

Z_ALPHA = 1.959964  # bilaterale, alfa = 0,05
Z_BETA = 0.841621   # potenza 80%
BANDA_FALSIFICATORE = 0.03  # +/-3pp, dalla bozza di claim nel registro del programma


def celle(cartella, pattern):
    """pass_rate per binario, contate una sola volta dalla regola condivisa."""
    acc = collections.defaultdict(list)
    for f in glob.glob(os.path.join(cartella, pattern)):
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                if e_misurazione(r):
                    acc[r["binary_id"]].append(float(r["pass_rate"]))
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s1", default=os.path.expanduser(
        "~/<capitolo-precedente>/research/s1-agentic-layer-cost/mini-pilot/results"))
    a = ap.parse_args()
    if not os.path.isdir(a.s1):
        sys.exit(f"non trovo i results di C1 in {a.s1}")

    sd_per_modello = {}
    print(f"  {'modello':<16}{'K':>4}{'nativo':>9}{'testo':>9}{'delta':>9}"
          f"{'SD(diff)':>10}{'sigma_run':>11}{'% rumore':>10}")
    for nome, pn, pt in COPPIE:
        N, T = celle(a.s1, pn), celle(a.s1, pt)
        com = sorted(set(N) & set(T))
        if len(com) < 2:
            print(f"  {nome}: meno di due binari in comune, salto")
            continue
        d = [st.mean(T[b]) - st.mean(N[b]) for b in com]
        sd_d = st.stdev(d)
        sd_per_modello[nome] = sd_d

        # Decomposizione: la varianza della differenza fra due medie di cella e'
        # eterogeneita' vera fra binari + errore di misura. Il secondo scende coi run per
        # cella, il primo no -- ed e' la ragione per cui piu' run non sostituiscono piu'
        # binari quando l'eterogeneita' domina.
        entro = [st.stdev(v) for v in list(N.values()) + list(T.values()) if len(v) > 1]
        s_run = st.mean(entro)
        n_run = st.mean([len(v) for v in list(N.values()) + list(T.values())])
        var_mis = 2 * s_run ** 2 / n_run
        print(f"  {nome:<16}{len(com):>4}"
              f"{st.mean([st.mean(N[b]) for b in com]):>9.4f}"
              f"{st.mean([st.mean(T[b]) for b in com]):>9.4f}{st.mean(d):>+9.4f}"
              f"{sd_d:>10.4f}{s_run:>11.4f}{100 * var_mis / sd_d ** 2:>9.0f}%")

    if not sd_per_modello:
        sys.exit("nessuna coppia calcolabile")

    pool = math.sqrt(sum(s ** 2 for s in sd_per_modello.values()) / len(sd_per_modello))
    peggio = max(sd_per_modello.values())
    print(f"\n  SD entro-modello, pooling per varianza: {pool:.4f}")
    print(f"  SD del modello peggiore, conservativa:   {peggio:.4f}")

    # Una SD calcolata sull'unione delle differenze dei due modelli sarebbe GONFIATA
    # dalla distanza fra le loro medie (+3,0pp contro -10,4pp): quel numero non e' la
    # variabilita' entro-modello, e usarlo qui sovrastimerebbe K.
    tutte = []
    for nome, pn, pt in COPPIE:
        N, T = celle(a.s1, pn), celle(a.s1, pt)
        com = sorted(set(N) & set(T))
        tutte += [st.mean(T[b]) - st.mean(N[b]) for b in com]
    print(f"  (per confronto, SD dell'unione grezza: {st.stdev(tutte):.4f} — gonfiata "
          f"dall'effetto del modello, non usarla)")

    print("\n  MDE per-modello, test appaiato, 80% di potenza:")
    for K in (30, 45, 60, 79, 90, 120):
        print(f"    K={K:>3}   pooled {Z_TOT * pool / math.sqrt(K) * 100:>5.2f} pp"
              f"   conservativa {Z_TOT * peggio / math.sqrt(K) * 100:>5.2f} pp")

    print(f"\n  K per rilevare la banda del falsificatore ({BANDA_FALSIFICATORE * 100:.0f}pp):")
    for eti, s in (("pooled", pool), ("conservativa", peggio)):
        print(f"    {eti:<14} K = {math.ceil((Z_TOT * s / BANDA_FALSIFICATORE) ** 2)}")

    # Il pavimento: con run infiniti resta solo l'eterogeneita' fra binari.
    print("\n  Pavimento per modello: SD residua a run per cella infiniti, e K che serve")
    for nome, pn, pt in COPPIE:
        N, T = celle(a.s1, pn), celle(a.s1, pt)
        com = sorted(set(N) & set(T))
        if len(com) < 2:
            continue
        d = [st.mean(T[b]) - st.mean(N[b]) for b in com]
        entro = [st.stdev(v) for v in list(N.values()) + list(T.values()) if len(v) > 1]
        s_run, n_run = st.mean(entro), st.mean(
            [len(v) for v in list(N.values()) + list(T.values())])
        var_bin = max(st.stdev(d) ** 2 - 2 * s_run ** 2 / n_run, 0.0)
        sd_inf = math.sqrt(var_bin)
        k_inf = math.ceil((Z_TOT * sd_inf / BANDA_FALSIFICATORE) ** 2) if sd_inf > 0 else 0
        print(f"    {nome:<16} SD_inf = {sd_inf:.4f}   K minimo = {k_inf}")


Z_TOT = Z_ALPHA + Z_BETA

if __name__ == "__main__":
    main()
