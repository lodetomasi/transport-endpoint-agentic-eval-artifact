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
# La quarta voce di una coppia, quando c'e', e' il CONTESTO che la frase deve contenere perche' il
# match conti. Serve perche' un numero nudo collide: il 15,6% della decomposizione sul sottoinsieme
# non saturo di T6, entrato il 2026-08-19, coincide col vecchio valore della banda di Wilson, e la
# guardia segnalava come residuo una frase che non parla di Wilson. La correzione non e'
# un'eccezione per quella frase: e' che il confronto porti con se' la quantita' di cui parla.
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
    (r"15\.6",       "24.4",     "banda di Wilson, llama su un endpoint", r"Wilson|identical scores"),
    (r"62\.2",       "66.7",     "banda di Wilson, llama sull'altro", r"Wilson|identical scores"),
    (r"10\.44",      "9.83",     "T3"),
    (r"8\.89",       "7.94",     "T6"),
    (r"6\.39",       "6.56",     "T1"),
    (r"0\.0177",     "0.0191",   "p minimo, serie Student"),
    (r"fifty-five",  "sixty-eight", "run che esauriscono il budget"),
    (r"factor of 77", "factor of 23.7", "rapporto fra le SD osservate"),
    (r"11\.88",      "11.59",    "MDE massimo"),
    (r"0\.15pp",     "0.49pp",   "MDE minimo"),
    # La vecchia formula diceva «sei raggiungibili da una sonda, due no», e la revisione EMSE l'ha
    # sostituita con i tre livelli misurati (4 / 3 / 1). La guardia sorveglia la formula VECCHIA,
    # perche' e' quella che non deve tornare; la nuova si verifica con COERENTI, sotto.
    (r"[Ss]ix are reachable by a\s+pre-flight probe", "four answer an ordinary single-request check",
     "vecchia dicotomia sonda si/no del censimento"),
    # Aggiunte dopo che un lettore ha trovato le potenze vecchie NELL'ABSTRACT: le sorvegliavo
    # come contrasti (T1/T3/T6) e non come terna di potenze, quindi il pattern non le vedeva.
    (r"20\.3\\%", "21.0", "potenza di T3"),
    (r"25\.1\\%", "30.9", "potenza di T6"),
    (r"37\.4\\%", "35.8", "potenza di T1"),
    (r"factor of three", "factor of 23.7", "dispersione delle SD, nell'abstract"),
    (r"optimistic for six of the", "five of the eight", "contrasti che superano l'MDE pre-registrato"),
    # La revisione EMSE ha portato in tabella principale la serie CONGELATA: il p minimo della
    # famiglia e' 0,0155, non 0,0191 (che e' la serie esatta, ora sensibilita' in appendice).
    # Un paragrafo era rimasto sulla vecchia serie mentre la tabella sopra dava l'altra.
    (r"\$p\$ of \$0\.0191\$", "0.0155", "p minimo della famiglia, serie congelata",
     r"misses both|smallest \$p\$"),
]

# Marche che rendono legittimo un valore vecchio: la frase sta confrontando le due raccolte.
MARCHE = [
    "original", "originally", "preceding chapter", "earlier chapter", "first batch",
    "before the re-collection", "replication", "re-collection", "in the original batch",
    "reported as", "whose value is",
]

