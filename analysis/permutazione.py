#!/usr/bin/env python3
"""R8 — test di permutazione sui contrasti appaiati, come analisi di sensibilita' NON pre-registrata.

PERCHE'. Il test pre-registrato e' un t appaiato su 45 binari, e un t appaiato assume che le
differenze siano approssimativamente normali. Su questa metrica non lo sono: pass-rate su cinque
unit test ha sei valori possibili, il 53% delle righe sta agli estremi, e la differenza appaiata di
due medie a sei livelli e' discreta e con code corte. L'obiezione e' legittima e costa poco
chiuderla: se un test che NON assume normalita' da' le stesse conclusioni, l'assunzione non stava
portando il risultato.

IL TEST. Per differenze appaiate il test di permutazione esatto e' il **sign-flip**: sotto l'ipotesi
nulla di nessun effetto, il segno di ciascuna differenza per binario e' scambiabile. Si enumerano
(o si campionano) le $2^{45}$ assegnazioni di segno, si ricalcola la media, e il p e' la frazione di
permutazioni con |media| almeno pari a quella osservata. Non assume nessuna distribuzione: assume
scambiabilita' del segno, che e' esattamente cio' che l'ipotesi nulla afferma.

$2^{45}$ e' oltre 35mila miliardi, quindi si campiona con seme fisso e si riporta l'errore Monte
Carlo del p stesso --- perche' un p ottenuto per campionamento e' una stima, e riportarlo senza la
sua incertezza sarebbe lo stesso errore che questo paper contesta altrove.

QUESTA ANALISI NON E' PRE-REGISTRATA e non sostituisce nulla: si riporta accanto, dichiarata come
sensibilita'. Se le conclusioni divergessero, la conclusione da riportare resterebbe quella
pre-registrata, con la divergenza dichiarata come limite.

    python3 analysis/permutazione.py                    # base primaria
    python3 analysis/permutazione.py --confermativa     # raccolta originale
    python3 analysis/permutazione.py --B 200000         # piu' permutazioni
"""
import math
import os
import random
import statistics as st
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

SEME = 20260819
B_DEFAULT = 50000
M_FAMIGLIA = 10          # la stessa famiglia fissa del test pre-registrato


def sign_flip(diff, B, rng):
    """p bilaterale per sign-flip, e l'errore Monte Carlo del p stesso."""
    oss = abs(st.mean(diff))
    n = len(diff)
    estremi = 0
    for _ in range(B):
        s = sum(d if rng.random() < 0.5 else -d for d in diff)
        if abs(s / n) >= oss - 1e-15:
            estremi += 1
    # +1 al numeratore e al denominatore: il p di un test di permutazione campionato non e' mai
    # zero, perche' la permutazione identita' e' sempre fra quelle possibili.
    p = (estremi + 1) / (B + 1)
    se = math.sqrt(p * (1 - p) / B)
    return p, se, estremi


def holm(coppie, m):
    """Holm step-down a m fisso, la stessa politica del test pre-registrato."""
    ordinate = sorted(coppie, key=lambda x: x[1])
    fuori, passa_ancora = [], True
    for i, (tid, p) in enumerate(ordinate):
        soglia = 0.05 / (m - i)
        passa = passa_ancora and p <= soglia
        passa_ancora = passa
        fuori.append((tid, p, soglia, passa))
    return fuori


def p_congelati():
    """I p che lo script congelato emette, presi dallo stesso comando che un lettore lancia.
    Servono qui perche' l'appendice e' il posto in cui le TRE serie stanno accanto: la
    pre-registrata, l'esatta di Student e la sign-flip. Separarle in tre tabelle diverse e' il
    modo piu' facile per far leggere come confermativa una serie che non lo e'."""
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(QUI, "analyze_c2.py"),
                        "--results", os.environ.get("C2_RESULTS", "results/riraccolta")],
                       capture_output=True, text=True, cwd=os.path.dirname(QUI))
    if r.returncode != 0:
        raise SystemExit("analyze_c2 e' uscito %d" % r.returncode)
    fuori = {}
    for riga in r.stdout.splitlines():
        c = riga.split()
        if c and c[0].startswith("T") and c[0][1:].isdigit():
            fuori[c[0]] = float(c[-1])
    return fuori


def latex(righe, B):
    """La tabella dell'appendice, generata. Era trascritta a mano, e la trascrizione e' andata alla
    deriva: il paper dichiarava B=50.000 mentre i numeri stampati venivano da B=20.000. Un seggio di
    conformita' l'ha trovato rigenerando con l'invocazione documentata e confrontando byte per byte.
    Una tabella che si genera non puo' divergere dal proprio script."""
    print("% Generata da analysis/permutazione.py --latex — non modificare a mano.")
    print(r"\begin{table}[h]")
    print(r"\centering")
    b_tex = f"{B:,}".replace(",", "{,}")   # solo il NUMERO prende il separatore TeX: la prima
    # versione applicava .replace alla stringa intera e trasformava la virgola della prosa in
    # «Student's $t${,} on», che si compone come un separatore di migliaia dentro una frase.
    print(r"\caption{\textbf{Two sensitivity series beside the pre-registered one.} The "
          r"\emph{frozen} column is the $p$ the pre-registered script emits and is the series "
          r"Table~\ref{tab:tests} reports; the other two were computed after the data existed and "
          r"are sensitivity analyses, not confirmatory results. \emph{Exact} is the exact Student "
          r"series on the same paired quantities; \emph{sign-flip} is the distribution-free "
          r"permutation on " + b_tex + r" sampled sign assignments at a declared seed. Holm applies "
          r"the same fixed $m{=}10$ throughout. The Monte Carlo column is the standard error of the "
          r"sampled $p$ itself: a $p$ obtained by sampling is an estimate, and reporting it without "
          r"its uncertainty would be the error this paper objects to elsewhere. No test passes its "
          r"Holm threshold under any of the three series, so the family outcome does not depend on "
          r"which one is read.}")
    print(r"\label{tab:permutazione}")
    print(r"\footnotesize")
    print(r"\setlength{\tabcolsep}{4pt}")
    cong = p_congelati()
    print(r"\begin{tabular}{@{}lrrrrr@{}}")
    print(r"\toprule")
    print(r"& $p$ frozen & $p$ exact & $p$ sign-flip & MC error & exact $\rightarrow$ flip \\")
    print(r"\midrule")
    for tid, ps, pp, se in righe:
        pc = cong.get(tid)
        pc_s = f"{pc:.4f}" if pc is not None else "---"
        print(f"{tid} & {pc_s} & {ps:.4f} & {pp:.4f} & {se:.4f} & ${pp-ps:+.4f}$ \\\\")
    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{table}")


