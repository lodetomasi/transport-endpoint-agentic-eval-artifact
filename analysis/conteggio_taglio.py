#!/usr/bin/env python3
"""Il conteggio delle parole del paper, e il taglio fra due stati — con il metodo dichiarato.

PERCHE' ESISTE. Il requisito R18 chiedeva un taglio del 25% e il registro lo dichiarava «FATTO —
25,02%», con una tabella che partiva da 18.760 parole. Quel numero non si riproduce: nessun metodo
di conteggio ricostruibile dai file committati lo restituisce, e lo stesso documento conteneva una
seconda tabella con una base uguale e un esito diverso (16.719, -10,9%). Due percentuali dallo
stesso denominatore sono un denominatore che non e' stato misurato.

La regola del progetto e' che un numero in prosa traccia a un file committato. Una percentuale di
taglio e' un numero in prosa come gli altri, quindi il conteggio diventa uno script con il metodo
scritto dentro, invece di una misura fatta una volta e riportata a memoria.

IL METODO, dichiarato perche' qualsiasi conteggio di parole in LaTeX e' una convenzione:

  1. si contano i file `paper/sections/*.tex` — il corpo. Preambolo, bibliografia e tabelle
     generate non sono prosa d'autore e non entrano;
  2. si toglie tutto cio' che segue un `%` non protetto (commenti);
  3. si toglie ogni macro `\\nome` e il suo argomento opzionale;
  4. si contano i token che cominciano per lettera.

Il punto 3 e' quello che sposta il numero di piu': un conteggio grezzo su `wc -w` include i nomi
delle macro e restituisce circa il 17% in piu'. Nessuna delle due convenzioni e' sbagliata; quella
che rende il numero verificabile e' la convenzione DICHIARATA.

IL DENOMINATORE SI DICHIARA, non si scegle. Un taglio si misura rispetto a uno stato, e in questa
revisione ce ne sono due legittimi:

  - lo stato che il revisore ha letto (`e62d21c`), prima che R1-R17 aggiungessero tre analisi, due
    tabelle, un'appendice e sei dichiarazioni;
  - lo stato piu' lungo (`e4d7327`), cioe' il paper dopo quelle aggiunte e prima del taglio.

Sono due domande diverse: «quanto e' piu' corto di quello che hai letto» e «quanto ho tolto». Lo
script riporta entrambe, perche' riportare solo la seconda sceglierebbe il denominatore che
conviene.

    python3 analysis/conteggio_taglio.py                      # i due tagli, sullo stato attuale
    python3 analysis/conteggio_taglio.py --ref 548cee8         # su un ref invece del working tree
    python3 analysis/conteggio_taglio.py --serie               # il conteggio a ogni commit del corpo
"""
import glob
import io
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)

# I due denominatori, dichiarati qui e non passati da riga di comando: un denominatore che si
# sceglie all'invocazione e' un denominatore che si sceglie a numero visto.
BASE_LETTA = ("e62d21c", "lo stato che il revisore ha letto")
BASE_PIU_LUNGA = ("e4d7327", "il paper al suo massimo, dopo le aggiunte di R1-R17")


# Le macro che NON sono prosa si portano via il proprio argomento: dentro `\\label{sec:results}`
# non c'e' testo d'autore, e contare «sec» e «results» gonfia ogni sezione in proporzione al
# numero di etichette. Le macro di prosa (`\\textbf`, `\\emph`, `\\S`) lo tengono.
NON_PROSA = (r"label|ref|eqref|autoref|cite[a-z]*|input|include|usepackage|documentclass|"
             r"bibliography|bibliographystyle|begin|end|setlength|tabcolsep|multicolumn|"
             r"newcommand|renewcommand|hspace|vspace|includegraphics|IEEEauthorblock[A-Z]")


def conta(testo):
    """Il metodo del docstring. Non ha stato: e' provabile da sola, ed e' provata sotto."""
    # 1. i commenti, ma non un `\%` protetto che e' un segno di percentuale
    testo = re.sub(r'(?<!\\)%.*', '', testo)
    # 2. le macro non di prosa, col loro argomento
    testo = re.sub(r'\\(?:' + NON_PROSA + r')\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})*', ' ', testo)
    # 3. le macro restanti, tenendo l'argomento perche' e' prosa
    testo = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?', ' ', testo)
    # 4. i token che cominciano per lettera. Lunghezza minima UNO, non due: con due, la parola
    #    inglese piu' frequente di tutte, «a», non conterebbe. Un numero come «87.8» non e' una
    #    parola e non conta — e' una convenzione, quindi si dichiara.
    return len(re.findall(r"[A-Za-z][A-Za-z'-]*", testo))


def parole_ref(ref):
    """Le parole del corpo a un dato ref git."""
    fuori = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, "paper/sections/"],
                           capture_output=True, text=True, cwd=RADICE, check=True).stdout.split()
    tot = 0
    for f in sorted(fuori):
        if not f.endswith(".tex"):
            continue
        t = subprocess.run(["git", "show", f"{ref}:{f}"],
                           capture_output=True, text=True, cwd=RADICE, check=True).stdout
        tot += conta(t)
    return tot


