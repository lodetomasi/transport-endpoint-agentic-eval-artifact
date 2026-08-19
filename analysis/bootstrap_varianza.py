#!/usr/bin/env python3
"""R1 — intervalli bootstrap sulla quota di rumore e su K_infinito, per tutti e otto i contrasti.

PERCHE'. La decomposizione della varianza (Tabella V) e l'inversione della calibrazione sono il
secondo contributo del paper, e finora erano riportate come stime puntuali: «0,5% di rumore,
K_inf=668». Una stima puntuale su 45 binari non dice se quello 0,5% e' distinguibile dal 50%, e
finche' non lo dice il contributo non e' verificabile. Un revisore ha posto la condizione nella
forma piu' utile possibile: **se l'intervallo di T3 copre il 50%, il contributo esce
dall'abstract.**

L'UNITA' DI RICAMPIONAMENTO E' IL BINARIO, non la run. I contrasti sono appaiati sul binario e K=45
e' il numero di binari: ricampionare le run stimerebbe l'incertezza della media entro binario, che
non e' la quantita' in questione. Ricampionando i binari con rimpiazzo si propaga esattamente
l'incertezza che 45 unita' portano.

DUE PROPRIETA' DEL STIMATORE CHE L'INTERVALLO EREDITA, e vanno lette insieme ai numeri:

1. `var_res = max(0, sd_oss^2 - sd_rumore^2)` e' **censurato a zero**. Quando il rumore stimato
   eccede la varianza osservata, la varianza residua non diventa negativa: diventa zero. Sui
   contrasti dove questo succede spesso, la distribuzione bootstrap di K_inf si accumula su zero e
   il quantile inferiore e' zero per costruzione, non per evidenza. Lo script riporta **quante
   replicazioni sono state censurate**, perche' senza quel numero l'intervallo si legge male.
2. La quota di rumore e' un rapporto fra due quantita' stimate dallo stesso campione, quindi non
   e' ne' normale ne' simmetrica. Si riportano i **percentili** (2,5 e 97,5), non media +/- 2SD.

    python3 analysis/bootstrap_varianza.py                    # la base primaria
    python3 analysis/bootstrap_varianza.py --confermativa     # la raccolta originale
    python3 analysis/bootstrap_varianza.py --B 10000          # piu' replicazioni

Il seme e' fisso e dichiarato: due esecuzioni danno lo stesso intervallo, che e' il minimo per un
numero che entra in un paper.
"""
import math
import os
import random
import statistics as st
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

SEME = 20260819          # la data, per non scegliere un seme che conviene
B_DEFAULT = 5000
BANDA = 0.03             # la banda del falsificatore, §IV
Z = (1.959964 + 0.841621) ** 2
RUNS = 8


def decomponi(a, b, binari):
    """La decomposizione su un dato insieme di binari. Stessa formula del file congelato:
    non si cambia l'estimatore per il bootstrap, altrimenti l'intervallo non appartiene alla
    stima che il paper riporta."""
    diff = [st.mean(a[k]) - st.mean(b[k]) for k in binari]
    if len(diff) < 2:
        return None
    sd_oss = st.stdev(diff)
    if sd_oss <= 0:
        return None
    var_a = st.mean([st.variance(a[k]) for k in binari])
    var_b = st.mean([st.variance(b[k]) for k in binari])
    sd_rumore = math.sqrt((var_a + var_b) / RUNS)
    var_res_grezza = sd_oss ** 2 - sd_rumore ** 2
    var_res = max(0.0, var_res_grezza)
    return {
        "quota": (sd_rumore ** 2) / (sd_oss ** 2),
        "k_inf": Z * var_res / BANDA ** 2,
        "censurata": var_res_grezza < 0,
    }


def bootstrap(a, b, binari, B):
    rng = random.Random(SEME)
    quote, kinf, censurate, scartate = [], [], 0, 0
    n = len(binari)
    for _ in range(B):
        camp = [binari[rng.randrange(n)] for _ in range(n)]
        r = decomponi(a, b, camp)
        if r is None:
            scartate += 1
            continue
        quote.append(r["quota"])
        kinf.append(r["k_inf"])
        censurate += r["censurata"]
    return quote, kinf, censurate, scartate


def pct(v, p):
    if not v:
        return float("nan")
    s = sorted(v)
    i = max(0, min(len(s) - 1, int(round(p / 100 * (len(s) - 1)))))
    return s[i]


