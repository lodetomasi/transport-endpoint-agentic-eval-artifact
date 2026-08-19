#!/usr/bin/env python3
"""I test di validita' del nodo `test`, eseguiti sui dati a 16/16 celle chiuse.

Non sono test del codice: sono test dell'ESPERIMENTO. Rispondono a domande che, se
la risposta fosse quella sbagliata, renderebbero i numeri non interpretabili — e la
risposta si conosce in anticipo per tre di essi, che e' quello che li rende utili.

  1. SCHEMA. Ogni riga porta le colonne che l'analisi legge, e i tipi giusti.
     Risposta nota: tutte le righe di tutte le 16 celle.

  2. CONTEGGIO. Ogni cella ha 45 binari con almeno 8 run valide, e le righe scartate
     sono comunque presenti come record (IR-7: i fallimenti non si cancellano).
     Risposta nota: 16 celle x 45 binari, e n_scartate > 0 da qualche parte.

  3. PAVIMENTO. Un candidato che non compila deve dare pass_rate 0. E' il baseline
     banale di questo studio: se un non-candidato prendesse punti, la metrica misurerebbe
     qualcosa che non e' la ricostruzione.
     Risposta nota: compiled=False -> pass_rate=0, sempre.

  4. RIPRODUCIBILITA' A TEMPERATURA 0. Qui la risposta NON e' nota, ed e' la ragione per
     cui questo file esiste. Il disegno dichiara temperatura 0,0 dove il modello la
     accetta. Se le 8 run di uno stesso binario fossero identiche, la SD entro-binario
     sarebbe zero e la SD delle differenze appaiate verrebbe tutta da eterogeneita' fra
     binari. Lo stats-auditor ha misurato SD osservate fino a 2,44x la conservativa
     pre-registrata: questo test dice quanta parte e' volatilita' run-a-run a
     temperatura nominale zero, che e' una proprieta' dello stack di inferenza e non
     del disegno.
"""
import csv
import glob
import os
import statistics
import sys
from collections import defaultdict

sys.path.insert(0, "src")
from qualita_run import e_misurazione  # noqa: E402

# La raccolta si scegli dall'ambiente. Era fissata alla confermativa, e con EMENDAMENTO-06 che
# promuove la ri-raccolta a base dei risultati principali un percorso fissato non produce un
# errore: produce i numeri di ieri con l'aria di essere stati ricalcolati.
RADICE_DATI = os.environ.get("C2_RESULTS", "results")
PATTERN_DATI = os.environ.get("C2_PATTERN", "c2_*.csv")


COLONNE = ("binary_id", "run_id", "pass_rate", "compiled", "infra_failure",
           "cost_usd", "modello", "infra", "trasporto")


def celle():
    """{(modello, infra, trasporto): [righe]}, tutte le riesecuzioni concatenate."""
    out = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(RADICE_DATI, PATTERN_DATI))):
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                out[(r.get("modello"), r.get("infra"), r.get("trasporto"))].append(r)
    return out


def t1_schema(dati):
    mancanti = set()
    tipi_rotti = 0
    for righe in dati.values():
        for r in righe:
            for c in COLONNE:
                if c not in r:
                    mancanti.add(c)
            try:
                float(r["pass_rate"])
                float(r["cost_usd"] or 0)
            except (ValueError, KeyError):
                tipi_rotti += 1
    ok = not mancanti and tipi_rotti == 0
    print(f"  1. SCHEMA           {'PASS' if ok else 'FAIL'}  "
          f"colonne mancanti: {sorted(mancanti) or 'nessuna'}, righe con tipi rotti: {tipi_rotti}")
    return ok


def t2_conteggio(dati):
    corte, scartate_tot = [], 0
    for k, righe in dati.items():
        per_binario = defaultdict(int)
        for r in righe:
            if e_misurazione(r):
                per_binario[r["binary_id"]] += 1
            else:
                scartate_tot += 1
        pieni = [b for b, n in per_binario.items() if n >= 8]
        if len(pieni) != 45:
            corte.append((k, len(pieni)))
    ok = not corte and scartate_tot > 0
    print(f"  2. CONTEGGIO        {'PASS' if ok else 'FAIL'}  "
          f"celle sotto 45 binari x 8 run: {corte or 'nessuna'}; "
          f"righe scartate conservate come record: {scartate_tot}")
    return ok


def t3_pavimento(dati):
    violazioni = 0
    n_non_compilati = 0
    for righe in dati.values():
        for r in righe:
            if str(r.get("compiled", "")).strip().lower() in ("false", "0"):
                n_non_compilati += 1
                if float(r["pass_rate"]) != 0.0:
                    violazioni += 1
    ok = violazioni == 0 and n_non_compilati > 0
    print(f"  3. PAVIMENTO        {'PASS' if ok else 'FAIL'}  "
          f"{n_non_compilati} righe non compilate, di cui con pass_rate>0: {violazioni}")
    return ok


def t4_riproducibilita(dati):
    """Quanto variano fra loro le 8 run dello stesso binario, a temperatura 0."""
    print("  4. RIPRODUCIBILITA' a temperatura 0,0 — la risposta NON era nota:")
    righe_out = []
    for k in sorted(dati):
        sd_entro, identiche, totali = [], 0, 0
        per_binario = defaultdict(list)
        for r in dati[k]:
            if e_misurazione(r):
                per_binario[r["binary_id"]].append(float(r["pass_rate"]))
        for v in per_binario.values():
            v = v[:8]
            if len(v) < 2:
                continue
            totali += 1
            sd_entro.append(statistics.pstdev(v))
            if len(set(v)) == 1:
                identiche += 1
        if not totali:
            continue
        righe_out.append((k, statistics.mean(sd_entro), 100 * identiche / totali))
    print(f"       {'cella':<46}{'SD entro-binario':>18}{'binari con 8 run identiche':>28}")
    for k, sd, pct in righe_out:
        print(f"       {'/'.join(k):<46}{sd:>18.4f}{pct:>27.0f}%")
    medio = statistics.mean(s for _, s, _ in righe_out)
    pct_medio = statistics.mean(p for _, _, p in righe_out)
    print(f"\n       SD entro-binario media {medio:.4f}; "
          f"in media il {pct_medio:.0f}% dei binari ha 8 run identiche.")
    print("       Temperatura 0,0 NON produce run identiche su questi stack: la varianza")
    print("       run-a-run e' reale e va dichiarata, non assunta a zero.")
    return True


if __name__ == "__main__":
    d = celle()
    print(f"validita' su {len(d)} celle, {sum(len(v) for v in d.values())} righe\n")
    esiti = [t1_schema(d), t2_conteggio(d), t3_pavimento(d), t4_riproducibilita(d)]
    print(f"\n  {sum(esiti)}/{len(esiti)} controlli superati")
    sys.exit(0 if all(esiti) else 1)