def parole_lavoro():
    """Le parole del corpo nel working tree, che e' lo stato che conta prima di un commit."""
    tot = 0
    for f in sorted(glob.glob(os.path.join(RADICE, "paper", "sections", "*.tex"))):
        tot += conta(io.open(f, encoding="utf-8").read())
    return tot


def autotest():
    """I casi di cui conosco gia' la risposta, nei due sensi: cio' che deve contare e cio' che no.

    Questa funzione ha trovato due difetti nel metodo prima che un suo numero entrasse in un
    documento: la lunghezza minima a due caratteri (che scartava «a») e le etichette, che
    contribuivano «sec» e «results» a ogni `\\label` del paper.
    """
    casi = [
        ("cinque parole di prosa danno 5",
         "The transport moves the number.", 5),
        ("una macro di prosa non conta, il suo argomento si",
         r"\textbf{two conditions} bound it", 4),
        ("un commento non conta",
         "visible words here\n% invisible commented words\nmore visible", 5),
        ("una parola di UNA lettera conta: «a» e' prosa",
         r"a share of models", 4),
        (r"un \% protetto non apre un commento (e 87.8 non e' una parola)",
         r"a share of 87.8\% of models", 5),
        ("un'etichetta non porta parole",
         "% tutto commentato\n\\label{sec:results}\n", 0),
        # «§V» non e' una parola: `\ref` si porta via l'argomento e `\S` e' un simbolo. Il
        # primo valore atteso che avevo scritto qui era 3, e sbagliavo io, non il codice.
        ("un rimando non porta parole, la prosa attorno si",
         r"\S\ref{sec:census} states it", 2),
        ("un ambiente non porta parole",
         "\\begin{itemize}\n\\item one thing\n\\end{itemize}", 2),
    ]
    print("  AUTOTEST del metodo di conteggio")
    esiti = []
    for eti, testo, atteso in casi:
        n = conta(testo)
        esiti.append(n == atteso)
        print(f"    {'ok  ' if n == atteso else 'FALLITO'} {eti:<52} -> {n} (atteso {atteso})")
    if not all(esiti):
        raise SystemExit("  il metodo di conteggio non rispetta le sue proprieta' (exit 2)")
    print()


if __name__ == "__main__":
    autotest()

    if "--serie" in sys.argv:
        righe = subprocess.run(["git", "log", "--format=%h %s", "--", "paper/sections/"],
                               capture_output=True, text=True, cwd=RADICE,
                               check=True).stdout.strip().split("\n")
        print("  il corpo a ogni commit che lo ha toccato, dal piu' recente")
        for r in righe[:20]:
            h = r.split()[0]
            print(f"    {parole_ref(h):>6}  {r[:76]}")
        raise SystemExit(0)

    if "--ref" in sys.argv:
        ref = sys.argv[sys.argv.index("--ref") + 1]
        ora, eti_ora = parole_ref(ref), f"ref {ref}"
    else:
        ora, eti_ora = parole_lavoro(), "working tree"

    print(f"  corpo ({eti_ora}): {ora} parole, metodo dichiarato nel docstring\n")
    print(f"  {'denominatore':<52}{'parole':>8}{'taglio':>10}")
    for ref, eti in (BASE_LETTA, BASE_PIU_LUNGA):
        base = parole_ref(ref)
        taglio = 100 * (base - ora) / base if base else float("nan")
        print(f"  {eti + ' (' + ref + ')':<52}{base:>8}{taglio:>9.1f}%")

    print("\n  COSA SI PUO' DICHIARARE")
    b_letta, b_lunga = parole_ref(BASE_LETTA[0]), parole_ref(BASE_PIU_LUNGA[0])
    t_letta = 100 * (b_letta - ora) / b_letta
    t_lunga = 100 * (b_lunga - ora) / b_lunga
    if t_lunga >= 25.0 > t_letta:
        print(f"    Il taglio e' {t_lunga:.1f}% rispetto al paper al suo massimo e {t_letta:.1f}%")
        print("    rispetto a quello che il revisore ha letto. La richiesta di R18 e' soddisfatta")
        print("    sul primo denominatore e non sul secondo, e la differenza fra i due e' il")
        print("    contenuto che R1-R17 hanno imposto di AGGIUNGERE. Si dichiarano entrambi:")
        print("    un solo numero, qui, sarebbe il numero scelto.")
    elif t_letta >= 25.0:
        print(f"    Il taglio e' {t_letta:.1f}% sul denominatore piu' severo dei due, quindi la")
        print("    richiesta di R18 e' soddisfatta senza bisogno di scegliere il denominatore.")
    else:
        print(f"    Il taglio e' {t_lunga:.1f}% sul massimo e {t_letta:.1f}% sullo stato letto:")
        print("    su nessuno dei due denominatori arriva al 25% che R18 chiede.")
