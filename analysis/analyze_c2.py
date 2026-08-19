#!/usr/bin/env python3
"""Analisi confermativa di C2 — SCRITTA E CONGELATA PRIMA CHE I DATI ESISTANO.

Questo file esiste prima della prima riga di dati. E' la meta' che C1 aveva lasciato aperta:
congelare le ipotesi e scrivere l'analisi a dati visti lascia intatta tutta la liberta' che la
pre-registrazione doveva chiudere -- quale test, su quale sottoinsieme, con quale esclusione.

Famiglia di dieci test, ordinata e non modificabile, in PREREGISTRAZIONE.md §7. m resta 10
anche se un braccio non e' eseguibile: togliere un test a dati visti abbassa le soglie di Holm
dei sopravvissuti.

    python3 analysis/analyze_c2.py --results results/
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

MODELLI = ["gpt-oss-120b", "llama-3.3-70b", "claude-haiku-4-5", "claude-sonnet-4-5"]
INFRA = ["databricks", "bedrock"]
TRASPORTI = ["native", "text"]
RUN_ATTESI = 8
BANDA = 0.03  # +/-3pp, la banda del falsificatore

# La famiglia, verbatim dalla pre-registrazione. L'ordine qui e' l'enumerazione, NON
# l'ordinamento di Holm: quello lo determinano i p-value.
FAMIGLIA = (
    [("T%d" % (i + 1), "trasporto", m, "databricks") for i, m in enumerate(MODELLI)]
    + [("T%d" % (i + 5), "infrastruttura", m, "native") for i, m in enumerate(MODELLI)]
    + [("T9", "eterogeneita", None, None), ("T10", "interazione", None, None)]
)
M_FAMIGLIA = 10
# Fuori dalla f-string: una barra rovesciata dentro l'espressione e' un errore di sintassi,
# e l'apostrofo va nell'etichetta, non nel formato.
ETICHETTA_ESATTO = "^ test esatto sulle stesse quantita'"


def carica(cartella):
    """Ogni riga porta modello, infrastruttura, trasporto, binario. Una riga e' una
    misurazione se e solo se la regola condivisa la accetta -- la stessa che usa la
    raccolta, perche' due definizioni divergono e la divergenza non fa rumore."""
    celle = collections.defaultdict(list)
    non_eseguibili = {}
    for f in sorted(glob.glob(os.path.join(cartella, "*.csv"))):
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                chiave = (r.get("modello") or r.get("model_label", ""),
                          r.get("infra", ""), r.get("trasporto", ""))
                if r.get("non_eseguibile") == "True":
                    non_eseguibili[chiave] = r.get("error", "")[:200]
                    continue
                if e_misurazione(r):
                    celle[chiave + (r["binary_id"],)].append(float(r["pass_rate"]))
    return celle, non_eseguibili


def media_per_binario(celle, modello, infra, trasporto):
    out = {}
    for (m, i, t, b), v in celle.items():
        if (m, i, t) == (modello, infra, trasporto) and v:
            out[b] = st.mean(v[:RUN_ATTESI])
    return out


def t_appaiato(a, b):
    """Ritorna (n, media_diff, ic_basso, ic_alto, t, p). Nessuna dipendenza esterna: scipy
    non e' garantito nell'ambiente di raccolta, e un'analisi che non gira dove girano i dati
    e' un'analisi che qualcuno rifara' a mano."""
    com = sorted(set(a) & set(b))
    d = [b[k] - a[k] for k in com]
    n = len(d)
    if n < 2:
        return n, float("nan"), float("nan"), float("nan"), float("nan"), float("nan")
    med, sd = st.mean(d), st.stdev(d)
    se = sd / math.sqrt(n)
    t = med / se if se > 0 else float("inf")
    # t critico al 95% per n-1 gradi, approssimazione di Hill sufficiente a K>=30
    tc = 1.959964 + 2.3737 / (n - 1) + 2.8 / (n - 1) ** 2
    p = 2 * (1 - _norm_cdf(abs(t) / (1 + 1.0 / (4 * (n - 1)))))
    return n, med, med - tc * se, med + tc * se, t, p


