#!/usr/bin/env python3
"""La Tabella 1 del paper — i dieci test pre-registrati — generata invece che trascritta.

PERCHE' ESISTE. Tre delle sue colonne non le produce nessuno script congelato: i p di Student,
la potenza a t non centrale e l'intervallo di T10. Erano state calcolate una volta e copiate
nel LaTeX a mano, e il seggio riproducibilita' del gauntlet lo ha trovato ricalcolando 20,9%
dove il paper diceva 19,4%. Con la ri-raccolta cambiano tutti e trenta i numeri della tabella:
una trascrizione a mano di trenta numeri e' un difetto in attesa, non un rischio.

COSA ASSEMBLA, e da dove:
  - delta, IC95, p PRE-REGISTRATO, soglia di Holm  <- analysis/analyze_c2.py  (congelato)
  - MDE per contrasto                              <- analysis/potenza_per_contrasto.py
  - SD osservate                                   <- analysis/scomposizione_varianza.py

LA COLONNA p E' QUELLA CONGELATA, e questa e' una decisione, non un'inerzia. La serie esatta di
Student e la serie sign-flip sono SENSIBILITA': stanno in appendice, dichiarate come tali.
Mettere in tabella principale un p migliore calcolato dopo significherebbe presentare come
pre-registrato un test scelto a dati visti — e la differenza fra le due cose e' meta' di questo
paper. Le tre serie danno lo stesso esito di famiglia, e l'appendice lo mostra.

LA COLONNA MDE NON ESISTE PIU' EITHER, e la ragione e' aritmetica invece che retorica. Due seggi
indipendenti del gauntlet hanno osservato che MDE = (z95+z80)*SD/sqrt(K) e semiampiezza dell'IC =
t(0,975;K-1)*SD/sqrt(K) differiscono per una COSTANTE: sulle otto righe il rapporto sta fra 1,3818 e
1,4026, contro il valore predetto 1,3901. La colonna era l'intervallo gia' stampato accanto, in altre
unita'. L'eterogeneita' che il capitolo vuole mostrare -- un fattore 23,7 fra contrasti dello stesso
disegno -- si legge dalle ampiezze degli intervalli e dalle SD di Tab. 2, senza una terza colonna che
non aggiunge un grado di liberta'.

LA COLONNA POTENZA NON ESISTE PIU'. Era potenza osservata: calcolata sulla SD misurata, contro
un MDE fisso. Una potenza a posteriori e' una ri-espressione monotona del p-value e non aggiunge
evidenza; peggio, invita a leggere «p non significativo perche' poco potente», che e'
circolare. Resta l'MDE per contrasto, che e' un'altra quantita': non dice quanto si e' visto,
dice quale effetto quel contrasto avrebbe potuto risolvere data la dispersione osservata. E'
un diagnostico di sensibilita' realizzata, ed e' etichettato cosi'.

La raccolta si scegli dall'ambiente, come negli altri: C2_RESULTS e C2_PATTERN. Il default e'
la ri-raccolta, che per EMENDAMENTO-06 e' la base dei risultati principali — deciso prima che
i dati esistessero, ed e' la clausola che impedisce di preferire a posteriori la raccolta piu'
conveniente.

    C2_RESULTS=results/riraccolta C2_PATTERN='c2r_*.csv' python3 analysis/tabella_principale.py

Un contrasto che manca NON diventa una riga vuota: lo script esce 2. Una tabella con un buco
si pubblica per distrazione, un errore no.
"""
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

RADICE = os.environ.setdefault("C2_RESULTS", "results/riraccolta")
PATTERN = os.environ.setdefault("C2_PATTERN", "c2r_*.csv")

ETICHETTE = {
    "T1": r"gpt-oss,\, transp.", "T2": r"llama,\, transp.",
    "T3": r"haiku,\, transp.", "T4": r"sonnet,\, transp.",
    "T5": r"gpt-oss,\, endp.", "T6": r"llama,\, endp.",
    "T7": r"haiku,\, endp.", "T8": r"sonnet,\, endp.",
    "T9": "heterogeneity", "T10": "interaction",
}