# FORMULE CHE NON DEVONO TORNARE, con la ragione. Non sono numeri vecchi: sono affermazioni che la
# revisione ha stabilito essere false o non sostenute, e che una riscrittura successiva potrebbe
# reintrodurre senza accorgersene. La guardia le cerca in TUTTE le sezioni, didascalie comprese.
VIETATE = [
    (r"achieved power", "potenza osservata: rimossa, e' una ri-espressione del p-value"),
    (r"least powered", "idem: ordina i contrasti per una quantita' che non aggiunge evidenza"),
    (r"& power &", "la colonna potenza della tabella principale"),
    (r"power determines what a \$p\$-value can mean", "la circolarita' potenza/p-value"),
    (r"designated (?:the )?primary basis in writing before it produced a row",
     "falso: la prima riga della ri-raccolta precede di 1h04m il file dei criteri"),
    (r"criteria frozen in advance", "i quattro criteri sono diagnostici pre-specificati, non congelati"),
    (r"no version of this contrast can hold the token count fixed",
     "piu' forte di cio' che l'evidenza sostiene"),
    (r"hand[s]? the model \\textbf\{2\.3", "i conteggi sono dichiarati dal provider, non cio' che il modello vede"),
    (r"neither party is malfunctioning", "adjudica una responsabilita' che l'evidenza non stabilisce"),
    (r"no party is at fault", "idem"),
    (r"turns & 12\.0 & 12\.0", "la colonna n_turns e' il budget configurato, non i turni usati"),
    (r"as a replication\b", "la raccolta originale non e' una replica progettata in anticipo"),
]