if __name__ == "__main__":
    conf = "--confermativa" in sys.argv
    B = B_DEFAULT
    if "--B" in sys.argv:
        B = int(sys.argv[sys.argv.index("--B") + 1])

    os.environ["C2_RESULTS"] = "results" if conf else "results/riraccolta"
    os.environ["C2_PATTERN"] = "c2_*.csv" if conf else "c2r_*.csv"
    import scomposizione_varianza as sv

    print(f"  bootstrap sui binari, B={B}, seme={SEME}, "
          f"raccolta {'confermativa' if conf else 'primaria (ri-raccolta)'}\n")
    print(f"  {'':5}{'quota rumore':>14}{'IC95 quota':>22}{'K_inf':>9}"
          f"{'IC95 K_inf':>18}{'cens.':>8}")

    esiti = {}
    for tid, mod, ca, cb in sv.CONTRASTI:
        a = sv.runs_per_binario(mod, *ca)
        b = sv.runs_per_binario(mod, *cb)
        com = sorted(set(a) & set(b))
        if len(com) < 2:
            print(f"  {tid:<5}{'non calcolabile':>14}")
            continue
        punto = decomponi(a, b, com)
        quote, kinf, cens, scart = bootstrap(a, b, com, B)
        lo_q, hi_q = pct(quote, 2.5), pct(quote, 97.5)
        lo_k, hi_k = pct(kinf, 2.5), pct(kinf, 97.5)
        esiti[tid] = dict(quota=punto["quota"], lo_q=lo_q, hi_q=hi_q,
                          k=punto["k_inf"], lo_k=lo_k, hi_k=hi_k, cens=cens, B=len(quote))
        print(f"  {tid:<5}{100*punto['quota']:>13.1f}%"
              f"{f'[{100*lo_q:.1f}, {100*hi_q:.1f}]':>22}"
              f"{punto['k_inf']:>9.0f}{f'[{lo_k:.0f}, {hi_k:.0f}]':>18}"
              f"{100*cens/max(1,len(quote)):>7.0f}%")

    # --- il criterio che il revisore ha posto ------------------------------------------
    print("\n  IL CRITERIO DI R1, e la sua risposta")
    t3 = esiti.get("T3")
    if not t3:
        raise SystemExit("  T3 non calcolabile: il criterio non si puo' applicare (exit 2)")
    copre = t3["lo_q"] <= 0.50 <= t3["hi_q"]
    print(f"    l'IC95 della quota di rumore di T3 e' "
          f"[{100*t3['lo_q']:.1f}%, {100*t3['hi_q']:.1f}%]")
    print(f"    copre il 50%: {'SI' if copre else 'NO'}")
    if copre:
        print("    -> il contributo #2 ESCE dall'abstract: a 45 binari la quota di rumore di T3")
        print("       non e' distinguibile dalla meta', e l'inversione della calibrazione non")
        print("       poggia su una stima risolta.")
    else:
        print("    -> il contributo #2 RESTA: la quota di rumore di T3 e' distinguibile dal 50%")
        print("       a 45 binari, e l'inversione poggia su una stima con intervallo dichiarato.")

    # --- il controllo a risposta nota --------------------------------------------------
    print("\n  CONTROLLO a risposta nota, nei due sensi")
    ok = []
    for tid in ("T3", "T6"):
        e = esiti.get(tid)
        if e:
            dentro = e["lo_q"] <= e["quota"] <= e["hi_q"]
            ok.append(dentro)
            print(f"    la stima puntuale di {tid} cade nel proprio IC95: "
                  f"{'ok' if dentro else 'FALLITO'}")
    alte = [t for t, e in esiti.items() if e["quota"] >= 1.0]
    if alte:
        tutte_cens = all(esiti[t]["cens"] > 0.5 * esiti[t]["B"] for t in alte)
        ok.append(tutte_cens)
        print(f"    i contrasti a quota >=100% ({', '.join(alte)}) hanno la maggioranza delle "
              f"replicazioni censurate: {'ok' if tutte_cens else 'FALLITO'}")
        print("      (e' la firma del clamp a zero, non evidenza di varianza residua nulla)")
    if not all(ok):
        raise SystemExit("  il bootstrap non rispetta le sue proprieta' strutturali (exit 2)")
    print("\n  Il numero fra parentesi in coda a ogni riga e' la quota di replicazioni in cui la")
    print("  varianza residua e' stata censurata a zero. Dove e' alta, il quantile inferiore di")
    print("  K_inf e' zero per costruzione dello stimatore e non per evidenza nei dati.")