def dallo_script_congelato():
    """delta, IC e p pre-registrato, dal file congelato invocato come processo — non importato.
    Importarlo eseguirebbe il suo main; e comunque il numero che entra in tabella deve venire
    dallo stesso comando che un lettore dell'artefatto puo' lanciare."""
    r = subprocess.run([sys.executable, os.path.join(QUI, "analyze_c2.py"),
                        "--results", RADICE],
                       capture_output=True, text=True, cwd=os.path.dirname(QUI))
    if r.returncode != 0:
        raise SystemExit(f"analyze_c2 e' uscito {r.returncode}:\n{r.stderr[-800:]}")
    fuori = {}
    for riga in r.stdout.splitlines():
        c = riga.split()
        if not c or c[0] not in ETICHETTE:
            continue
        tid = c[0]
        # ...  K  delta  IC  p   — le ultime quattro colonne, con delta e IC assenti su T9
        p = c[-1]
        ic = c[-2]
        delta = c[-3]
        fuori[tid] = {"delta": delta, "ic": ic, "p_prereg": p}
    return fuori


def soglie_holm(p_per_test, m=10):
    """Le soglie di Holm, dal p pre-registrato. In tabella invece che nella sola prosa: una
    colonna che porta la soglia accanto al p rende l'esito leggibile senza fidarsi di una frase."""
    ordinati = sorted(p_per_test.items(), key=lambda kv: kv[1])
    return {t: 0.05 / (m - i) for i, (t, _) in enumerate(ordinati)}


def numeri():
    cong = dallo_script_congelato()
    soglie = soglie_holm({t: float(c["p_prereg"]) for t, c in cong.items()})
    return cong, soglie


def formatta(cong, soglie):
    righe = []
    for tid in ETICHETTE:
        if tid not in cong:
            raise SystemExit(f"  contrasto {tid} assente: la tabella avrebbe un buco")
        c = cong[tid]
        p = c["p_prereg"]
        sog = f"{soglie[tid]:.4f}"
        d = c["delta"].replace("pp", "")
        ic = c["ic"].replace("[", "$[").replace("]", "]$")
        # T9 non ha un delta; T10 lo ha ma non un intervallo prodotto dallo script congelato,
        # e quello calcolato fuori con n=4 e' stato tolto (SPEC-20): un intervallo su quattro
        # unita', generato fuori dalla procedura congelata, non appartiene alla tabella
        # confermativa. Resta la stima puntuale e l'esito del test pre-registrato.
        if tid == "T9":
            d, ic = "---", "---"
        elif tid == "T10":
            ic = "---"
        righe.append((float(p), tid, d if d == "---" else f"${d}$", ic, p, sog))
    righe.sort()
    return righe


AXIS = {"T1": "transport", "T2": "transport", "T3": "transport", "T4": "transport",
        "T5": "endpoint", "T6": "endpoint", "T7": "endpoint", "T8": "endpoint"}


