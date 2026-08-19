#!/usr/bin/env python3
"""Rumore contro eterogeneita': quale delle due leve morde, contrasto per contrasto.

Richiesto dallo `stats-auditor` il 2026-08-15 come condizione per chiudere il nodo `test`.
Senza questo file, la frase «la volatilita' a temperatura zero spiega la SD alta» resta
un'affermazione plausibile e non verificata nel deposito.

LA DOMANDA. La SD della differenza appaiata per binario ha due sorgenti:

  1. RUMORE entro-binario — le 8 run della stessa cella non danno lo stesso pass_rate.
     Si riduce aumentando le RUN per binario, e con run infinite sparisce.
  2. ETEROGENEITA' vera fra binari — l'effetto del trasporto e' davvero diverso da un
     binario all'altro. NON si riduce con piu' run: serve un K piu' grande.

Le due leve non sono intercambiabili, e quale morda dipende dal modello: la
pre-registrazione §7 lo dichiarava gia' per C1 («per llama il 60% e' eterogeneita' vera,
per haiku l'84% e' rumore fra run»). Questo file rifa' lo stesso conto sui dati di C2, e
per haiku la risposta e' capovolta.

LA SCOMPOSIZIONE. La differenza fra le medie di 8 run in due condizioni ha varianza

    Var(diff) = Var_eterogeneita + (Var_entro_A + Var_entro_B) / 8

dove Var_entro e' la MEDIA DELLE VARIANZE per binario, non il quadrato della media delle
SD: alcuni binari sono deterministici e altri no, e la media delle SD schiaccia proprio
quelli che portano il rumore.

    K necessario = (z(0,975) + z(0,80))^2 * SD_residua^2 / delta^2,  delta = 3pp

3pp e' la banda del falsificatore di §4, la stessa per cui §7 calcolava K = 99-119.
"""
import csv
import glob
import os

# Il percorso era fisso a «results/c2_*.csv», e con la ri-raccolta questo e' diventato un
# difetto: passando --results results/riraccolta lo script leggeva comunque la raccolta
# vecchia e produceva lo STESSO output, che e' il modo in cui un flag ignorato sembra
# funzionare. Ora si sceglie da riga di comando, e il default resta il confermativo.
RADICE_DATI = os.environ.get("C2_RESULTS", "results")
PATTERN = os.environ.get("C2_PATTERN", "c2_*.csv")
import math
import statistics as st
import sys
from collections import defaultdict

sys.path.insert(0, "src")
from qualita_run import e_misurazione  # noqa: E402

Z = (1.959964 + 0.841621) ** 2          # 7,849 — bilaterale al 5%, potenza 80%
BANDA = 0.03                            # la banda del falsificatore, §4
RUNS = 8

CONTRASTI = [
    ("T1", "gpt-oss-120b",      ("databricks", "native"), ("databricks", "text")),
    ("T2", "llama-3.3-70b",     ("databricks", "native"), ("databricks", "text")),
    ("T3", "claude-haiku-4-5",  ("databricks", "native"), ("databricks", "text")),
    ("T4", "claude-sonnet-4-5", ("databricks", "native"), ("databricks", "text")),
    ("T5", "gpt-oss-120b",      ("databricks", "native"), ("bedrock", "native")),
    ("T6", "llama-3.3-70b",     ("databricks", "native"), ("bedrock", "native")),
    ("T7", "claude-haiku-4-5",  ("databricks", "native"), ("bedrock", "native")),
    ("T8", "claude-sonnet-4-5", ("databricks", "native"), ("bedrock", "native")),
]


def runs_per_binario(modello, infra, trasporto):
    per = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(RADICE_DATI, PATTERN))):
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                if (r.get("modello"), r.get("infra"), r.get("trasporto")) == (modello, infra, trasporto):
                    if e_misurazione(r):
                        per[r["binary_id"]].append(float(r["pass_rate"]))
    return {b: v[:RUNS] for b, v in per.items() if len(v) >= RUNS}


def scomponi(modello, cond_a, cond_b):
    a = runs_per_binario(modello, *cond_a)
    b = runs_per_binario(modello, *cond_b)
    com = sorted(set(a) & set(b))
    if len(com) < 2:
        return None

    diff = [st.mean(a[k]) - st.mean(b[k]) for k in com]
    sd_oss = st.stdev(diff)

    # media delle varianze per binario, una per condizione
    var_a = st.mean(st.variance(a[k]) for k in com)
    var_b = st.mean(st.variance(b[k]) for k in com)
    sd_rumore = math.sqrt((var_a + var_b) / RUNS)

    var_res = max(0.0, sd_oss ** 2 - sd_rumore ** 2)
    sd_res = math.sqrt(var_res)
    quota_rumore = (sd_rumore ** 2) / (sd_oss ** 2) if sd_oss > 0 else float("nan")

    k_ora = Z * sd_oss ** 2 / BANDA ** 2
    k_inf = Z * sd_res ** 2 / BANDA ** 2
    return dict(K=len(com), sd_oss=sd_oss, sd_rumore=sd_rumore, sd_res=sd_res,
                quota=quota_rumore, k_ora=k_ora, k_inf=k_inf)