def _norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def holm(risultati):
    """Holm step-down su m=10 FISSO. I test non calcolabili non escono dalla famiglia:
    restano, non si testano, e non abbassano la soglia di nessun altro."""
    calcolabili = [r for r in risultati if not math.isnan(r["p"])]
    calcolabili.sort(key=lambda r: r["p"])
    for rango, r in enumerate(calcolabili, start=1):
        r["rango"] = rango
        r["soglia"] = 0.05 / (M_FAMIGLIA - rango + 1)
        r["passa"] = r["p"] <= r["soglia"]
    # Holm si ferma al primo che non passa: quelli dopo non sono significativi comunque
    fermato = False
    for r in calcolabili:
        if fermato:
            r["passa"] = False
        elif not r["passa"]:
            fermato = True
    return calcolabili


def lungo(celle):
    """Le celle in forma lunga: una riga per (modello, infra, trasporto, binario)."""
    righe = []
    for (m, i, t, b), v in celle.items():
        if v:
            righe.append({"modello": m, "infra": i, "trasporto": t, "binario": b,
                          "pass_rate": st.mean(v[:RUN_ATTESI])})
    return righe


def t9_t10(celle, tipo):
    """T9 (eterogeneita' fra modelli) e T10 (interazione trasporto x infrastruttura).

    Il valore che entra in Holm e' quello PRE-REGISTRATO in §7, cioe' il modello misto.
    Accanto si calcola un test esatto sulle stesse quantita', perche' con quattro livelli di
    modello una componente di varianza e' al limite di cio' che si stima, e un LRT su una
    varianza al confine dello spazio dei parametri non e' chi-quadro puro. In C1 le due
    letture dello stesso slope davano p=0,29 e p=0,41: si riportano entrambe, non si sceglie.
    """
    vuoto = {"id": "", "eti": tipo, "n": 0, "med": float("nan"), "lo": float("nan"),
             "hi": float("nan"), "p": float("nan"), "esatto": None}
    righe = lungo(celle)
    if not righe:
        return {**vuoto, "id": "T9" if tipo == "eterogeneita" else "T10"}

    # --- la parte esatta, che non dipende da nessuna libreria -------------------------
    def delta(modello, infra):
        n = {r["binario"]: r["pass_rate"] for r in righe
             if (r["modello"], r["infra"], r["trasporto"]) == (modello, infra, "native")}
        t = {r["binario"]: r["pass_rate"] for r in righe
             if (r["modello"], r["infra"], r["trasporto"]) == (modello, infra, "text")}
        com = sorted(set(n) & set(t))
        return {b: t[b] - n[b] for b in com}

    if tipo == "eterogeneita":
        gruppi = [list(delta(m, "databricks").values()) for m in MODELLI]
        gruppi = [g for g in gruppi if len(g) > 1]
        p_esatto = _anova_una_via(gruppi) if len(gruppi) > 1 else float("nan")
        eti = "eterogeneita' dell'effetto trasporto fra modelli"
        med = float("nan")
    else:
        # Per ogni modello, la differenza fra le due differenze: e' l'interazione, appaiata
        # sul binario. Si aggrega sui modelli come media delle stime per modello.
        stime, ps = [], []
        for m in MODELLI:
            dd, db = delta(m, "databricks"), delta(m, "bedrock")
            com = sorted(set(dd) & set(db))
            if len(com) < 2:
                continue
            d = [dd[b] - db[b] for b in com]
            n_, med_, lo_, hi_, t_, p_ = t_appaiato({i: 0.0 for i in range(len(d))},
                                                    dict(enumerate(d)))
            stime.append(med_)
            ps.append(p_)
        p_esatto = min(ps) * len(ps) if ps else float("nan")   # Bonferroni sui modelli
        p_esatto = min(p_esatto, 1.0) if ps else float("nan")
        med = st.mean(stime) if stime else float("nan")
        eti = "interazione trasporto x infrastruttura"

    # --- la parte pre-registrata: modello misto --------------------------------------
    p_misto = _misto(righe, tipo)
    return {"id": "T9" if tipo == "eterogeneita" else "T10", "eti": eti,
            "n": len(righe), "med": med, "lo": float("nan"), "hi": float("nan"),
            "p": p_misto, "esatto": p_esatto}


