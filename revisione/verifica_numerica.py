#!/usr/bin/env python3
"""SPEC-32 — ogni valore cambiato dalla revisione, rigenerato dal suo script e confrontato col testo.

La regola del progetto e' che un numero in prosa tracci a un file, e la regola di questa revisione e'
piu' stretta: nessun valore si modifica a mano. Qui ogni riga dichiara la fonte, rilancia la fonte, e
cerca il valore nel manoscritto compilato.

CONTROLLO A RISPOSTA NOTA: l'ultima riga della tabella e' un valore che NON deve comparire (la vecchia
potenza di T6, 30,9%). Se la ricerca lo trovasse, il confronto starebbe passando per la ragione
sbagliata --- cioe' cercando in un testo che non e' quello del paper.

    python3 revisione/verifica_numerica.py [--tsv revisione/numeric_verification.tsv]
"""
import argparse, glob, os, re, shlex, subprocess, sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def testo_paper():
    fuori = []
    for f in sorted(glob.glob(os.path.join(RADICE, "paper", "sections", "*.tex"))) + \
             sorted(glob.glob(os.path.join(RADICE, "paper", "tables", "*.tex"))):
        fuori.append(re.sub(r"(?<!\\)%.*", "", open(f, errors="ignore").read()))
    return re.sub(r"\s+", " ", " ".join(fuori))


def esegui(cmd):
    """I comandi di VOCI sono letterali e non contengono metacaratteri di shell, quindi la shell
    non serve: si passa la lista di argomenti. Non era una vulnerabilita' --- `cmd` non arriva
    da argv, da stdin o dall'ambiente --- ma una shell che non serve e' superficie che non serve."""
    r = subprocess.run(shlex.split(cmd), capture_output=True, text=True, cwd=RADICE)
    return r.stdout + r.stderr


