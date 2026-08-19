#!/usr/bin/env python3
"""Ogni modifica che la revisione dichiara di aver fatto, verificata sul testo.

PERCHE' ESISTE. `str.replace` restituisce la stringa intatta quando il bersaglio non c'e', e non
solleva. In questa revisione e' successo due volte: una riscrittura di §5.2 e l'intestazione di
§8 sono state annunciate come fatte e non erano avvenute --- il bersaglio differiva per
un'interruzione di paragrafo. Uno script che stampa «riformulata» dopo un replace a vuoto e'
esattamente il difetto che questo capitolo studia: un controllo che passa per la ragione
sbagliata.

Due elenchi: cio' che deve essere SPARITO e cio' che deve essere PRESENTE. Il secondo esiste
perche' una guardia sul solo vecchio testo non si accorge se il nuovo e' stato perso in una
riscrittura successiva.

    python3 revisione/modifiche_dichiarate.py
"""
import glob, os, re, sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (sezione, frammento, etichetta) — confronto a spazi normalizzati, come il testo composto.
SPARITE = [
    ("05-results", "achieved power", "potenza osservata"),
    ("05-results", "least powered", "i tre contrasti meno potenti"),
    ("09-conclusion", "achieved power", "potenza in conclusione"),
    ("01-introduction", "if the difference persists it", "attribuzione causale all'endpoint"),
    ("05-results", "points away from hardware", "diagnosi causale di T6"),
    ("05-results", "hand the model 2.3 times", "token consegnati al modello"),
    ("08-threats", "no version of this contrast can hold", "assoluto sul trasporto"),
    ("06-census", "neither party is malfunctioning", "M8, ontologia della colpa"),
    ("06-census", "no party is at fault", "M8, ontologia della colpa (2)"),
    ("06-census", "the client sends a valid request", "M8, ontologia della colpa (3)"),
    ("08-threats", "criteria frozen in advance", "criteri «congelati»"),
    ("08-threats", "not designated primary before it produced a row", "precedenza, fuori da §8"),
    ("08-threats", "not outcome-independent", "non indipendente, fuori da §8"),
    ("08-threats", "4h31m", "cronologia forense, fuori da §8"),
    ("08-threats", "which we state rather than round past", "meta-commento sull'arrotondamento"),
    ("08-threats", "what we did about it", "voce d'autore nell'intestazione"),
    ("08-threats", "an artifact reviewer would find anyway", "auto-consapevolezza sull'intestazione"),
    ("08-threats", "carries both cautions", "registro difensivo"),
    ("05-results", "as a replication", "la raccolta originale come replica"),
    ("04-design", "no hypothesis, test or comparison is added", "nessuna ipotesi aggiunta"),
    ("04-design", "44 binaries of 45", "la cella a 44 binari"),
    ("05-results", "turns & 12.0 & 12.0", "i turni configurati come misura"),
    ("05-results", "$p$ of $0.0191$", "p della serie sbagliata"),
    ("05-results", "was not verifiable", "calibrazione non verificabile"),
    ("05-results", "had no way", "il designer senza modo di sapere"),
    ("05-results", "we were not looking for", "risultato non cercato"),
    ("05-results", "no tokenizer for the served model", "giustificazione-per-limite sui token"),
    ("06-census", "upper bound rather than a measurement", "caveat su M1 al posto della claim"),
    ("07-discussion", "the field we can least fully satisfy", "il campo meno soddisfatto"),
    ("12-appendice", "Neither timestamp is verifiable by a", "editoriale sulla provenienza"),
    ("05-results", "evidence against call", "RQ5 come eliminazione causale"),
    ("07-discussion", "not a null finding", "titolo che sembra recuperare il nullo"),
    ("00-front", "carry the finding", "contrasti presentati come reperti"),
    ("08-threats", "carry the result", "contrasti presentati come reperti, in §8"),
    ("00-front", "would have let it resolve", "formulazione retrospettiva nell'abstract"),
    ("09-conclusion", "carry the finding", "contrasti presentati come reperti, in conclusione"),
    ("08-threats", "843 of 5", "dettaglio forense sull'affollamento"),
    ("05-results", "whatever its size", "RQ5 senza il tetto aritmetico"),
    ("00-front", "two properties usually assumed", "cornice troppo larga sul contributo 2"),
    ("07-discussion", "no counterpart in current checklists", "novita' della checklist"),
    ("07-discussion", "Variance components can be apparatus-specific", "proposizione sulla varianza"),
    ("07-discussion", "checklists we did not read", "meta-commento sulla checklist"),
    ("02-related", "nothing for anyone to fix", "aforisma sulla tassonomia"),
    ("02-related", "we assert to be low and did not measure", "claim di prevalenza"),
    ("05-results", "winner's curse", "aforisma"),
    ("01-introduction", "harder to escape", "aforisma (2)"),
    ("01-introduction", "What this paper does not claim", "titolo interamente negativo"),
    ("03-method", "rather than let a reader find", "meta-commento nel metodo"),
    ("06-census", "we state each with its own denominator and never mix them", "meta sui denominatori"),
    ("06-census", "the asymmetry belongs in the open", "meta sull'asimmetria"),
]

