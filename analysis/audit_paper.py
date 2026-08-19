#!/usr/bin/env python3
"""Cerca nel paper i numeri della raccolta che NON e' la base primaria.

PERCHE' ESISTE. Quando la ri-raccolta e' diventata la base primaria, ho aggiornato le sezioni
una per una e ho dichiarato finito. Un lettore ha poi trovato che la Conclusion diceva ancora
«5,805 measured trials», il determinismo «98--100% vs 13--24%» e le bande di Wilson
«15,6% vs 62,2%» — tre serie della raccolta precedente, in una sezione che riassume il paper.
Verificare per sezione trova i residui delle sezioni che guardi; verificare per NUMERO li trova
tutti.

    python3 analysis/audit_paper.py          # esce 1 se trova un residuo non dichiarato
    python3 analysis/audit_paper.py --lista  # stampa i valori attesi e chi li produce

COME DISTINGUE un residuo da una citazione deliberata. Il paper cita di proposito i valori
dell'originale quando confronta le due raccolte («0,1% e K=705 nell'originale, 0,5% e 668 nella
ri-raccolta»). Un residuo e' un valore vecchio che compare SENZA una di queste marche di
confronto nella stessa frase. La lista delle marche e' esplicita e va estesa quando il paper
introduce un modo nuovo di dire «questo e' il vecchio batch» — ed e' una lista, quindi cede alla
marca che non contiene: per questo il fallimento e' un avviso da leggere, non una licenza.
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
SEZIONI = os.path.join(RADICE, "paper", "sections")
MAIN = os.path.join(RADICE, "paper", "main.tex")

# (valore vecchio, valore nuovo, cosa e') — il vecchio non deve comparire senza una marca.
COPPIE = [
    (r"5\{,\}805",   "5{,}809",  "misurazioni valide"),
    (r"5,805",       "5,809",    "misurazioni valide (senza il separatore TeX)"),
    (r"5\{,\}747",   "5{,}756",  "run che hanno chiamato un tool"),
    (r"\b58 (?:runs|called)", "53", "run senza nessuna tool call"),
    (r"0\.110\b",    "0.113",    "pavimento del metrico"),
    (r"0\.636\b",    "0.638",    "media con tool"),
    (r"98--100",     "91--100",  "determinismo, haiku"),
    (r"13--24",      "20--24",   "determinismo, gpt-oss"),
    (r"13--16",      "20--22",   "determinismo, gpt-oss su un cloud"),
    (r"15\.6",       "24.4",     "banda di Wilson, llama su un endpoint"),
    (r"62\.2",       "66.7",     "banda di Wilson, llama sull'altro"),
    (r"10\.44",      "9.83",     "T3"),
    (r"8\.89",       "7.94",     "T6"),
    (r"6\.39",       "6.56",     "T1"),
    (r"0\.0177",     "0.0191",   "p minimo, serie Student"),
    (r"fifty-five",  "sixty-eight", "run che esauriscono il budget"),
    (r"factor of 77", "factor of 23.7", "rapporto fra le SD osservate"),
    (r"11\.88",      "11.59",    "MDE massimo"),
    (r"0\.15pp",     "0.49pp",   "MDE minimo"),
    (r"\bSix mechanisms\b", "six pre-collection mechanisms plus two conversational-state",
     "conteggio dei meccanismi del censimento"),
    # Aggiunte dopo che un lettore ha trovato le potenze vecchie NELL'ABSTRACT: le sorvegliavo
    # come contrasti (T1/T3/T6) e non come terna di potenze, quindi il pattern non le vedeva.
    (r"20\.3\\%", "21.0", "potenza di T3"),
    (r"25\.1\\%", "30.9", "potenza di T6"),
    (r"37\.4\\%", "35.8", "potenza di T1"),
    (r"factor of three", "factor of 23.7", "dispersione delle SD, nell'abstract"),
    (r"optimistic for six of the", "five of the eight", "contrasti che superano l'MDE pre-registrato"),
]

# Marche che rendono legittimo un valore vecchio: la frase sta confrontando le due raccolte.
MARCHE = [
    "original", "originally", "preceding chapter", "earlier chapter", "first batch",
    "before the re-collection", "replication", "re-collection", "in the original batch",
    "reported as", "whose value is",
]

# Valori che appartengono al capitolo PRECEDENTE e non a questo studio: non sono residui.
ESENTI = [
    (r"10\.4pp", "il calo misurato nel capitolo precedente, citato come tale"),
    (r"84\\%", "la quota di rumore del capitolo precedente"),
    (r"130\.7", "il ricalcolo del capitolo precedente con l'estimatore di qui"),
    (r"843 of 5\{,\}805", "l'esposizione alla concorrenza NELLA raccolta originale"),
]


def sezioni_compilate():
    """Solo i file che main.tex include davvero. Un file orfano ha gia' falsato un conteggio:
    10-artifact.tex era rimasto nel repo con sei occorrenze che il PDF non conteneva."""
    with open(MAIN, errors="ignore") as fh:
        nomi = re.findall(r"input\{sections/([^}]+)\}", fh.read())
    fuori = []
    for n in nomi:
        p = os.path.join(SEZIONI, n + ".tex")
        if os.path.isfile(p):
            fuori.append((n, p))
    return fuori


def frasi(testo):
    """Il testo spezzato in frasi, con il numero di riga di ciascuna: la marca di confronto vale
    per la frase, non per il file."""
    fuori, riga = [], 1
    for pezzo in re.split(r"(?<=\.)\s+|\n\n", testo):
        fuori.append((riga, pezzo))
        riga += pezzo.count("\n")
    return fuori


def esente(frase):
    return any(re.search(p, frase) for p, _ in ESENTI)


def marcata(frase):
    b = frase.lower()
    return any(m in b for m in MARCHE)


def sezioni_vuote():
    """Un titolo di sottosezione senza corpo. NASCE DA UN TAGLIO: spostando quattro paragrafi
    nell'artefatto ho lasciato i loro titoli, e il PDF ha compilato quattro promesse vuote in
    pagina due — una delle quali era «what this paper does not claim», cioe' esattamente la
    sezione che delimita la claim. Zero overfull, zero riferimenti irrisolti, e un lettore che
    vede il buco prima di leggere una riga di argomento: nessun controllo esistente lo prendeva
    perche' guardavano i numeri e la tipografia, non la struttura."""
    fuori = []
    for nome, percorso in sezioni_compilate():
        with open(percorso, errors="ignore") as fh:
            righe = fh.read().splitlines()
        for i, r in enumerate(righe):
            if not r.startswith("\\subsection"):
                continue
            j = i + 1
            while j < len(righe) and (not righe[j].strip()
                                      or righe[j].lstrip().startswith("%")
                                      or righe[j].startswith("\\label")):
                j += 1
            if j >= len(righe) or righe[j].startswith(("\\subsection", "\\section")):
                fuori.append((nome, i + 1, r[:70]))
    return fuori


