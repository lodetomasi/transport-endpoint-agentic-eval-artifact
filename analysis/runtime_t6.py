#!/usr/bin/env python3
"""R11 — indizi di runtime diverso dietro T6, il contrasto fra i due cloud a modello fisso.

PERCHE'. T6 misura 7,94pp fra due piattaforme che servono lo stesso identificatore di modello, e il
paper dichiara di non poter verificare che i pesi siano identici byte per byte. La dichiarazione e'
onesta e sterile: non porta nessuna evidenza sulla direzione in cui i due runtime differirebbero.

I dati grezzi contengono quattro quantita' che un serving stack determina e un modello no: la
latenza per run, i token emessi, il throughput, e la lunghezza del candidato prodotto. Se le due
piattaforme servissero configurazioni identiche, queste quattro concorderebbero a meno del rumore
di rete. Se divergono in modo sistematico, non sappiamo ancora \\emph{cosa} differisce --- potrebbe
essere quantizzazione, versione del runtime, batching lato server, un limite di output diverso ---
ma sappiamo che qualcosa differisce, e il confondimento passa da dichiarato a documentato.

QUESTO NON CHIUDE IL CONFONDIMENTO. Nessuna di queste quantita' identifica la causa, e un throughput
diverso e' compatibile con pesi identici su hardware diverso. Lo scopo e' spostare l'affermazione da
«non possiamo verificare» a «ecco in che misura i due si comportano diversamente, e il lettore
giudichi se e' compatibile con l'identita' che l'identificatore promette».

    python3 analysis/runtime_t6.py
    python3 analysis/runtime_t6.py --tutti     # tutti e quattro i modelli, non solo llama
"""
import csv
import glob
import os
import statistics as st
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, os.path.join(RADICE, "src"))
from qualita_run import e_misurazione  # noqa: E402

RADICE_DATI = os.environ.get("C2_RESULTS", "results/riraccolta")
PATTERN = os.environ.get("C2_PATTERN", "c2r_*.csv")


def righe(modello, infra, trasporto="native"):
    fuori = []
    for f in sorted(glob.glob(os.path.join(RADICE, RADICE_DATI, PATTERN))):
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                if (r.get("modello"), r.get("infra"), r.get("trasporto")) != (modello, infra, trasporto):
                    continue
                if not e_misurazione(r):
                    continue
                try:
                    fuori.append({
                        "elapsed": float(r["elapsed_s"]),
                        "out": int(r["out_tokens"]),
                        "inp": int(r["in_tokens"]),
                        "chars": int(r["candidate_chars"]),
                        "turni": int(r["n_turns"]),
                    })
                except (ValueError, KeyError, TypeError):
                    continue
    return fuori


def riassunto(v, chiave):
    x = sorted(d[chiave] for d in v)
    if not x:
        return None
    return {"n": len(x), "mediana": st.median(x),
            "q1": x[len(x) // 4], "q3": x[3 * len(x) // 4],
            "media": st.mean(x)}


def confronta(modello):
    a = righe(modello, "databricks")
    b = righe(modello, "bedrock")
    if not a or not b:
        return None
    print(f"\n  {modello}, trasporto nativo — {len(a)} run su databricks, {len(b)} su bedrock")
    print(f"    {'quantita':<26}{'databricks':>22}{'bedrock':>22}{'rapporto':>10}")
    fuori = {}
    for chiave, eti, fmt in (("elapsed", "latenza per run (s)", "{:.1f}"),
                             ("out", "token emessi", "{:.0f}"),
                             ("inp", "token in ingresso", "{:.0f}"),
                             ("chars", "caratteri del candidato", "{:.0f}"),
                             ("turni", "turni", "{:.1f}")):
        ra, rb = riassunto(a, chiave), riassunto(b, chiave)
        rap = rb["mediana"] / ra["mediana"] if ra["mediana"] else float("nan")
        fuori[chiave] = rap
        print(f"    {eti:<26}"
              f"{fmt.format(ra['mediana']) + ' [' + fmt.format(ra['q1']) + '-' + fmt.format(ra['q3']) + ']':>22}"
              f"{fmt.format(rb['mediana']) + ' [' + fmt.format(rb['q1']) + '-' + fmt.format(rb['q3']) + ']':>22}"
              f"{rap:>10.2f}")
    # throughput: token in uscita per secondo, calcolato per run e poi mediano
    tpa = st.median([d["out"] / d["elapsed"] for d in a if d["elapsed"] > 0])
    tpb = st.median([d["out"] / d["elapsed"] for d in b if d["elapsed"] > 0])
    fuori["throughput"] = tpb / tpa if tpa else float("nan")
    print(f"    {'token in uscita al secondo':<26}{tpa:>22.2f}{tpb:>22.2f}{tpb/tpa:>10.2f}")
    return fuori


if __name__ == "__main__":
    tutti = "--tutti" in sys.argv
    MODELLI = ["llama-3.3-70b"] if not tutti else \
        ["gpt-oss-120b", "llama-3.3-70b", "claude-haiku-4-5", "claude-sonnet-4-5"]

    print("  R11 — le quantita' che un serving stack determina e un modello no")
    print("  (mediana [primo-terzo quartile]; il rapporto e' bedrock/databricks)")
    esiti = {}
    for m in MODELLI:
        r = confronta(m)
        if r:
            esiti[m] = r

    t6 = esiti.get("llama-3.3-70b")
    if not t6:
        raise SystemExit("  T6 non calcolabile su questi dati (exit 2)")

    print("\n  COSA DICE SU T6")
    diverge = [(k, v) for k, v in t6.items() if abs(v - 1.0) > 0.25]
    if diverge:
        print("    Le due piattaforme divergono di oltre il 25% su:")
        for k, v in sorted(diverge, key=lambda kv: -abs(kv[1] - 1)):
            verso = "piu' alto su bedrock" if v > 1 else "piu' alto su databricks"
            print(f"      {k:<14}rapporto {v:.2f}  ({verso})")
        print("    Nessuna di queste identifica la causa, e un throughput diverso e' compatibile")
        print("    con pesi identici su hardware diverso. Ma il confondimento di T6 passa da")
        print("    dichiarato a documentato: qualcosa nei due stack differisce in modo misurabile.")
    else:
        print("    Le quattro quantita' concordano entro il 25%: su questi indizi i due stack si")
        print("    comportano in modo simile, e T6 non trova qui un'ipotesi di runtime diverso.")

    print("\n  CONTROLLO a risposta nota")
    ok = []
    a = righe("llama-3.3-70b", "databricks")
    ok.append(all(d["elapsed"] > 0 for d in a))
    print(f"    ogni run ha latenza positiva: {'ok' if ok[-1] else 'FALLITO'}")
    ok.append(all(d["out"] >= 0 for d in a))
    print(f"    nessun conteggio di token negativo: {'ok' if ok[-1] else 'FALLITO'}")
    ok.append(1 <= st.median([d["turni"] for d in a]) <= 13)
    print(f"    i turni stanno nel budget dichiarato (1-13): {'ok' if ok[-1] else 'FALLITO'}")
    if not all(ok):
        raise SystemExit("  i dati di runtime non rispettano le loro proprieta' (exit 2)")