# COERENZE: una formula che DEVE comparire, e dove. Una guardia che sorveglia solo il vecchio non
# accorge se il nuovo e' sparito in una riscrittura.
COERENTI = [
    ("00-front", r"four are returned to an ordinary single-request capability check"),
    ("01-introduction", r"four are returned to an ordinary single-request capability check"),
    ("06-census", r"Four\s+mechanisms answer a single ordinary request"),
    ("09-conclusion", r"four answer an ordinary single-request\s+capability check"),
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


def nomi_di_file_md():
    """Il paper non nomina file .md. Un journal stampa prosa, non un albero di repository: un
    nome come `REDAZIONE.md` in una frase impegna il deposito a contenere quel file esatto con
    quel nome esatto, e la frase diventa falsa il giorno che il file si chiama altrimenti. La
    stessa informazione si scrive per FUNZIONE --- «il deposito porta una tabella delle
    sostituzioni» --- che resta vera qualunque sia il nome. Ne era rimasto uno, in Declarations.
    """
    fuori = []
    for nome, percorso in sezioni_compilate():
        for i, r in enumerate(open(percorso, encoding="utf-8").read().splitlines(), 1):
            if r.lstrip().startswith("%"):
                continue
            for m in re.finditer(r'\b[A-Za-z0-9_-]+\.md\b', r):
                fuori.append((nome, i, m.group(0)))
    return fuori


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


def vietate():
    """Le formule che la revisione ha stabilito essere false o non sostenute. Sorvegliate su TUTTE
    le sezioni, didascalie e note comprese: una riscrittura successiva le reintroduce con la
    stessa facilita' con cui il paper le conteneva."""
    fuori = []
    for nome, percorso in sezioni_compilate():
        testo = re.sub(r"(?<!\\)%.*", "", open(percorso, errors="ignore").read())
        for pat, perche in VIETATE:
            for m in re.finditer(pat, testo):
                # la negazione esplicita e' il modo corretto di nominarla
                intorno = testo[max(0, m.start() - 120):m.start()].lower()
                if any(n in intorno for n in ("not ", "never ", "no longer", "therefore not")):
                    continue
                fuori.append((nome, testo[:m.start()].count("\n") + 1, m.group(0)[:60], perche))
    return fuori


def apertura_conclusione():
    """La conclusione deve APRIRE col censimento, non con lo stato dell'emendamento.

    PERCHE' ESISTE. La conclusione apriva ricordando che due test su dieci erano stati
    implementati sotto emendamento e che la calibrazione ereditata veniva da un lotto difettoso.
    Sono due cose vere e gia' dichiarate altrove; in apertura di conclusione consegnano a un
    revisore la propria obiezione prima del risultato. Questa guardia guarda le prime 60 parole."""
    testo = re.sub(r"(?<!\\)%.*", "", open(os.path.join(SEZIONI, "09-conclusion.tex"),
                                          errors="ignore").read())
    corpo = re.sub(r"\\(section|label)\{[^}]*\}", " ", testo)
    corpo = re.sub(r"\\textbf\{|\}", " ", corpo)
    apertura = " ".join(corpo.split()[:60]).lower()
    guasti = []
    if not re.search(r"endpoint|mechanism|remove", apertura):
        guasti.append("l'apertura non nomina il censimento")
    for vietato in ("amendment", "validity flag", "calibration", "holm"):
        if vietato in apertura:
            guasti.append(f"l'apertura contiene «{vietato}»")
    return guasti


def coerenti_mancanti():
    """Il verso opposto: una formula che DEVE esserci e non c'e' piu'. Senza questo, la guardia
    passa quando il testo che deve dire una cosa non la dice affatto."""
    fuori = []
    mappa = dict(sezioni_compilate())
    for nome, pat in COERENTI:
        percorso = mappa.get(nome)
        if not percorso:
            fuori.append((nome, "sezione assente"))
            continue
        # Spazi normalizzati e case-insensitive: la coerenza che si vuole e' semantica. Una
        # guardia sensibile a dove cade l'a-capo chiede di spostare un ritorno a capo per farla
        # tacere, che e' il contrario del suo scopo. Nella prima versione lo era in entrambi i
        # sensi, e ha segnalato come assente una frase presente.
        testo = re.sub(r"\s+", " ", open(percorso, errors="ignore").read())
        if not re.search(re.sub(r"\\s\+", " ", pat), testo, re.I):
            fuori.append((nome, pat))
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
            for coppia in COPPIE:
                vecchio, nuovo, eti = coppia[0], coppia[1], coppia[2]
                contesto = coppia[3] if len(coppia) > 3 else None
                if not re.search(vecchio, frase) or marcata(frase):
                    continue
                if contesto and not re.search(contesto, frase, re.I):
                    continue    # il numero c'e' ma la frase parla d'altro
                residui.append((nome, riga, eti, nuovo, " ".join(frase.split())[:100]))
    return residui


if __name__ == "__main__":
    if "--lista" in sys.argv:
        print("  I valori della base primaria, e chi li produce:\n")
        print("    analysis/numeri_paper.py            misurazioni, p, SD, MDE, pavimento, budget")
        print("    analysis/tabella_principale.py      i dieci contrasti e la varianza")
        print("    analysis/incertezza.py              le bande di Wilson")
        print("    analysis/validita.py                il determinismo per cella\n")
        for c in COPPIE:
            ctx = f"  [contesto: {c[3]}]" if len(c) > 3 else ""
            print(f"    {c[2]:<52} vecchio {c[0]:<18} nuovo {c[1]}{ctx}")
        sys.exit(0)

    residui = audit()
    vuote = sezioni_vuote()
    md = nomi_di_file_md()
    viet = vietate()
    manc = coerenti_mancanti()
    apert = apertura_conclusione()
    sez = len(sezioni_compilate())
    print(f"  audit di {sez} sezioni compilate, {len(COPPIE)} valori sorvegliati, "
          f"{len(VIETATE)} formule vietate, {len(COERENTI)} coerenze, apertura della conclusione\n")
    if viet:
        for nome, riga, testo, perche in viet:
            print(f"  FORMULA VIETATA  {nome}:~{riga}  \"{testo}\"")
            print(f"                   {perche}")
        raise SystemExit(1)
    if manc:
        for nome, pat in manc:
            print(f"  COERENZA PERSA   {nome}  manca: {pat}")
        print("\n  Una formula che la revisione ha stabilito e' sparita in una riscrittura.")
        raise SystemExit(1)
    if apert:
        for g in apert:
            print(f"  APERTURA         09-conclusion  {g}")
        print("\n  La conclusione deve aprire col risultato, non con lo stato procedurale.")
        raise SystemExit(1)
    if md:
        for nome, riga, f in md:
            print(f"  NOME DI FILE  {nome}:{riga}  {f}")
        print(f"\n  {len(md)} nomi di file .md nella prosa. Un journal stampa prosa, non un albero")
        print("  di repository: la stessa informazione si scrive per funzione, che resta vera")
        print("  qualunque sia il nome del file.")
        raise SystemExit(1)
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
