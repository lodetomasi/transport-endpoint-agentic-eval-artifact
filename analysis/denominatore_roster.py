#!/usr/bin/env python3
"""Il denominatore del roster: quante coppie modello-piattaforma abbiamo tentato, e quante sono
state rimosse prima di produrre un punteggio.

PERCHE'. Il censimento riporta ESISTENZA — otto meccanismi, ciascuno con il messaggio verbatim
dell'endpoint che l'ha prodotto — e il paper dichiara che non sono un tasso. E' corretto e non
basta: senza un denominatore un lettore non sa se otto meccanismi su dieci tentativi o otto su
mille, e la differenza cambia come si legge tutto il resto. Un denominatore del NOSTRO roster
esiste, e' calcolabile, e non e' un tasso di popolazione: e' l'incidenza dentro il campione che
abbiamo effettivamente provato a costruire.

PERCHE' E' UN'ENUMERAZIONE E NON UNA QUERY. Su una delle due piattaforme l'SCP nega
`ListFoundationModels`, `ListInferenceProfiles` e `ListCustomModels`: si invoca ma non si enumera.
Il roster si dichiara per enumerazione esplicita, non per regola, ed e' esattamente il fatto di
riproducibilita' che il paper riporta. Questo file E' quella dichiarazione, in forma eseguibile.

COSA NON E'. Non e' un tasso di incidenza su modelli o piattaforme in generale, e non ne calcoliamo
uno. Il roster e' assemblato per convenienza --- i modelli che i due cloud dell'autore servivano,
piu' quelli provati per costruire il campione --- non campionato. Chi vuole un tasso deve sondare un
roster campionato, ed e' la misura che manca (§7.5).

    python3 analysis/denominatore_roster.py
"""
import sys

# (modello, piattaforma, esito, meccanismo)
# esito: "misurato" = ha prodotto punteggi; "rimosso" = niente punteggio prima di produrne uno.
# Ogni riga «rimosso» ha una evidenza verbatim nel censimento del deposito.
ROSTER = [
    ("gpt-oss-120b",      "Databricks", "misurato", None),
    ("gpt-oss-120b",      "Bedrock",    "misurato", None),
    ("llama-3.3-70b",     "Databricks", "misurato", None),
    ("llama-3.3-70b",     "Bedrock",    "misurato", None),
    ("claude-haiku-4-5",  "Databricks", "misurato", None),
    ("claude-haiku-4-5",  "Bedrock",    "misurato", None),
    ("claude-sonnet-4-5", "Databricks", "misurato", None),
    ("claude-sonnet-4-5", "Bedrock",    "misurato", None),
    ("claude-opus-4-5",   "Databricks", "misurato", None),
    ("claude-opus-4-5",   "Bedrock",    "misurato", None),
    ("llama-3.1-8b",      "Databricks", "misurato", None),
    ("llama-3.1-8b",      "Bedrock",    "misurato", None),
    ("gpt-oss-20b",       "Bedrock",    "misurato", None),
    # --- rimossi prima di produrre un punteggio -----------------------------------------
    ("gemma-3-12b",       "Databricks", "rimosso", "rifiuto di protocollo"),
    ("llama-3.1-8b",      "Azure",      "rimosso", "deprecazione"),
    ("gpt-oss-20b",       "Azure",      "rimosso", "quota inesistente"),
    ("claude-sonnet-4",   "Bedrock",    "rimosso", "disuso"),
    ("claude-opus-4-1",   "Bedrock",    "rimosso", "disuso"),
    ("llama-4-maverick",  "Bedrock",    "rimosso", "giurisdizione"),
    ("llama-3.3-70b",     "Azure",      "rimosso", "chiamate parallele"),
    # Questa rimozione e' reale --- nessun punteggio --- ma la sua causa NON e' uno degli otto
    # meccanismi nominati: il paper la classifica fra i «quattro casi ulteriori» del deposito
    # («un modello comparabile su un cloud, rifiutato da un secondo, funzionante su un terzo»).
    # Il primo conteggio la promuoveva a meccanismo e faceva nove: il controllo a risposta nota
    # l'ha preso, ed e' la ragione per cui il controllo esiste.
    ("gpt-oss-20b",       "Databricks", "rimosso", "canale di ragionamento (caso ulteriore)"),
]

# I sei meccanismi NOMINATI che rimuovono una riga del roster. L'elenco e' quello del paper, e
# serve a distinguere «una coppia e' stata rimossa» da «e' stata rimossa da uno degli otto».
MECCANISMI_NOMINATI = [
    "rifiuto di protocollo", "deprecazione", "quota inesistente",
    "disuso", "giurisdizione", "chiamate parallele",
]