def audit():
    residui = []
    for nome, percorso in sezioni_compilate():
        with open(percorso, errors="ignore") as fh:
            testo = fh.read()
        # via i commenti LaTeX: contengono di proposito la storia delle correzioni
        testo = re.sub(r"(?<!\\)%.*", "", testo)
        for riga, frase in frasi(testo):
            if esente(frase):
                continue
            for vecchio, nuovo, eti in COPPIE:
                if re.search(vecchio, frase) and not marcata(frase):
                    residui.append((nome, riga, eti, nuovo, " ".join(frase.split())[:100]))
    return residui


if __name__ == "__main__":
    if "--lista" in sys.argv:
        print("  I valori della base primaria, e chi li produce:\n")
        print("    analysis/numeri_paper.py            misurazioni, p, SD, MDE, pavimento, budget")
        print("    analysis/tabella_principale.py      i dieci contrasti e la varianza")
        print("    analysis/incertezza.py              le bande di Wilson")
        print("    analysis/validita.py                il determinismo per cella\n")
        for v, n, e in COPPIE:
            print(f"    {e:<52} vecchio {v:<18} nuovo {n}")
        sys.exit(0)

    residui = audit()
    vuote = sezioni_vuote()
    sez = len(sezioni_compilate())
    print(f"  audit di {sez} sezioni compilate, {len(COPPIE)} valori sorvegliati\n")
    if vuote:
        for nome, riga, titolo in vuote:
            print(f"  SEZIONE VUOTA  {nome}:{riga}  {titolo}")
        print(f"\n  {len(vuote)} titoli senza corpo. Un titolo-promessa vuoto si vede prima di")
        print("  qualunque argomento: o si scrive il corpo, o si toglie il titolo.")
        raise SystemExit(1)
    if not residui:
        print("  nessun numero della raccolta precedente compare senza una marca di confronto.")
        print("  NB: questo NON prova che ogni numero sia giusto — prova che nessuno dei valori")
        print("  sorvegliati e' rimasto. Un valore nuovo mai inserito in COPPIE non viene visto.")
        sys.exit(0)

    for nome, riga, eti, nuovo, frase in residui:
        print(f"  RESIDUO  {nome}:~{riga}  {eti}  (la base primaria dice {nuovo})")
        print(f"           {frase}")
    print(f"\n  {len(residui)} residui. Ognuno e' un numero della raccolta precedente in una frase")
    print("  che non dichiara di confrontare le due: o si aggiorna, o si aggiunge la marca.")
    sys.exit(1)
