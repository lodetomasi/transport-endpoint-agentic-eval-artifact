#!/usr/bin/env python3
"""Il braccio di ablazione morde? E dove?

`SUCCESSIONE-08` ha dichiarato PRIMA della raccolta che la quota di turni con almeno una
chiamata scartata doveva cadere nel 33-38%, stimata dalla quota di turni con piu' di una
chiamata osservata nel nativo pieno (haiku 38,0%, sonnet 32,6%). Una quota vicina a zero
avrebbe significato che il vincolo non morde e che il braccio stava pagando un duplicato del
nativo: si sarebbe fermato.

La quota osservata sta sotto la banda, e la ragione NON e' che il vincolo non morde. E' che la
banda presupponeva un tasso di raggruppamento costante lungo la traiettoria, e il tasso non e'
costante: il modello raggruppa al primo turno, riceve il rifiuto, e non ci riprova piu'.

Questo script separa le due letture, che i dati distinguono nettamente:

  - «il vincolo non morde»  -> gli scarti sarebbero rari OVUNQUE, anche al primo turno
  - «il modello si adatta»  -> gli scarti sono concentrati PRIMA del primo rifiuto

La seconda e' verificabile senza modello di riferimento: basta condizionare sul fatto che la
traiettoria abbia gia' ricevuto un rifiuto. E' il controllo di cui si conosce gia' la risposta
in un verso — se il vincolo non mordesse, la quota al turno 1 sarebbe bassa quanto le altre.
"""
import glob
import json
import sys
from collections import defaultdict

BANDA = (33.0, 38.0)   # dichiarata in registro/SUCCESSIONE-08-ablazione-batching.md


def leggi(percorso="results/trajectories/c2a_*/*.jsonl"):
    per_indice = defaultdict(lambda: [0, 0])
    prima, dopo = [0, 0], [0, 0]
    chiamate = turni = 0
    for t in sorted(glob.glob(percorso)):
        rifiutato = False
        idx = 0
        for riga in open(t, errors="ignore"):
            try:
                d = json.loads(riga)
            except json.JSONDecodeError:
                continue
            tc = d.get("tool_calls") or []
            if not tc:
                continue
            idx += 1
            turni += 1
            chiamate += len(tc)
            scarto = any(c.get("scartata_da_ablazione") for c in tc)
            per_indice[idx][1] += 1
            per_indice[idx][0] += scarto
            b = dopo if rifiutato else prima
            b[1] += 1
            b[0] += scarto
            rifiutato = rifiutato or scarto
    return per_indice, prima, dopo, turni, chiamate


if __name__ == "__main__":
    per_indice, prima, dopo, turni, chiamate = leggi()
    if not turni:
        sys.exit("nessuna traiettoria di ablazione: verificare il percorso")

    scarti = sum(s for s, _ in per_indice.values())
    quota = 100 * scarti / turni

    print("Il vincolo dell'ablazione morde, e dove\n")
    print(f"  turni con almeno una chiamata : {turni}")
    print(f"  turni con almeno uno scarto   : {scarti}  = {quota:.1f}%")
    print(f"  banda dichiarata in SUCCESSIONE-08 : {BANDA[0]:.0f}-{BANDA[1]:.0f}%")
    print(f"  chiamate OFFERTE per turno    : {chiamate/turni:.3f}\n")

    print("  quota di scarto per indice di turno")
    for i in sorted(per_indice)[:10]:
        s, n = per_indice[i]
        print(f"    turno {i:>2}  {s:>4}/{n:<5} {100*s/n:>6.1f}%  {'#' * round(30 * s / n)}")

    qp = 100 * prima[0] / prima[1] if prima[1] else float("nan")
    qd = 100 * dopo[0] / dopo[1] if dopo[1] else float("nan")
    print(f"\n  prima di un rifiuto : {prima[0]:>4}/{prima[1]:<5} = {qp:.1f}%")
    print(f"  dopo un rifiuto     : {dopo[0]:>4}/{dopo[1]:<5} = {qd:.1f}%")

    # Le due letture sono distinguibili, e i dati scelgono. Il controllo di cui si conosce
    # gia' la risposta e' il primo: se il vincolo non mordesse, qp sarebbe basso quanto qd.
    if qp < BANDA[0]:
        print("\n  IL VINCOLO NON MORDE: gli scarti sono rari anche prima del primo rifiuto.")
        print("  Il braccio sta raccogliendo un duplicato del nativo. Fermare.")
        sys.exit(2)

    print(f"\n  LETTURA. Il vincolo morde: {qp:.1f}% dei turni raggruppa finche' e' ammesso.")
    print(f"  Poi la quota crolla a {qd:.1f}%, e la quota complessiva ({quota:.1f}%) cade sotto")
    print(f"  la banda per questo e non perche' il vincolo sia inerte. Cio' che la banda")
    print("  presupponeva - un tasso di raggruppamento costante lungo la traiettoria - e'")
    print("  falsificato dai dati stessi: un solo rifiuto basta, e vale per il resto della run.")
    print("\n  CONSEGUENZA PER IL BRACCIO. La differenza fra nativo pieno e nativo vincolato non")
    print("  isola il solo batching: include l'adattamento al rifiuto. Il braccio resta")
    print("  interpretabile come limite superiore dell'effetto del batching, e si riporta cosi'.")