# (claim, comando che lo produce, regex sull'output dello script, valore atteso nel paper, deve comparire)
VOCI = [
    ("Table 6 — p congelato di T6", "python3 analysis/analyze_c2.py --results results/riraccolta",
     r"T6\s+.*?(0\.0155)", "0.0155", True),
    ("Table 6 — p congelato di T3", "python3 analysis/analyze_c2.py --results results/riraccolta",
     r"T3\s+.*?(0\.0181)", "0.0181", True),
    ("Table 6 — delta di T3", "python3 analysis/analyze_c2.py --results results/riraccolta",
     r"(-9\.83)pp", "-9.83", True),
    ("Table 6 — delta di T6", "python3 analysis/analyze_c2.py --results results/riraccolta",
     r"(-7\.94)pp", "-7.94", True),
    ("Table 6 — delta di T10, dallo script congelato", "python3 analysis/analyze_c2.py --results results/riraccolta",
     r"T10.*?(-4\.16)pp", "-4.16", True),
    ("Table 6 — soglia di Holm al rango 1", "python3 analysis/analyze_c2.py --results results/riraccolta",
     r"soglia=(0\.0050)", "0.0050", True),
    # La colonna MDE e' stata rimossa dopo il gauntlet: era una riscalatura costante
    # dell'ampiezza dell'intervallo, quindi non un secondo asse di evidenza. Ora si sorveglia
    # che NON torni, e che l'eterogeneita' resti leggibile dalle SD.
    ("Table 6 — la colonna MDE non deve tornare", None, None, "& MDE", False),
    ("Varianza — SD massima, che porta l'eterogeneita'", "python3 analysis/tabella_principale.py --varianza",
     r"(0\.2774)", "0.2774", True),
    ("Varianza — SD minima", "python3 analysis/tabella_principale.py --varianza",
     r"(0\.0117)", "0.0117", True),
    ("Censimento — coppie tentate", "python3 analysis/denominatore_roster.py", r"tentate\s*:\s*(21)", "21", True),
    ("Censimento — coppie rimosse", "python3 analysis/denominatore_roster.py", r"punteggio\s*:\s*(8)", "8 of 21", True),
    ("Censimento — cause distinte", "python3 analysis/denominatore_roster.py", r"cause distinte\s*:\s*(7)", "7 distinct causes", True),
    ("Censimento — modelli sondati", "python3 analysis/denominatore_roster.py", r"sondati\s*:\s*(11)", "11 distinct models", True),
    ("Turni — traiettorie al budget, ri-raccolta", "python3 analysis/saturazione_turni.py --braccio riraccolta",
     r"(68) al budget", "68", True),
    ("Turni — quota al budget", "python3 analysis/saturazione_turni.py --braccio riraccolta",
     r"\((1\.16)%\)", "1.16", True),
    ("Turni — cella gpt-oss/databricks/native", "python3 analysis/saturazione_turni.py --braccio riraccolta",
     r"gpt-oss-120b_databricks_native\t\d+\t[\d.]+\t[\d.]+\t[\d.]+\t(10\.02)", "10.0", True),
    ("T6 — turni usati, mediane", "python3 analysis/runtime_t6.py", r"turni usati\s+(6\.0)", "6.0", True),
    ("T6 — token in ingresso, databricks", "python3 analysis/runtime_t6.py", r"(20562)", "20{,}562", True),
    ("T6 — token in ingresso, bedrock", "python3 analysis/runtime_t6.py", r"(8853)", "8{,}853", True),
    ("T6 — token al primo turno", "python3 analysis/contesto_t6.py", r"token al 1o turno\s+(1263)", "1{,}263", True),
    ("Ri-raccolta — misurazioni valide", "python3 analysis/numeri_paper.py", r"misurazioni_valide\s+(5809)", "5{,}809", True),
    ("Varianza — quota di rumore di T3", "python3 analysis/numeri_paper.py", r"quota_rumore_T3\s+(0\.0051)", "0.5", True),
    ("Varianza — K_inf di T3", "python3 analysis/numeri_paper.py", r"k_inf_T3\s+(667)", "668", True),
    ("Ri-raccolta — segni concordi", "python3 analysis/tabella_riraccolta.py", r"segni concordi: (6)/8", "six of eight", True),
    ("Ri-raccolta — copertura IC95", "python3 analysis/tabella_riraccolta.py", r"copertura IC95: (7)/8", "seven of eight", True),
    # I due conteggi di soglia: l'MDE per contrasto contro la banda del falsificatore (3pp) e
    # contro l'MDE del disegno (4,87pp). Sono due domande diverse e il testo li teneva confusi.
    ("Banda ±3pp — contrasti che NON la risolvono", "python3 revisione/conta_soglie.py",
     r"oltre 3pp\s*:\s*(6)", "on six of the eight contrasts the interval is too wide", True),
    ("MDE del disegno 4,87pp — contrasti che lo superano", "python3 revisione/conta_soglie.py",
     r"oltre 4,87pp\s*:\s*(5)", "on five it is wider than the 4.87pp", True),
    ("CONTROLLO NEGATIVO — la vecchia potenza di T6 non deve comparire", None, None, "30.9", False),
    ("CONTROLLO NEGATIVO — la vecchia potenza di T3 non deve comparire", None, None, "21.0\\%", False),
    ("CONTROLLO NEGATIVO — il controllo stesso deve saper fallire", None, None, "5{,}809", True),
]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tsv"); a = ap.parse_args()
    testo = testo_paper()
    cache, righe, guasti = {}, [], 0
    for claim, cmd, pat, atteso, deve in VOCI:
        if cmd:
            if cmd not in cache:
                cache[cmd] = esegui(cmd)
            m = re.search(pat, cache[cmd], re.S)
            rigenerato = m.group(1) if m else "NON PRODOTTO"
        else:
            rigenerato = "n/d (controllo negativo)"
        # LETTERALE, non regex. La prima versione passava `atteso` a re.search e «8{,}853»
        # veniva letto come «8 ripetuto zero o piu' volte» + «853»: trovava «853» ovunque e
        # dichiarava MATCH senza che il numero ci fosse. Un controllo che passa per la ragione
        # sbagliata e' peggio di uno assente, e qui ne e' passato uno.
        presente = atteso in testo
        ok = (presente == deve) and (cmd is None or rigenerato != "NON PRODOTTO")
        if not ok:
            guasti += 1
        righe.append((claim, cmd or "-", rigenerato, atteso, "MATCH" if ok else "FALLITO"))

    intest = ("claim/table", "source script", "regenerated value", "manuscript value", "match")
    larg = max(len(r[0]) for r in righe)
    print("%-*s  %-18s %-10s %s" % (larg, "claim", "rigenerato", "atteso", "esito"))
    for c, s, r, m, e in righe:
        print("%-*s  %-18s %-14s %s" % (larg, c, r, m, e))
    print("\n  %d voci, %d guasti." % (len(righe), guasti))
    if a.tsv:
        with open(a.tsv, "w") as fh:
            fh.write("\t".join(intest) + "\n")
            for r in righe:
                fh.write("\t".join(r) + "\n")
    return 1 if guasti else 0


if __name__ == "__main__":
    sys.exit(main())
