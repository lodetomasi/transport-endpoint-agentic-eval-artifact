#!/usr/bin/env python3
"""L'unica definizione di «quanto abbiamo speso». Tutto cio' che sorveglia il tetto la usa.

PERCHE' ESISTE. La spesa era definita due volte — in `sorveglia_costi.sh` (che UCCIDE i
processi al superamento) e in `check_cost.sh` (che fa il referto) — per enumerazione di
cartelle:

    glob("results/c2_*.csv") + glob("results/esplorativo/*.csv")

Il commento in `sorveglia_costi.sh` documenta che le due copie erano gia' divergute una volta,
nell'agosto 2026, e che la correzione fu aggiungere `esplorativo` a entrambe. La correzione
per enumerazione non tiene: appena e' nata `results/ablazione/`, il tetto e' tornato cieco, e
questa volta ha morso davvero — $22,47 spesi e invisibili al sorvegliante, mentre il diario
registrava «nessuna crescita, cella lenta o bloccata» a raccolta viva.

Il tetto protegge un conto in banca, non una cartella. Quindi la definizione e' ricorsiva su
tutto `results/`, e ogni cartella futura e' coperta per costruzione invece che per memoria.

Uso:
    python3 analysis/spesa_totale.py            # il totale, una riga, per gli script
    python3 analysis/spesa_totale.py --dettaglio
    python3 analysis/spesa_totale.py --impronta # byte totali dei CSV: cresce a ogni run
    python3 analysis/spesa_totale.py --autotest # i due sensi, su dati costruiti
"""
import argparse
import csv
import glob
import os
import sys
import tempfile


def csv_di_spesa(radice="results"):
    """Ogni CSV sotto la radice, a qualunque profondita'. Nessun elenco da tenere aggiornato."""
    return sorted(glob.glob(os.path.join(radice, "**", "*.csv"), recursive=True))


def spesa(radice="results"):
    t = 0.0
    for f in csv_di_spesa(radice):
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                try:
                    t += float(r.get("cost_usd") or 0)
                except (TypeError, ValueError):
                    pass
    return t


def impronta(radice="results"):
    """Byte totali dei CSV. Cresce a ogni run scritta, ovunque venga scritta — che e' il
    punto: la rilevazione «sta crescendo?» era cieca esattamente come il totale, e per la
    stessa ragione."""
    return sum(os.path.getsize(f) for f in csv_di_spesa(radice) if os.path.exists(f))


def per_cartella(radice="results"):
    out = {}
    for f in csv_di_spesa(radice):
        d = os.path.dirname(f) or radice
        s = 0.0
        for r in csv.DictReader(open(f, errors="ignore")):
            try:
                s += float(r.get("cost_usd") or 0)
            except (TypeError, ValueError):
                pass
        out[d] = out.get(d, 0.0) + s
    return out


def autotest():
    """I due sensi, come vuole il progetto: il caso che deve fallire con la vecchia
    definizione, e il caso che deve passare con entrambe. Senza il secondo, una funzione che
    somma qualunque cosa sembrerebbe corretta."""
    with tempfile.TemporaryDirectory() as d:
        r = os.path.join(d, "results")
        for sub, nome, costo in [("", "c2_modello_cloud_native.csv", 10.0),
                                 ("ablazione", "c2a_modello.csv", 5.0),
                                 ("riraccolta", "c2r_modello.csv", 3.0),
                                 ("invalidati/lotto1", "c2_vecchio.csv", 4.0)]:
            p = os.path.join(r, sub)
            os.makedirs(p, exist_ok=True)
            with open(os.path.join(p, nome), "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["binary_id", "cost_usd"])
                w.writerow(["progX", f"{costo}"])

        # senso 1 -- DEVE trovare tutto: e' il caso che la vecchia definizione sbagliava
        tot = spesa(r)
        assert abs(tot - 22.0) < 1e-9, f"totale {tot}, atteso 22.0 (10+5+3+4)"

        # senso 2 -- DEVE dare il numero giusto anche quando c'e' solo il confermativo,
        # altrimenti una funzione che somma il doppio passerebbe il senso 1
        solo = os.path.join(d, "solo")
        os.makedirs(solo)
        with open(os.path.join(solo, "c2_x.csv"), "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["binary_id", "cost_usd"])
            w.writerow(["progY", "7.77"])
        uno = spesa(solo)
        assert abs(uno - 7.77) < 1e-9, f"totale {uno}, atteso 7.77"

        # senso 3 -- una radice vuota vale zero, non solleva
        vuota = os.path.join(d, "vuota")
        os.makedirs(vuota)
        assert spesa(vuota) == 0.0

        # e l'impronta cresce quando si aggiunge una riga in una cartella NUOVA
        prima = impronta(r)
        nuova = os.path.join(r, "cartella_mai_vista")
        os.makedirs(nuova)
        with open(os.path.join(nuova, "z.csv"), "w", newline="") as fh:
            fh.write("binary_id,cost_usd\nprogZ,1.0\n")
        assert impronta(r) > prima, "l'impronta non vede una cartella nuova"
    print("  autotest: 4 controlli, tutti passati (totale, singola, vuota, impronta)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--radice", default="results")
    ap.add_argument("--dettaglio", action="store_true")
    ap.add_argument("--impronta", action="store_true")
    ap.add_argument("--autotest", action="store_true")
    a = ap.parse_args()

    if a.autotest:
        sys.exit(autotest())
    if a.impronta:
        print(impronta(a.radice))
        sys.exit(0)
    if a.dettaglio:
        d = per_cartella(a.radice)
        for k in sorted(d, key=lambda k: -d[k]):
            print(f"  {k:<42} ${d[k]:>8.2f}")
        print(f"  {'TOTALE':<42} ${sum(d.values()):>8.2f}")
        sys.exit(0)
    print(f"{spesa(a.radice):.4f}")