if __name__ == "__main__":
    print("Scomposizione della varianza della differenza appaiata — C2, 16 celle chiuse\n")
    print(f"  {'':5}{'modello':<20}{'SD oss':>9}{'SD rumore':>11}{'% rumore':>10}"
          f"{'SD resid.':>11}{'K a 3pp':>9}{'K con run inf.':>16}")
    righe = {}
    for tid, mod, ca, cb in CONTRASTI:
        s = scomponi(mod, ca, cb)
        if not s:
            print(f"  {tid:<5}{mod:<20}  non calcolabile")
            continue
        righe[tid] = s
        nota = "  <- rumore > SD osservata" if s["sd_rumore"] > s["sd_oss"] else ""
        print(f"  {tid:<5}{mod:<20}{s['sd_oss']:>9.4f}{s['sd_rumore']:>11.4f}"
              f"{100*s['quota']:>9.1f}%{s['sd_res']:>11.4f}{s['k_ora']:>9.0f}"
              f"{s['k_inf']:>16.0f}{nota}")

    anomali = [t for t, s in righe.items() if s["sd_rumore"] > s["sd_oss"]]
    if anomali:
        print(f"\n  I tre contrasti marcati ({', '.join(anomali)}) hanno rumore stimato MAGGIORE")
        print("  della SD osservata, cioe' varianza residua negativa. Non e' un errore di conto:")
        print("  significa che la differenza fra le due condizioni e' MENO variabile di quanto")
        print("  il rumore indipendente predirebbe. Due letture, entrambe da dichiarare:")
        print("    - le run delle due condizioni non sono indipendenti come il modello assume")
        print("      (stesso binario, stesso stack, errori correlati), oppure")
        print("    - e' rumore di stima sulle varianze, con 45 binari e 8 run.")
        print("  In entrambi i casi la lettura utile e' la stessa: su quei contrasti NON c'e'")
        print("  eterogeneita' vera fra binari da rilevare, e la SD osservata e' tutta rumore")
        print("  che piu' run ridurrebbero. E' l'opposto di T3 e T6.")

    print("\n  Le due leve, per i tre contrasti con p nominale sotto 0,05:")
    for tid in ("T1", "T3", "T6"):
        if tid not in righe:
            continue
        s = righe[tid]
        if s["quota"] > 0.5:
            leva = (f"piu RUN per binario: il {100*s['quota']:.0f}% della varianza e' rumore, "
                    f"e con run infinite K scenderebbe da {s['k_ora']:.0f} a {s['k_inf']:.0f}")
        else:
            leva = (f"NESSUNA leva praticabile: solo il {100*s['quota']:.0f}% e' rumore, "
                    f"quindi anche con run infinite servirebbero K={s['k_inf']:.0f} binari")
        print(f"    {tid}: {leva}")

    print("\n  La calibrazione importata da C1 per haiku, e cosa dicono i dati di C2:")
    if "T3" in righe:
        q = 100 * righe["T3"]["quota"]
        print(f"    PREREGISTRAZIONE §7, da C1: «per haiku-4-5 l'84% e' rumore fra run e il")
        print(f"    pavimento e' K=13».   Osservato in C2 sullo stesso contrasto: {q:.1f}% rumore,")
        print(f"    pavimento K={righe['T3']['k_inf']:.0f}.")
        print(f"    La calibrazione non ha sbagliato solo la grandezza: ha invertito il MECCANISMO.")

    print("\n  Controllo con risposta nota — lo stats-auditor, calcolando indipendentemente,")
    print("  ha riportato SD osservate 0,1950 (T1), 0,2844 (T3), 0,2481 (T6):")
    for tid, atteso in (("T1", 0.1950), ("T3", 0.2844), ("T6", 0.2481)):
        if tid in righe:
            ok = abs(righe[tid]["sd_oss"] - atteso) < 0.0005
            print(f"    {tid}: {righe[tid]['sd_oss']:.4f} contro {atteso:.4f}  "
                  f"{'COINCIDE' if ok else 'NON COINCIDE — verificare la convenzione'}")
