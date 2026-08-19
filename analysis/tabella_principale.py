#!/usr/bin/env python3
"""La Tabella 1 del paper — i dieci test pre-registrati — generata invece che trascritta.

PERCHE' ESISTE. Tre delle sue colonne non le produce nessuno script congelato: i p di Student,
la potenza a t non centrale e l'intervallo di T10. Erano state calcolate una volta e copiate
nel LaTeX a mano, e il seggio riproducibilita' del gauntlet lo ha trovato ricalcolando 20,9%
dove il paper diceva 19,4%. Con la ri-raccolta cambiano tutti e trenta i numeri della tabella:
una trascrizione a mano di trenta numeri e' un difetto in attesa, non un rischio.

COSA ASSEMBLA, e da dove:
  - delta, IC95, p pre-registrato   <- analysis/analyze_c2.py         (congelato, importato)
  - p di Student                    <- analysis/p_esatti_student.py
  - potenza, IC di T10              <- analysis/potenza_per_contrasto.py
  - SD osservate                    <- analysis/scomposizione_varianza.py

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


def numeri():
    import p_esatti_student as pes
    import potenza_per_contrasto as pc
    import statistics as st
    import math
    from scipy import stats

    cong = dallo_script_congelato()
    student = {t: f"{ps:.4f}" for t, _, _, _, ps in pes.serie()}
    student.update({t: f"{v:.4f}" for t, v in pes.p_misto_dal_congelato().items()})
    pot = {t: pc.potenza_t(sd) for t, _, sd in pc.SD}
    # R12: la potenza a MDE fisso e' una sola faccia. L'MDE per contrasto dice, per ciascuno,
    # quale effetto sarebbe stato risolvibile all'80% — e su otto contrasti dello stesso disegno
    # varia di un fattore 23,7, che e' il punto del capitolo. Le due colonne stanno insieme:
    # la potenza risponde «quanto vedeva a 4,87pp», l'MDE «cosa serviva per vedere».
    import math as _m
    Z80 = 1.959964 + 0.841621
    mde = {t: 100 * Z80 * sd / _m.sqrt(45) for t, _, sd in pc.SD}

    # IC di T10, con il modello come unita' di replicazione
    stime = pc.T10_PER_MODELLO
    med = st.mean(stime)
    se = st.stdev(stime) / math.sqrt(len(stime))
    tc = stats.t.ppf(0.975, df=len(stime) - 1)
    t10 = (100 * med, 100 * (med - tc * se), 100 * (med + tc * se))
    return cong, student, pot, t10, mde


def formatta(cong, student, pot, t10, mde):
    righe = []
    for tid in ETICHETTE:
        if tid not in cong:
            raise SystemExit(f"  contrasto {tid} assente: la tabella avrebbe un buco (exit 2)")
        c = cong[tid]
        p = student.get(tid, c["p_prereg"])
        pw = pot.get(tid)
        md = mde.get(tid)
        if tid == "T9":
            righe.append((float(p), tid, "---", "---", p, "---", "---"))
        elif tid == "T10":
            ic = f"$[{t10[1]:+.1f},{t10[2]:+.1f}]^{{\\S}}$"
            righe.append((float(p), tid, f"${t10[0]:+.2f}$", ic, p, "---", "---"))
        else:
            d = c["delta"].replace("pp", "").replace("+", "+").replace("-", "-")
            ic = c["ic"].replace("[", "$[").replace("]", "]$")
            righe.append((float(p), tid, f"${d}$", ic, p,
                          f"{100*pw:.1f}\\%" if pw is not None else "---",
                          f"{md:.2f}" if md is not None else "---"))
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
          r"resolve 3pp with unlimited runs per binary. $\dagger$: the estimated noise exceeds "
          r"the observed variance, so the variance model does not fit that cell and its "
          r"decomposition is not reported --- the bootstrap clamps the residual to zero in 86\% "
          r"and 69\% of replications respectively.}")
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
    cong, student, pot, t10, mde = numeri()
    righe = formatta(cong, student, pot, t10, mde)

    fonte = "re-collection (isolated workspaces)" if "riraccolta" in RADICE \
        else "original collection"

    # Il divario normale-vs-t era scritto in didascalia come «0.7--2.0 points»: misurato sulla
    # raccolta confermativa e falso sulla ri-raccolta, dove T7 satura e il minimo e' 0,0. Una
    # didascalia e' prosa, e la regola sui numeri in prosa non fa eccezione per le didascalie.
    import potenza_per_contrasto as _pc
    div = sorted(100 * (_pc.potenza_normale(sd) - _pc.potenza_t(sd)) for _, _, sd in _pc.SD)
    divario = f"{div[0]:.1f}--{div[-1]:.1f}"
    print(f"% Generata da analysis/tabella_principale.py su {RADICE} — non modificare a mano.")
    print(r"\begin{table}[t]")
    print(r"\caption{The ten pre-registered tests, on the " + fonte + r". $\delta$ is the "
          r"paired difference per binary, over 45 binaries of 8 runs each. \textbf{Sign "
          r"convention}: for transport contrasts $\delta = \text{textual} - \text{native}$, so a "
          r"negative value means the textual protocol scores lower; for endpoint contrasts "
          r"$\delta = \text{Bedrock} - \text{Databricks}$. MDE is the effect this contrast could "
          r"have resolved at 80\% power given its own observed standard deviation, in percentage "
          r"points --- the column exists because it varies by a factor of 23.7 across contrasts "
          r"of one design. Power is computed "
          r"against the pre-registered MDE of 4.87pp using the \emph{observed} standard "
          r"deviation and the non-central $t$ --- the distribution the test actually uses. "
          r"A normal approximation would report " + divario + r" points higher, which in a "
          r"paper reporting its own under-powering would err in the flattering direction. "
          r"$^\ddagger$The $p$ column is the \emph{exact} Student series, not the approximation the "
          r"frozen script emits: the approximation understates $p$ in eight cases of eight --- for "
          r"T6, 0.0155 against 0.0191 --- always in the direction that makes an effect look more "
          r"significant. Both series are in the artifact, the distribution-free series is in "
          r"Appendix~\ref{sec:appendice-permutazione}, and no test passes its Holm threshold under "
          r"any of the three. $^{\P}$T5 is the one contrast whose $p$ rests on $K{=}44$ while its "
          r"$\delta$ and interval rest on $K{=}45$: one binary returned seven valid runs of eight on "
          r"one endpoint, the frozen script averages it and the exact-$p$ script requires a full "
          r"complement. We print both rather than harmonise them, because harmonising would mean "
          r"choosing a rule after seeing what it does to a pre-registered number.}")
    print(r"\label{tab:tests}")
    print(r"\centering")
    print(r"\scriptsize")
    print(r"\setlength{\tabcolsep}{2.2pt}")
    print(r"\begin{tabular}{llrrrrr}")
    print(r"\toprule")
    print(r"& contrast & $\delta$ & 95\% CI & $p$$^\ddagger$ & power & MDE \\")
    print(r"\midrule")
    for _, tid, d, ic, p, pw, md in righe:
        # T5 e' l'unico contrasto il cui p poggia su un K diverso da quello del suo delta: si
        # marca nella riga invece di lasciarlo a chi confronta due script.
        marca = r"$^{\P}$" if tid == "T5" else ""
        print(f"{tid}{marca} & {ETICHETTE[tid]} & {d} & {ic} & {p} & {pw} & {md} \\\\")
    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{table}")
