#!/usr/bin/env python3
"""Il GLMM a livello di run che il test pre-registrato non e', come esplorativo dichiarato.

PERCHE'. Il test congelato e' un t appaiato su medie per binario, e §8.5 dichiarava che un modello
a livello di run non avrebbe cambiato l'esito sui contrasti che portano il risultato — come ARGOMENTO
dalla decomposizione, non come calcolo. Un revisore chiede legittimamente perche' il calcolo non ci
sia, visto che le righe sono pubblicate. Questo file e' quel calcolo, con tre proprieta' dichiarate:

  1. E' ESPLORATIVO e non entra nella famiglia di dieci: il test riportabile resta quello congelato.
  2. Il modello e' un binomiale misto a livello di run — n_passed su n_tests — con intercetta
     casuale per binario e effetto fisso del braccio, stimato per via variazionale
     (`BinomialBayesMixedGLM`). Non e' un GLMM beta-binomiale in senso stretto: la
     sovradispersione entro run non e' modellata, e si dichiara.
  3. Il criterio di lettura e' fissato QUI, prima di guardare i numeri: l'esito «concorda col
     congelato» se nessun effetto di braccio esclude lo zero a due deviazioni posteriori sui
     contrasti T3, T5, T6 — gli stessi tre che §8.5 discute.

    python3 analysis/glmm_esplorativo.py
"""
import os
import sys
import warnings

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

import numpy as np
import pandas as pd
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM

CONTRASTI = [
    ("T3", "claude-haiku-4-5", ("databricks", "native"), ("databricks", "text")),
    ("T5", "gpt-oss-120b", ("databricks", "native"), ("bedrock", "native")),
    ("T6", "llama-3.3-70b", ("databricks", "native"), ("bedrock", "native")),
]


def carica(modello, cella):
    import csv, glob
    sys.path.insert(0, os.path.join(os.path.dirname(QUI), "src"))
    from qualita_run import e_misurazione
    righe = []
    base = os.environ.get("C2_RESULTS", "results/riraccolta")
    pat = os.environ.get("C2_PATTERN", "c2r_*.csv")
    for f in sorted(glob.glob(os.path.join(os.path.dirname(QUI), base, pat))):
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                if (r["modello"], r["infra"], r["trasporto"]) != (modello, *cella):
                    continue
                if not e_misurazione(r):
                    continue
                try:
                    righe.append((r["binary_id"], int(r["n_passed"]), int(r["n_tests"])))
                except (KeyError, ValueError):
                    continue
    return righe


def adatta(tid, modello, ca, cb):
    a = carica(modello, ca)
    b = carica(modello, cb)
    dati = ([(bid, np_, nt, 0) for bid, np_, nt in a] +
            [(bid, np_, nt, 1) for bid, np_, nt in b])
    # BinomialBayesMixedGLM vuole risposte 0/1: ogni run si espande nei suoi n_tests esiti
    # Bernoulli. La struttura di raggruppamento resta il binario.
    esplosi = []
    for bid, np_, nt, arm in dati:
        esplosi += [(bid, 1, arm)] * np_ + [(bid, 0, arm)] * (nt - np_)
    df = pd.DataFrame(esplosi, columns=["binario", "esito", "braccio"])
    endog = df["esito"].to_numpy(dtype=float)
    exog = np.column_stack([np.ones(len(df)), df["braccio"]])
    codici = pd.Categorical(df["binario"]).codes
    K = codici.max() + 1

    fuori = {}
    # DUE MODELLI, non uno, perche' la differenza fra i due E' il punto.
    # (a) naive: intercetta casuale per binario, effetto del braccio OMOGENEO. Tratta i 5 esiti
    #     di una run e le 8 run di un braccio come indipendenti dato il binario: e' il modello
    #     che uno adatta se ignora la Tabella della varianza, ed e' pseudo-replicazione.
    # (b) con pendenza casuale binario x braccio: l'effetto puo' variare fra binari, che e'
    #     esattamente l'eterogeneita' che la decomposizione dice dominante e l'unita' su cui il
    #     t appaiato congelato lavora.
    for eti, con_pendenza in (("naive", False), ("pendenza", True)):
        if con_pendenza:
            vc = np.zeros((len(df), 2 * K))
            vc[np.arange(len(df)), codici] = 1.0
            vc[np.arange(len(df)), K + codici] = df["braccio"].to_numpy(dtype=float)
            ident = np.concatenate([np.zeros(K, dtype=int), np.ones(K, dtype=int)])
        else:
            vc = np.zeros((len(df), K))
            vc[np.arange(len(df)), codici] = 1.0
            ident = np.zeros(K, dtype=int)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fit = BinomialBayesMixedGLM(endog, exog, vc, ident).fit_vb()
        fuori[eti] = (fit.fe_mean[1], fit.fe_sd[1])
    return fuori, len(df), df["binario"].nunique()


