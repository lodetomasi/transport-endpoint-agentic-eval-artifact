#!/usr/bin/env python3
"""Controllo statico del sorgente LaTeX, perche' su questa macchina non c'e' un compilatore.

NON sostituisce una compilazione e non pretende di farlo. Prende le tre classi di rottura che
una riscrittura di sezioni introduce davvero: ambienti sbilanciati, righe di tabella con un
numero di colonne diverso dal preambolo, riferimenti a etichette che non esistono.

CONTROLLO A RISPOSTA NOTA, nei due sensi: il file di prova in coda contiene un errore di ogni
classe e uno di ogni classe che deve passare.

    python3 revisione/controlla_latex.py [--autotest]
"""
import glob, os, re, sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def senza_commenti(t):
    return re.sub(r"(?<!\\)%.*", "", t)


def ambienti(t):
    """(env, riga) aperti e mai chiusi, o chiusi e mai aperti."""
    pila, errori = [], []
    for i, riga in enumerate(t.splitlines(), 1):
        for m in re.finditer(r"\\(begin|end)\{([^}]+)\}", riga):
            if m.group(1) == "begin":
                pila.append((m.group(2), i))
            else:
                if not pila or pila[-1][0] != m.group(2):
                    errori.append(("chiusura senza apertura", m.group(2), i))
                else:
                    pila.pop()
    return errori + [("apertura senza chiusura", e, r) for e, r in pila]


def colonne(t):
    """Righe di tabular con un numero di & diverso da quello che il preambolo dichiara."""
    errori = []
    for m in re.finditer(r"\\begin\{tabular\}(?:\[[^\]]*\])?\{", t):
        # Il preambolo va letto CONTANDO LE GRAFFE: `p{0.07\linewidth}` ne contiene una coppia,
        # e una regex non annidata si ferma li' leggendo zero colonne. La prima versione di questo
        # script lo faceva, dichiarava 46 guasti e li dichiarava tutti per un difetto proprio.
        i, prof = m.end(), 1
        while i < len(t) and prof:
            prof += (t[i] == "{") - (t[i] == "}")
            i += 1
        pre = t[m.end():i - 1]
        fine = t.find("\\end{tabular}", i)
        if fine < 0:
            continue
        corpo = t[i:fine]
        # colonne del preambolo: l/c/r/p{..}, ignorando @{..} e |
        # Il preambolo si consuma da sinistra, un token per volta. Contare con una regex
        # globale sbaglia appena entra un `P{0.155\linewidth}`: la `l` di «linewidth» diventa
        # una colonna. Sulla tabella dei meccanismi il conto tornava lo stesso, per compenso
        # fra due errori --- cioe' il controllo passava per la ragione sbagliata.
        n, i = 0, 0
        while i < len(pre):
            c = pre[i]
            if c in " \t":
                i += 1
            elif c in "|":
                i += 1
            elif c in "@!><":                      # @{..} !{..} >{..} <{..}: non sono colonne
                i += 1
                if i < len(pre) and pre[i] == "{":
                    prof = 1; i += 1
                    while i < len(pre) and prof:
                        prof += (pre[i] == "{") - (pre[i] == "}"); i += 1
            elif c in "lcrX":
                n += 1; i += 1
            elif c in "pmbPMB":                    # p{..} m{..} b{..} e i newcolumntype in maiuscolo
                n += 1; i += 1
                if i < len(pre) and pre[i] == "{":
                    prof = 1; i += 1
                    while i < len(pre) and prof:
                        prof += (pre[i] == "{") - (pre[i] == "}"); i += 1
            elif c == "*":                          # *{n}{spec}: non usato qui, ma non va contato come colonna
                i += 1
            else:
                i += 1
        base = t[:m.start()].count("\n") + 1
        for j, riga in enumerate(corpo.split("\\\\")):
            if not riga.strip() or re.match(r"^\s*\\(top|mid|bottom)rule", riga.strip()):
                continue
            if "\\multicolumn" in riga:
                continue    # il conteggio non e' banale e la riga e' deliberata
            k = len(re.findall(r"(?<!\\)&", riga)) + 1
            if k != n:
                errori.append((base, n, k, " ".join(riga.split())[:70]))
    return errori


def riferimenti(files):
    etichette, usi = set(), []
    for f in files:
        t = senza_commenti(open(f, errors="ignore").read())
        etichette |= set(re.findall(r"\\label\{([^}]+)\}", t))
        for m in re.finditer(r"\\ref\{([^}]+)\}", t):
            usi.append((os.path.basename(f), m.group(1)))
    return [(f, r) for f, r in usi if r not in etichette]


def main(files):
    guasti = 0
    for f in files:
        t = senza_commenti(open(f, errors="ignore").read())
        for tipo, env, riga in ambienti(t):
            print(f"  AMBIENTE  {os.path.basename(f)}:{riga}  {tipo}: {env}"); guasti += 1
        for riga, atteso, avuto, testo in colonne(t):
            print(f"  COLONNE   {os.path.basename(f)}:~{riga}  attese {atteso}, trovate {avuto}: {testo}")
            guasti += 1
    for f, r in riferimenti(files):
        print(f"  RIF ROTTO {f}  \\ref{{{r}}} non ha \\label"); guasti += 1
    return guasti


if __name__ == "__main__":
    if "--autotest" in sys.argv:
        buono = r"\begin{tabular}{lrr}" "\n" r"a & 1 & 2 \\" "\n" r"\end{tabular}" "\n" r"\label{x} \ref{x}"
        cattivo = (r"\begin{tabular}{lrr}" "\n" r"a & 1 \\" "\n" r"\end{tabular}" "\n"
                   r"\begin{itemize}" "\n" r"\ref{mai_definita}")
        import tempfile
        ok = True
        for nome, testo, atteso in (("buono", buono, 0), ("cattivo", cattivo, 3)):
            d = tempfile.mkdtemp(); p = os.path.join(d, "t.tex"); open(p, "w").write(testo)
            n = main([p])
            esito = "ok" if n == atteso else "FALLITO"
            if n != atteso:
                ok = False
            print(f"  autotest {nome}: guasti attesi {atteso}, trovati {n}: {esito}")
        sys.exit(0 if ok else 1)
    files = sorted(glob.glob(os.path.join(RADICE, "paper", "sections", "*.tex"))) + \
        sorted(glob.glob(os.path.join(RADICE, "paper", "tables", "*.tex"))) + \
        [os.path.join(RADICE, "paper", "main.tex")]
    n = main(files)
    print(f"\n  {n} guasti statici su {len(files)} file.")
    sys.exit(1 if n else 0)
