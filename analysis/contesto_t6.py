#!/usr/bin/env python3
"""SPEC-14 — da cosa e' composto il divario di token in ingresso fra le due celle di T6.

PERCHE' ESISTE. Il paper attribuiva un rapporto di 2,3x fra i token in ingresso dichiarati dai
due provider a «cio' che ogni stack MANDA» — scaffolding, serializzazione degli schemi,
troncamento della storia. Nessuna delle tre e' osservabile dall'esterno, e il conteggio del
provider e' l'unica cosa misurata.

Cio' che le traiettorie rilasciate permettono di ricostruire e' la SCOMPOSIZIONE del totale:
  - i token del PRIMO turno, dove non c'e' ancora storia: sistema + schemi + messaggio iniziale;
  - il numero di turni, che moltiplica la storia;
  - la crescita per turno.
Un totale piu' alto perche' la traiettoria e' piu' lunga NON e' lo stesso fenomeno di un totale
piu' alto a parita' di turni.

CONTROLLO A RISPOSTA NOTA: la somma per run dei token in ingresso delle traiettorie deve
riprodurre la colonna `in_tokens` dei CSV (mediana), che il paper gia' riporta come 20.562 e
8.853. Se non coincide, la ricostruzione sta leggendo un'altra cosa.

    python3 analysis/contesto_t6.py
"""
import csv, glob, json, os, statistics as st, sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CELLE = [("Databricks", "c2r_llama-3.3-70b_databricks_native"),
         ("Bedrock", "c2r_llama-3.3-70b_bedrock_native")]
ATTESO_CSV = {"Databricks": 20562, "Bedrock": 8853}   # mediane gia' nel paper


def per_run(cella):
    fuori = []
    base = os.path.join(RADICE, "results", "trajectories")
    for d in sorted(glob.glob(os.path.join(base, cella + "*"))):
        for p in sorted(glob.glob(os.path.join(d, "*.jsonl"))):
            righe = [json.loads(l) for l in open(p) if l.strip()]
            inp = [r.get("usage", {}).get("input_tokens", 0) for r in righe]
            if not inp:
                continue
            fuori.append({"turni": len(righe), "primo": inp[0], "totale": sum(inp),
                          "ultimo": inp[-1]})
    return fuori


def mediana_csv(cella):
    v = []
    for f in glob.glob(os.path.join(RADICE, "results", "riraccolta", cella + "*.csv")):
        for r in csv.DictReader(open(f, errors="ignore")):
            if r.get("infra_failure") == "False" and r.get("in_tokens"):
                v.append(int(r["in_tokens"]))
    return st.median(v) if v else None


def main():
    stat = {}
    for nome, cella in CELLE:
        d = per_run(cella)
        stat[nome] = {
            "N": len(d),
            "turni": st.median(x["turni"] for x in d),
            "primo_turno": st.median(x["primo"] for x in d),
            "totale": st.median(x["totale"] for x in d),
            "per_turno": st.median(x["totale"] / x["turni"] for x in d),
        }
    print("  Scomposizione dei token in ingresso DICHIARATI DAL PROVIDER, per run (mediane)\n")
    print("  %-28s %14s %14s %8s" % ("quantita'", "Databricks", "Bedrock", "rapporto"))
    for k, et in [("N", "run"), ("turni", "turni usati"),
                  ("primo_turno", "token al 1o turno"),
                  ("per_turno", "token per turno"), ("totale", "token in ingresso, totale")]:
        a, b = stat["Databricks"][k], stat["Bedrock"][k]
        rap = ("%8.2f" % (b / a)) if a else "       -"
        print("  %-28s %14.1f %14.1f %s" % (et, a, b, rap))

    print("\n  CONTROLLO a risposta nota — la ricostruzione deve dare la mediana dei CSV")
    ok = True
    for nome, cella in CELLE:
        m = mediana_csv(cella)
        atteso = ATTESO_CSV[nome]
        buono = m is not None and abs(m - atteso) <= 1
        ok &= buono
        print("    %-12s CSV %8s   atteso %8d   %s" % (nome, m, atteso, "ok" if buono else "FALLITO"))
        ric = stat[nome]["totale"]
        vicino = abs(ric - atteso) / atteso < 0.02
        ok &= vicino
        print("    %-12s traiettorie %8.0f   entro il 2%% del CSV: %s"
              % (nome, ric, "ok" if vicino else "FALLITO"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