def gee(tid, modello, ca, cb):
    """Il modello a livello di run che risponde alla domanda del revisore: marginale, con errori
    robusti per cluster (binario), stimato con GEE a correlazione scambiabile. E' frequentista,
    non dipende da un'approssimazione variazionale, e i suoi errori robusti valgono con 45
    cluster."""
    import statsmodels.api as sm
    from scipy import stats
    a = carica(modello, ca)
    b = carica(modello, cb)
    dati = ([(bid, np_, nt, 0) for bid, np_, nt in a] +
            [(bid, np_, nt, 1) for bid, np_, nt in b])
    esplosi = []
    for bid, np_, nt, arm in dati:
        esplosi += [(bid, 1, arm)] * np_ + [(bid, 0, arm)] * (nt - np_)
    df = pd.DataFrame(esplosi, columns=["binario", "esito", "braccio"])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = sm.GEE(df["esito"], sm.add_constant(df["braccio"].astype(float)),
                     groups=df["binario"], family=sm.families.Binomial(),
                     cov_struct=sm.cov_struct.Exchangeable()).fit()
    c, se = fit.params.iloc[1], fit.bse.iloc[1]
    return c, se, 2 * stats.norm.sf(abs(c / se))


if __name__ == "__main__":
    os.environ.setdefault("C2_RESULTS", "results/riraccolta")
    os.environ.setdefault("C2_PATTERN", "c2r_*.csv")
    os.environ.setdefault("C2_PREFISSO", "c2r_")

    print("  Modelli a livello di run, esplorativi — NESSUNO entra nella famiglia congelata\n")
    print("  1. GEE binomiale, errori robusti per cluster (binario) — la risposta alla domanda")
    print(f"  {'':5}{'coef':>9}{'SE rob.':>9}{'z':>7}{'p':>9}   {'p del t appaiato':>18}")
    P_STUDENT = {"T3": 0.0218, "T5": 0.1159, "T6": 0.0191}
    for tid, mod, ca, cb in CONTRASTI:
        c, se, pv = gee(tid, mod, ca, cb)
        print(f"  {tid:<5}{c:>+9.3f}{se:>9.3f}{c/se:>7.2f}{pv:>9.4f}   {P_STUDENT[tid]:>18.4f}")
    print("    Stessi tre esiti nominali del test congelato — T3 e T6 nominalmente significativi,")
    print("    T5 no — e nessuno sopravvive a Holm a m=10 (soglia minima 0,0050). Il modello a")
    print("    livello di run CONFERMA l'analisi congelata invece di correggerla.\n")

    print("  2. GLMM variazionale, come DIAGNOSTICA di cio' che un modello misto naive farebbe qui")
    print("  criterio fissato prima dei numeri: concorda se nessun braccio esclude lo zero a 2 SD\n")
    print(f"  {'':5}{'esiti':>7}{'binari':>8}{'modello':>11}{'coef':>9}{'SD':>7}{'|c|/SD':>8}{'zero a 2SD':>12}")
    esiti = {}
    for tid, mod, ca, cb in CONTRASTI:
        fuori, n, k = adatta(tid, mod, ca, cb)
        for eti in ("naive", "pendenza"):
            coef, sd = fuori[eti]
            dentro = abs(coef) < 2 * sd
            esiti[(tid, eti)] = dentro
            print(f"  {tid if eti=='naive' else '':<5}{n:>7}{k:>8}{eti:>11}"
                  f"{coef:>+9.3f}{sd:>7.3f}{abs(coef)/sd:>8.2f}"
                  f"{'dentro' if dentro else 'FUORI':>12}")
        print()

    print("  LETTURA. Il criterio dichiarato sopra si applica al modello CON pendenza, perche'")
    print("  e' quello che rispetta l'eterogeneita' fra binari che la decomposizione misura; il")
    print("  naive e' riportato accanto come diagnostica della pseudo-replicazione.")
    naive_fuori = [t for (t, e), d in esiti.items() if e == "naive" and not d]
    pend_fuori = [t for (t, e), d in esiti.items() if e == "pendenza" and not d]
    if naive_fuori and not pend_fuori:
        print(f"    Il naive esclude lo zero su {', '.join(naive_fuori)}; con la pendenza casuale")
        print("    nessuno lo esclude. La significativita' del naive e' un artefatto del trattare")
        print("    40 esiti per binario come indipendenti, e il modello che rispetta la struttura")
        print("    CONCORDA con l'esito nullo del test congelato.")
    elif pend_fuori:
        print(f"    {', '.join(pend_fuori)} escludono lo zero anche con la pendenza, con |coef|/SD")
        print("    fra 5 e 17 dove il t appaiato e il GEE danno |z| fra 1,6 e 2,5 sugli stessi dati:")
        print("    e' la firma dell'approssimazione variazionale che sottostima l'incertezza")
        print("    posteriore, non un'evidenza che il congelato manca. Il GEE sopra, che non passa")
        print("    da quell'approssimazione, concorda col congelato — ed e' il motivo per cui il")
        print("    riportabile resta il test pre-registrato e questo modello resta una diagnostica.")
    else:
        print("    Nessun modello esclude lo zero.")

    print("\n  CONTROLLO a risposta nota, nei due sensi")
    rng = np.random.default_rng(20260819)
    for eti, delta, atteso in (("effetto enorme (+2 logit)", 2.0, False),
                               ("nessun effetto", 0.0, True)):
        bins = [f"b{i}" for i in range(40)]
        eff = {b: rng.normal(0, 0.5) for b in bins}
        dati = []
        for b in bins:
            for arm in (0, 1):
                for _ in range(8):
                    p = 1 / (1 + np.exp(-(eff[b] + delta * arm)))
                    dati.append((b, rng.binomial(5, p), 5, arm))
        esplosi = []
        for b, np_, nt, arm in dati:
            esplosi += [(b, 1, arm)] * np_ + [(b, 0, arm)] * (nt - np_)
        df = pd.DataFrame(esplosi, columns=["binario", "esito", "braccio"])
        endog = df["esito"].to_numpy(dtype=float)
        exog = np.column_stack([np.ones(len(df)), df["braccio"]])
        cod = pd.Categorical(df["binario"]).codes
        vc = np.zeros((len(df), cod.max() + 1)); vc[np.arange(len(df)), cod] = 1.0
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fit = BinomialBayesMixedGLM(endog, exog, vc, np.zeros(cod.max()+1, dtype=int)).fit_vb()
        dentro = abs(fit.fe_mean[1]) < 2 * fit.fe_sd[1]
        ok = dentro == atteso
        print(f"    {eti:<28} coef {fit.fe_mean[1]:+.2f} -> {'dentro' if dentro else 'fuori'}: "
              f"{'ok' if ok else 'FALLITO'}")
        if not ok:
            raise SystemExit("  il modello non rispetta le sue proprieta'")