# I due meccanismi che non rimuovono un modello dal ROSTER: si manifestano dentro il braccio
# confermativo, e costano un lotto e delle run invece di una riga della tabella.
DENTRO_IL_BRACCIO = [
    "configurazione dei tool non esprimibile",   # il settimo
    "l'endpoint rifiuta l'output del modello che serve",  # l'ottavo
]

if __name__ == "__main__":
    tentate = len(ROSTER)
    rimosse = [r for r in ROSTER if r[2] == "rimosso"]
    misurate = [r for r in ROSTER if r[2] == "misurato"]
    modelli = sorted({r[0] for r in ROSTER})
    piattaforme = sorted({r[1] for r in ROSTER})
    mecc_roster = sorted({r[3] for r in rimosse})
    mecc_nominati = sorted({r[3] for r in rimosse if r[3] in MECCANISMI_NOMINATI})
    altri_casi = [r for r in rimosse if r[3] not in MECCANISMI_NOMINATI]

    print("  IL DENOMINATORE DEL NOSTRO ROSTER, dichiarato per enumerazione\n")
    print(f"  coppie modello-piattaforma tentate      : {tentate}")
    print(f"  hanno prodotto punteggi                 : {len(misurate)}")
    print(f"  rimosse prima di produrre un punteggio  : {len(rimosse)}"
          f"  ({100*len(rimosse)/tentate:.0f}% delle tentate)")
    print(f"  cause distinte                          : {len(mecc_roster)}")
    print(f"    di cui fra gli otto meccanismi nominati: {len(mecc_nominati)}")
    print(f"    altri casi, nel deposito               : {len(altri_casi)}")
    print(f"  modelli distinti sondati                : {len(modelli)}")
    print(f"  piattaforme distinte                    : {len(piattaforme)}  {piattaforme}")
    print(f"\n  piu' {len(DENTRO_IL_BRACCIO)} meccanismi che non rimuovono una riga del roster ma")
    print(f"  colpiscono dentro il braccio confermativo, per un totale di "
          f"{len(mecc_nominati) + len(DENTRO_IL_BRACCIO)} nominati.")

    print("\n  le rimozioni, una per riga")
    for m, p, _, mec in rimosse:
        print(f"    {m:<20}{p:<12}{mec}")

    print("\n  COSA QUESTO NUMERO E', E COSA NO")
    print(f"    E': l'incidenza dentro il roster che abbiamo tentato — {len(rimosse)} coppie su")
    print(f"    {tentate}, per {len(mecc_roster)} cause distinte di cui {len(mecc_nominati)} fra gli otto")
    print("    meccanismi nominati, ognuna con l'evidenza verbatim dell'endpoint.")
    print("    NON E': un tasso su modelli o piattaforme in generale. Il roster e' assemblato per")
    print("    convenienza, non campionato, e un tasso richiede un roster campionato — la misura")
    print("    che manca e che dichiariamo come lavoro futuro specificato.")

    print("\n  CONTROLLO a risposta nota")
    ok = []
    ok.append(len(modelli) == 11)
    print(f"    i modelli distinti sono 11, come dichiara l'abstract: "
          f"{'ok' if len(modelli) == 11 else f'FALLITO ({len(modelli)})'}")
    tot_mecc = len(mecc_nominati) + len(DENTRO_IL_BRACCIO)
    ok.append(tot_mecc == 8)
    print(f"    i meccanismi documentati sono 8, come dichiara il paper: "
          f"{'ok' if tot_mecc == 8 else f'FALLITO ({tot_mecc})'}")
    quattro = {m for m, p, e, _ in ROSTER if e == "misurato"}
    ok.append(len({"gpt-oss-120b", "llama-3.3-70b", "claude-haiku-4-5", "claude-sonnet-4-5"} - quattro) == 0)
    print(f"    i quattro modelli dei bracci pieni sono fra i misurati: "
          f"{'ok' if ok[-1] else 'FALLITO'}")
    ok.append(all(r[3] for r in rimosse))
    print(f"    ogni rimozione porta un meccanismo: {'ok' if ok[-1] else 'FALLITO'}")
    ok.append(all(r[3] is None for r in misurate))
    print(f"    nessuna riga misurata porta un meccanismo: {'ok' if ok[-1] else 'FALLITO'}")
    if not all(ok):
        raise SystemExit("  il roster non rispetta le sue proprieta'")