PRESENTI = [
    ("05-results", "poorly identified at the boundary", "T7 e T8 al bordo"),
    ("05-results", "provider-reported input-token accounting difference", "token, decisione B"),
    ("05-results", "turns used (median)", "turni misurati in tabella"),
    ("05-results", "68 reach the turn budget", "saturazione calcolata"),
    ("05-results", "our prompted-text protocol", "scope del trasporto"),
    ("05-results", "existence demonstration", "nondeterminismo esistenziale"),
    ("05-results", "on six of the eight contrasts the interval is too wide", "soglia ±3pp"),
    ("06-census", "under the evaluated configuration", "limite di configurazione"),
    ("06-census", "Four mechanisms answer a single ordinary request", "rilevabilita' 4/3/1"),
    ("07-discussion", "interaction budget", "budget dei turni nella checklist"),
    ("07-discussion", "not explicit in that checklist", "novita' limitata alla fonte"),
    ("08-threats", "by construction, not observed absent", "l'argomento portante di §8"),
    ("09-conclusion", "Six mechanisms remove a model-platform pair", "conclusione apre col censimento"),
    ("12-appendice", "Provenance of the re-collection", "appendice della provenienza"),
    ("06-census", "is the probe that reaches the mechanism", "colonna det. come sonda usata"),
    ("07-discussion", "it ships the decompilation outputs themselves", "il deposito consegna gli output"),
    ("05-results", "at most \\textbf{26\\%} and \\textbf{13\\%}", "il tetto aritmetico di RQ5"),
    ("05-results", "clamped in more than half of the bootstrap", "soglia esplicita di esclusione T7/T8"),
    ("05-results", "Two readings of that ratio", "ambiguita' tokenizer/contenuto su T6"),
    ("05-results", "individually significant at the conventional", "i due percentili concessi"),
    ("06-census", "easiest of the three level-2 mechanisms", "M7 documentato dal vendor"),
    ("02-related", "11 of 31 endpoints serving distributions", "Model Equality Testing citato"),
    ("03-method", "no per-model result was computed or read", "cosa fu ispezionato prima di T9/T10"),
    ("00-front", "assembled rather than sampled", "vincolo di 8/21 in linea nell'abstract"),
]


def testi():
    fuori = {}
    for f in glob.glob(os.path.join(RADICE, "paper", "sections", "*.tex")):
        nome = os.path.basename(f)[:-4]
        fuori[nome] = re.sub(r"\s+", " ", re.sub(r"(?<!\\)%.*", "", open(f, errors="ignore").read()))
    return fuori


def main():
    T = testi()
    guasti = []
    larg = max(len(e) for _, _, e in SPARITE + PRESENTI)
    for sez, fr, eti in SPARITE:
        male = fr in T.get(sez, "")
        guasti += [(eti, sez, "ANCORA PRESENTE")] if male else []
        print(f"  {'GUASTO' if male else 'ok    '}  {eti:<{larg}}  {sez}")
    for sez, fr, eti in PRESENTI:
        male = fr not in T.get(sez, "")
        guasti += [(eti, sez, "MANCA")] if male else []
        print(f"  {'GUASTO' if male else 'ok    '}  {eti:<{larg}}  {sez}")
    print(f"\n  {len(SPARITE)} rimozioni e {len(PRESENTI)} inserimenti dichiarati, {len(guasti)} non verificati.")
    for eti, sez, come in guasti:
        print(f"    {come}: {eti} ({sez})")
    return 1 if guasti else 0


if __name__ == "__main__":
    sys.exit(main())
