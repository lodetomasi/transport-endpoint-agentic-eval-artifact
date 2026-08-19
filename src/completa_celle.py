#!/usr/bin/env python3
"""Quante run mancano a una cella, e su quali binari.

Una cella e' completa quando ogni binario dell'elenco congelato ha RUNS run VALIDE. Le
riesecuzioni si accumulano nella catena di suffissi ("", "_redo", "_redo2", "_redo3"),
perche' results/ e' append-only e un file non si riscrive.

Il conteggio e' sulle run VALIDE, non sulle righe: una riga con `infra_failure` e' stata
pagata ma non e' una misurazione, e contarla come tale lascerebbe la cella corta senza che
niente lo dica. In C1 lo stesso errore al contrario -- contare col filtro che scarta le celle
corte -- produsse deficit di 8 per celle che ne volevano 1.

    python3 src/completa_celle.py                       # tutte le celle
    python3 src/completa_celle.py --cella <eti>/<infra>/<trasporto> --scrivi-elenco <file>
"""
import argparse
import collections
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, QUI)
from qualita_run import e_misurazione  # noqa: E402

SUFFISSI = ("", "_redo", "_redo2", "_redo3")
RUNS = 8


def elenco_congelato():
    p = os.path.join(RADICE, "configs", "binari_holdout.txt")
    return [r.split("#")[0].strip() for r in open(p).read().splitlines()
            if r.split("#")[0].strip()]


BRACCI = ("confermativo", "ablazione", "riraccolta", "esplorativo")


def percorso_cella(eti, infra, trasporto, suf, braccio="confermativo"):
    """Dove sta il CSV di una cella. Un braccio, un posto, una funzione sola: quando la
    regola viveva in due copie, il driver dell'ablazione chiedeva a questa funzione se la
    cella fosse completa e riceveva la risposta del braccio CONFERMATIVO — che e' chiuso.
    Il driver avrebbe stampato «CHIUSA gia'», speso zero e chiuso con successo, senza
    raccogliere niente. Trovato da `<revisione-avversariale-dell-apparato>` prima della raccolta.

    IL PREFISSO NEL NOME NON E' COSMETICO. `run_minipilot` deriva il tag della workdir e
    della directory di traiettorie da `Path(--out).stem`, cioe' dal NOME e non dal percorso.
    Due bracci con lo stesso nome file in cartelle diverse condividono il tag, e
    `write_trajectory` apre in "w": la ri-raccolta avrebbe sovrascritto le 5.760 traiettorie
    dell'originale, in silenzio e senza recupero. Percorsi distinti non bastano — servono
    STEM distinti, ed e' quello che `test/test_bracci.py` verifica.

    Un braccio sconosciuto solleva invece di ricadere sul confermativo: e' il modo in cui un
    refuso manderebbe una raccolta a scrivere sopra il braccio sbagliato."""
    if braccio not in BRACCI:
        raise ValueError(f"braccio sconosciuto: {braccio!r} (attesi {BRACCI})")
    if braccio == "ablazione":
        return os.path.join(RADICE, "results", "ablazione",
                            f"c2a_{eti}_{infra}_{trasporto}1{suf}.csv")
    if braccio == "riraccolta":
        return os.path.join(RADICE, "results", "riraccolta",
                            f"c2r_{eti}_{infra}_{trasporto}{suf}.csv")
    if braccio == "esplorativo" or infra == "azure":
        return os.path.join(RADICE, "results", "esplorativo",
                            f"c2x_{eti}_{infra}_{trasporto}{suf}.csv")
    return os.path.join(RADICE, "results", f"c2_{eti}_{infra}_{trasporto}{suf}.csv")


def valide_per_binario(eti, infra, trasporto, braccio="confermativo"):
    """Somma sulla catena di suffissi. Un file assente non e' un errore: e' una
    riesecuzione che non e' servita."""
    n = collections.Counter()
    for suf in SUFFISSI:
        f = percorso_cella(eti, infra, trasporto, suf, braccio)
        if not os.path.exists(f):
            continue
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                if e_misurazione(r):
                    n[r["binary_id"]] += 1
    return n


def prossimo_suffisso(eti, infra, trasporto, braccio="confermativo"):
    """Il primo suffisso libero NEL BRACCIO GIUSTO.

    Senza il flag, questa funzione guardava i file del confermativo anche quando il driver
    stava raccogliendo l'ablazione: per haiku, dove `` e `_redo` sono gia' occupati dalla
    raccolta confermativa, il primo file dell'ablazione e' nato `_redo2` — un nome che
    dichiara una seconda ripresa dove c'era una prima raccolta. Peggio: con tutti e quattro i
    suffissi confermativi occupati, il driver sarebbe uscito con «esauriti i suffissi» per una
    cella di ablazione vuota. Stesso difetto che `<revisione-avversariale-dell-apparato>` ha trovato in `deficit`, in
    una seconda funzione."""
    for suf in SUFFISSI:
        if not os.path.exists(percorso_cella(eti, infra, trasporto, suf, braccio)):
            return suf
    sys.exit(f"c2_{eti}_{infra}_{trasporto}: esauriti i suffissi {SUFFISSI}. Un quinto "
             f"suffisso nessuna analisi lo legge, quindi non lo creo.")


def deficit(eti, infra, trasporto, braccio="confermativo"):
    n = valide_per_binario(eti, infra, trasporto, braccio)
    manca = {b: RUNS - n.get(b, 0) for b in elenco_congelato() if n.get(b, 0) < RUNS}
    return n, manca


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cella", default=None)
    ap.add_argument("--scrivi-elenco", default=None,
                    help="scrive i binari carenti su questo file e stampa il deficit massimo")
    a = ap.parse_args()

    sys.path.insert(0, QUI)
    from raccogli_c2 import celle  # noqa: E402
    scelte = [tuple(a.cella.split("/"))] if a.cella else list(celle())

    massimo = 0
    for eti, infra, trasporto in scelte:
        n, manca = deficit(eti, infra, trasporto)
        tot = sum(n.values())
        if not manca:
            print(f"  {eti}/{infra}/{trasporto}: CHIUSA ({tot} valide)")
            continue
        d = max(manca.values())
        massimo = max(massimo, d)
        print(f"  {eti}/{infra}/{trasporto}: {tot} valide, {len(manca)} binari carenti, "
              f"deficit max {d}")
        if a.scrivi_elenco and a.cella:
            with open(a.scrivi_elenco, "w") as f:
                f.write("\n".join(sorted(manca)) + "\n")
            print(f"    -> {len(manca)} binari in {a.scrivi_elenco}, servono {d} run each")
    if a.scrivi_elenco:
        print(f"DEFICIT_MAX={massimo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