def _anova_una_via(gruppi):
    """F test fra gruppi, senza dipendenze. p dalla F con approssimazione normale sui log,
    sufficiente a distinguere ordini di grandezza; il valore esatto lo da' il misto."""
    k = len(gruppi)
    n_tot = sum(len(g) for g in gruppi)
    if k < 2 or n_tot <= k:
        return float("nan")
    media = st.mean([x for g in gruppi for x in g])
    ss_fra = sum(len(g) * (st.mean(g) - media) ** 2 for g in gruppi)
    ss_dentro = sum((x - st.mean(g)) ** 2 for g in gruppi for x in g)
    if ss_dentro <= 0:
        return 0.0
    F = (ss_fra / (k - 1)) / (ss_dentro / (n_tot - k))
    # trasformazione di Wilson-Hilferty: F -> normale
    d1, d2 = k - 1, n_tot - k
    z = ((F ** (1 / 3)) * (1 - 2 / (9 * d2)) - (1 - 2 / (9 * d1))) / \
        math.sqrt(2 / (9 * d1) + (F ** (2 / 3)) * 2 / (9 * d2))
    return 1 - _norm_cdf(z)


def _misto(righe, tipo):
    """Il modello misto di §7. Se statsmodels non c'e', il test resta non calcolabile e lo
    dice: sostituirlo in silenzio con l'esatto cambierebbe il test pre-registrato."""
    try:
        import pandas as pd
        import statsmodels.formula.api as smf
    except ImportError:
        return float("nan")
    df = pd.DataFrame(righe)
    df["tr"] = (df["trasporto"] == "text").astype(int)
    # NON chiamarla "inf": patsy la parsa come infinito e la formula esplode con un
    # PatsyError che un `except Exception` nudo trasformerebbe in "non calcolabile".
    df["cloud"] = (df["infra"] == "bedrock").astype(int)
    try:
        if tipo == "eterogeneita":
            pieno = smf.mixedlm("pass_rate ~ tr", df, groups=df["modello"],
                                re_formula="~tr").fit(reml=False)
            nullo = smf.mixedlm("pass_rate ~ tr", df, groups=df["modello"]).fit(reml=False)
            lr = 2 * (pieno.llf - nullo.llf)
            # Varianza al confine: mistura 0.5*chi2_1 + 0.5*chi2_2, non chi2 puro.
            p1 = 1 - _chi2_cdf(lr, 1)
            p2 = 1 - _chi2_cdf(lr, 2)
            return 0.5 * p1 + 0.5 * p2
        m = smf.mixedlm("pass_rate ~ tr * cloud", df, groups=df["modello"]).fit(reml=False)
        return float(m.pvalues.get("tr:cloud", float("nan")))
    except Exception as e:
        # Il perche' si stampa. Un test pre-registrato che diventa "non calcolabile" senza
        # dire la ragione e' indistinguibile da un test che non c'e': in C1 un campo scritto
        # dall'harness e letto da nessuno costo' un finding pubblicato e poi ritirato.
        print(f"    [misto {tipo}] non calcolabile: {type(e).__name__}: {str(e)[:120]}")
        return float("nan")