if __name__ == "__main__":
    conf = "--confermativa" in sys.argv
    vuole_latex = "--latex" in sys.argv
    B = B_DEFAULT
    if "--B" in sys.argv:
        B = int(sys.argv[sys.argv.index("--B") + 1])

    os.environ["C2_RESULTS"] = "results" if conf else "results/riraccolta"
    os.environ["C2_PATTERN"] = "c2_*.csv" if conf else "c2r_*.csv"
    import scomposizione_varianza as sv
    from scipy import stats

    rng = random.Random(SEME)
    if not vuole_latex:
        print(f"  sign-flip su {B} permutazioni, seme={SEME}, "
              f"raccolta {'confermativa' if conf else 'primaria'}\n")
        print(f"  {'':5}{'K':>4}{'delta':>9}{'p Student':>12}{'p permut.':>12}"
              f"{'MC err':>9}{'differenza':>12}")

    coppie = []
    righe_tab = []
    for tid, mod, ca, cb in sv.CONTRASTI:
        a = sv.runs_per_binario(mod, *ca)
        b = sv.runs_per_binario(mod, *cb)
        com = sorted(set(a) & set(b))
        if len(com) < 2:
            continue
        diff = [st.mean(b[k]) - st.mean(a[k]) for k in com]
        med = st.mean(diff)
        t = med / (st.stdev(diff) / math.sqrt(len(diff)))
        p_stud = 2 * stats.t.sf(abs(t), df=len(diff) - 1)
        p_perm, se, _ = sign_flip(diff, B, rng)
        coppie.append((tid, p_perm))
        righe_tab.append((tid, p_stud, p_perm, se))
        if not vuole_latex:
            print(f"  {tid:<5}{len(com):>4}{100*med:>+8.2f}{p_stud:>12.4f}{p_perm:>12.4f}"
                  f"{se:>9.4f}{p_perm - p_stud:>+12.4f}")

    if vuole_latex:
        # Ordinate per il p CONGELATO, non per l'esatto: la prima colonna e' quella confermativa,
        # e una tabella ordinata su una colonna di sensibilita' si legge fuori ordine nell'altra.
        _cong = p_congelati()
        righe_tab.sort(key=lambda r: _cong.get(r[0], r[1]))
        latex(righe_tab, B)
        raise SystemExit(0)

    print(f"\n  Holm step-down sui p di permutazione, m={M_FAMIGLIA} fisso "
          f"(la stessa politica del pre-registrato)")
    esiti = holm(coppie, M_FAMIGLIA)
    passano = [t for t, _, _, ok in esiti if ok]
    for i, (tid, p, soglia, ok) in enumerate(esiti, 1):
        print(f"    rango {i:>2}  {tid:<5}p={p:.4f}  soglia={soglia:.4f}  "
              f"{'PASSA' if ok else 'no'}")
    print(f"\n  {len(passano)} test superano la soglia"
          + (f": {', '.join(passano)}" if passano else " — nessuno"))

    # --- il confronto che l'obiezione chiede -----------------------------------------
    print("\n  LA RISPOSTA ALL'OBIEZIONE")
    if not passano:
        print("    Nessun test supera Holm ne' con il t appaiato pre-registrato ne' con il")
        print("    sign-flip, che non assume normalita'. La conclusione della famiglia non")
        print("    dipende dall'assunzione distributiva, e l'obiezione e' chiusa senza")
        print("    cambiare nulla di pre-registrato.")
    else:
        print(f"    ATTENZIONE: {len(passano)} test passano con la permutazione e non con il t.")
        print("    La conclusione da riportare resta quella pre-registrata; questa divergenza")
        print("    va dichiarata come limite, non usata per sostituire il risultato.")

    # --- controllo a risposta nota, nei due sensi -------------------------------------
    print("\n  CONTROLLO a risposta nota, nei due sensi")
    ok = []
    finto = [0.10] * 45
    p_f, _, _ = sign_flip(finto, 2000, random.Random(1))
    ok.append(p_f < 0.01)
    print(f"    45 differenze tutte +0,10 (effetto enorme) -> p={p_f:.4f}: "
          + ("ok" if p_f < 0.01 else "FALLITO: dovrebbe essere minuscolo"))
    nullo = [0.10 if i % 2 else -0.10 for i in range(44)]
    p_n, _, _ = sign_flip(nullo, 2000, random.Random(2))
    ok.append(p_n > 0.5)
    print(f"    44 differenze a somma zero (nessun effetto) -> p={p_n:.4f}: "
          + ("ok" if p_n > 0.5 else "FALLITO: dovrebbe essere grande"))
    if not all(ok):
        raise SystemExit("  il test di permutazione non rispetta le sue proprieta'")