def tabella_varianza():
    """La decomposizione, Tabella 2. Stessa ragione della prima: era trascritta, e la
    ri-raccolta cambia tutti e ventiquattro i suoi numeri."""
    import scomposizione_varianza as sv
    righe = []
    for tid, mod, a, b in sv.CONTRASTI:
        r = sv.scomponi(mod, a, b)
        if r is None:
            continue
        q = r["quota"]
        marca = "$^\\dagger$" if q >= 1.0 else ""
        righe.append((q, tid, AXIS[tid], r["sd_oss"], q, r["k_inf"], marca))
    righe.sort()
    print(f"% Generata da analysis/tabella_principale.py --varianza su {RADICE}.")
    print(r"\begin{table}[t]")
    print(r"\caption{Variance decomposition. $K_\infty$ is the number of binaries needed to "
          r"resolve 3pp with unlimited runs per binary. $\dagger$: on these two contrasts the "
          r"components are \textbf{poorly identified at the boundary} --- the estimated noise "
          r"exceeds the observed variance, and the bootstrap clamps the residual to zero in 86\% "
          r"of replications on T7 and 69\% on T8. No component is reported for them, in either "
          r"direction: a clamped estimate is a boundary artefact, and printing a precise zero "
          r"would report the constraint rather than the data. T1, T3 and T6 clamp in at "
          r"most 1\% of replications, and are the rows the decomposition is read on.}")
    print(r"\label{tab:variance}")
    print(r"\centering")
    print(r"\small")
    print(r"\begin{tabular}{llrrr}")
    print(r"\toprule")
    print(r"& axis & SD & \% noise & $K_\infty$ \\")
    print(r"\midrule")
    for _, tid, ax, sd, q, kinf, marca in righe:
        # Dove la quota di rumore eccede la varianza osservata il modello non regge su quella
        # cella, e il testo dichiara di non riportarne la decomposizione: stampare comunque una
        # SD e un K_inf contraddirebbe la frase che sta due paragrafi sopra. Si stampa la SD, che
        # e' osservata, e si nega il resto — che e' stimato da un modello che non si adatta.
        if q >= 1.0:
            print(f"{tid} & {ax} & {sd:.4f} & \\multicolumn{{2}}{{c}}{{not decomposable$^\\dagger$}} \\\\")
        else:
            print(f"{tid} & {ax} & {sd:.4f} & {100*q:.1f}\\%{marca} & {kinf:.0f} \\\\")
    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{table}")


if __name__ == "__main__":
    if "--varianza" in sys.argv:
        tabella_varianza()
        raise SystemExit(0)
    cong, soglie = numeri()
    righe = formatta(cong, soglie)

    fonte = "re-collection (isolated workspaces)" if "riraccolta" in RADICE \
        else "original collection"

    print(f"% Generata da analysis/tabella_principale.py su {RADICE} — non modificare a mano.")
    print(r"\begin{table}[t]")
    print(r"\caption{The ten pre-registered tests, on the " + fonte + r". \textbf{The $p$ column "
          r"is the one the frozen analysis script emits}, so this table is the pre-registered "
          r"analysis and nothing else; the exact-Student and distribution-free series are "
          r"sensitivity analyses and are reported in Appendix~\ref{sec:appendice-permutazione}, "
          r"where the family outcome is the same under all three. $\delta$ is the paired "
          r"difference per binary, over 45 binaries of 8 runs each. \textbf{Sign convention}: for "
          r"transport contrasts $\delta = \text{textual} - \text{native}$, so a negative value "
          r"means the textual protocol scores lower; for endpoint contrasts $\delta = "
          r"\text{Bedrock} - \text{Databricks}$. The Holm column is each test's own threshold at "
          r"the pre-registered $m{=}10$, printed beside its $p$ so the outcome is readable "
          r"without trusting a sentence. \textbf{The interval widths carry the heterogeneity}: "
          r"they differ by a factor of 23.7 across contrasts of one design, which is what makes a "
          r"single pre-specified band the wrong instrument for all eight. "
          r"$^{\P}$T5's $\delta$ and interval rest on $K{=}45$; "
          r"one of its binaries returned seven valid runs of eight on one endpoint, which the "
          r"frozen script averages and the exact-$p$ sensitivity script excludes, so that "
          r"sensitivity series rests on $K{=}44$ for this row alone. $^{\ast}$T6 is a contrast "
          r"between two deployed services: they differ in provider-reported input tokens, in "
          r"latency and in turns used (\S\ref{sec:runtime}), and the source of the score "
          r"difference is not identified.}")
    print(r"\label{tab:tests}")
    print(r"\centering")
    print(r"\scriptsize")
    print(r"\setlength{\tabcolsep}{2.6pt}")
    print(r"\begin{tabular}{llrrrr}")
    print(r"\toprule")
    print(r"& contrast & $\delta$ & 95\% CI & $p$ (frozen) & Holm thr. \\")
    print(r"\midrule")
    for _, tid, d, ic, p, sog in righe:
        marca = {"T5": r"$^{\P}$", "T6": r"$^{\ast}$"}.get(tid, "")
        print(f"{tid}{marca} & {ETICHETTE[tid]} & {d} & {ic} & {p} & {sog} \\\\")
    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{table}")