def _chi2_cdf(x, k):
    if x <= 0:
        return 0.0
    if k == 1:
        return math.erf(math.sqrt(x / 2))
    if k == 2:
        return 1 - math.exp(-x / 2)
    return float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--consenti-parziale", action="store_true",
                    help="calcola anche su celle incomplete. NON usare per il confermativo: "
                         "i binari si processano in ordine di indice e i primi sono piu' "
                         "facili, quindi la media su un prefisso stima i binari facili.")
    a = ap.parse_args()

    celle, non_eseguibili = carica(a.results)
    if not celle:
        sys.exit(f"nessuna misurazione in {a.results}/ — non c'e' niente da analizzare")

    # --- completezza, prima di qualunque numero -------------------------------------
    atteso = 45
    incomplete = []
    for m in MODELLI:
        for i in INFRA:
            for t in TRASPORTI:
                if (m, i, t) in non_eseguibili:
                    continue
                n = len(media_per_binario(celle, m, i, t))
                if n < atteso:
                    incomplete.append((m, i, t, n))
    if non_eseguibili:
        print(f"  {len(non_eseguibili)} cella/e NON ESEGUIBILI (rifiuto di piattaforma, "
              f"non fallimento di capacita'):")
        for (m, i, t), msg in sorted(non_eseguibili.items()):
            print(f"    {m} / {i} / {t}: {msg}")
        print()
    if incomplete and not a.consenti_parziale:
        print("  celle incomplete:")
        for m, i, t, n in incomplete:
            print(f"    {m} / {i} / {t}: {n}/{atteso} binari")
        sys.exit("\n  Mi rifiuto di calcolare su bracci parziali. I binari si processano in "
                 "ordine di indice\n  e i primi sono piu' facili: la media su un prefisso "
                 "stima i binari facili, non il braccio.\n  In C1 un braccio a 0,936 a meta' "
                 "raccolta ha chiuso a 0,832.")

    # --- i dieci test ----------------------------------------------------------------
    risultati = []
    for tid, tipo, modello, fisso in FAMIGLIA:
        if tipo == "trasporto":
            a1 = media_per_binario(celle, modello, fisso, "native")
            b1 = media_per_binario(celle, modello, fisso, "text")
            eti = f"{modello} — testo vs nativo su {fisso}"
        elif tipo == "infrastruttura":
            a1 = media_per_binario(celle, modello, "databricks", fisso)
            b1 = media_per_binario(celle, modello, "bedrock", fisso)
            eti = f"{modello} — bedrock vs databricks, trasporto {fisso}"
        else:
            r = t9_t10(celle, tipo)
            risultati.append(r)
            continue
        n, med, lo, hi, t, p = t_appaiato(a1, b1)
        risultati.append({"id": tid, "eti": eti, "n": n, "med": med,
                          "lo": lo, "hi": hi, "p": p})

    print(f"  {'id':<5}{'contrasto':<48}{'K':>4}{'delta':>9}{'IC95':>20}{'p':>10}")
    for r in risultati:
        ic = (f"[{r['lo'] * 100:+.1f},{r['hi'] * 100:+.1f}]"
              if not math.isnan(r["lo"]) else "—")
        d = f"{r['med'] * 100:+.2f}pp" if not math.isnan(r["med"]) else "—"
        p = f"{r['p']:.4f}" if not math.isnan(r["p"]) else "non calcolabile"
        print(f"  {r['id']:<5}{r['eti'][:47]:<48}{r['n']:>4}{d:>9}{ic:>20}{p:>10}")
        e = r.get("esatto")
        if e is not None:
            ee = f"{e:.4f}" if not math.isnan(e) else "non calcolabile"
            print(f"       {ETICHETTA_ESATTO:<48}{'':>4}{'':>9}{'':>20}{ee:>10}")

    # --- Holm, su m fisso ------------------------------------------------------------
    print(f"\n  Holm step-down, m={M_FAMIGLIA} FISSO "
          f"({sum(1 for r in risultati if math.isnan(r['p']))} non calcolabili restano nella "
          f"famiglia e non abbassano nessuna soglia)")
    for r in holm(risultati):
        print(f"    rango {r['rango']:>2}  {r['id']:<5} p={r['p']:.4f}  "
              f"soglia={r['soglia']:.4f}  {'PASSA' if r['passa'] else 'no'}")

    # --- fuori banda: cio' che rifiuta il falsificatore ------------------------------
    print(f"\n  Fuori dalla banda del falsificatore (±{BANDA * 100:.0f}pp, IC95 che la esclude):")
    fuori = [r for r in risultati
             if not math.isnan(r["lo"]) and (r["lo"] > BANDA or r["hi"] < -BANDA)]
    if fuori:
        for r in fuori:
            print(f"    {r['id']} {r['eti']}: {r['med'] * 100:+.2f}pp "
                  f"[{r['lo'] * 100:+.1f},{r['hi'] * 100:+.1f}]")
    else:
        print("    nessuno. NB: K=45 non alimenta un test di equivalenza a 3pp (serve K>=99),")
        print("    quindi questo NON e' 'nessuna differenza': e' 'l'IC esclude effetti sopra")
        print("    4,9pp'. La distinzione e' pre-registrata, non scelta adesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
