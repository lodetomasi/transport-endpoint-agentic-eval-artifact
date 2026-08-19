# C2 — L'interfaccia dei tool è un parametro libero

Secondo capitolo di un programma di dottorato sulla validità sperimentale delle valutazioni
agentiche. Il primo ha misurato che il vantaggio agentico è una proprietà di quanto contesto
si nega al baseline. Questo generalizza da **confondimento del baseline** a **confondimento
dell'infrastruttura**.

> **Il cap sposta un numero. Il trasporto cancella un modello dal campione.**

Effetto di selezione, non bias di misura: un bias lo si delimita, una selezione no, perché il
modello assente non ha una riga da correggere.

## La domanda, in una riga

Quanto del numero che una valutazione agentica pubblica dipende da **come parla ai tool**, e
non dal modello?

Nel primo capitolo Claude Haiku 4.5 ha perso **10,4 punti** di pass-rate passando dal function
calling nativo a un protocollo testuale. Su una sola infrastruttura, e quel numero ha due
letture indistinguibili: è una proprietà del **modello**, o dello **shim** di quel provider?

Con un endpoint solo non è rispondibile — modello e infrastruttura sono perfettamente confusi.
Lo stesso modello su due cloud le separa in modo binario.

**Che il trasporto sposti il numero è già pubblicato**: la Berkeley Function-Calling Leaderboard
riporta per ogni modello le due varianti, e GPT-4-1106-Preview fa 85,65 in modalità Prompt
contro 79,65 in FC — il testo **vince** di 6pp, nella direzione opposta al nostro seme. Quello
che nessuno incrocia è il trasporto con **l'identità del cloud gestito a parità di pesi**, e
nessuno tratta la cancellazione di un modello come effetto di selezione di prima classe. La
claim è stata ristretta a questo il 2026-08-15
([emendamento 04](registro/EMENDAMENTO-04-claim-dopo-bfcl.md)).

## Il disegno

| | |
|---|---|
| modelli | `gpt-oss-120b` · `llama-3.3-70b` · `claude-haiku-4-5` · `claude-sonnet-4-5` |
| infrastrutture | Databricks (Azure) · Bedrock (AWS) — due cloud, non due facciate |
| trasporti | tool nativi · protocollo `TOOL_CALL:` nel testo |
| celle | 4 × 2 × 2 = **16**, da 45 binari × 8 run |
| costo previsto | **$124,88** su un tetto dichiarato di **$200** ([emendamento 01](registro/EMENDAMENTO-01-tetto.md)) |

Le celle a **pesi aperti** sono la prova pulita: ciascun cloud ospita davvero quei pesi, quindi
un risultato nullo significa che le infrastrutture concordano, non che sono la stessa con due
nomi. Le celle Anthropic funzionano da controllo negativo.

Era previsto anche un **braccio esplorativo** su un terzo cloud, Azure
([emendamento 02](registro/EMENDAMENTO-02-braccio-azure.md)), fuori dalla famiglia dei dieci
test. **Non ha dati validi**: le sue 238 righe erano nel lotto invalidato per i tre canali del
nome dell'algoritmo e non sono state riraccolte
([nota](results/VALIDITA-BRACCIO-AZURE-2026-08-15.md)). `m` resta 10 e nulla cambia per i dieci
test, ma il braccio va dichiarato assente invece che annunciato.

## Cosa è congelato, e quando

La pre-registrazione **e lo script di analisi** sono congelati insieme, prima della prima riga
di dati. È la metà che il capitolo precedente aveva lasciato aperta: congelare le ipotesi e
scrivere l'analisi a dati visti lascia intatta tutta la libertà che la pre-registrazione
doveva chiudere — quale test, su quale sottoinsieme, con quale esclusione.

```bash
./verifica_hash.sh     # 6 file, e pretende che una successione NOMINI il file divergente
```

Ogni modifica a un file congelato ha un `registro/SUCCESSIONE-NN-*.md` scritto **prima**, con l'effetto
isolato sulla misura e l'hash precedente conservato.

## Riprodurre

Servono Python 3.9+, Docker (la compilazione dei candidati gira in un container `linux/amd64`)
e le credenziali dei due cloud. Nessuna credenziale è in questo repository.

```bash
# Databricks: un profilo del CLI          Bedrock: un profilo AWS
export DATABRICKS_PROFILE=<profilo>
export AWS_PROFILE=<profilo> AWS_REGION=us-east-1

python3 src/raccogli_c2.py --dry-run                       # i comandi, senza eseguirli
python3 src/raccogli_c2.py --cella gpt-oss-120b/databricks/native
python3 src/raccogli_c2.py --solo-infra databricks         # una partizione, per parallelizzare

nohup "$(pwd)/sorveglia_costi.sh" &                        # ferma al tetto, non commenta
```

Il driver fa un **preflight** per provider prima di qualunque cella: le credenziali dei due
cloud sono meccanismi diversi e nessuno si annuncia mancante finché non lo usi.

## Dove si guarda

| domanda | comando |
|---|---|
| a che punto è la raccolta | `./stato.sh` |
| quanto è stato speso | `./check_cost.sh` — per riga valida, `exit 2` oltre il tetto |
| quali celle sono corte, e di quanto | `python3 src/completa_celle.py` |
| i file congelati sono intatti | `./verifica_hash.sh` |
| cosa dicono i dati | `python3 analysis/analyze_c2.py` — si **rifiuta** sui bracci parziali |
| quanta potenza ha il disegno | `python3 analysis/potenza.py` |

`check_cost.sh` risponde *quanto è stato speso*; `sorveglia_costi.sh` **impedisce** che si
spenda oltre. Il primo è un referto.

## Cosa è stato fatto, quando, e perché

[`PERCORSO.md`](PERCORSO.md) — la catena datata: le decisioni, i difetti trovati con quanto sarebbero costati, le due cose che il gauntlet ha cambiato, e cosa resta aperto. Nel paper ne resterà una frase per voce; qui c'è la genealogia con l'evidenza.

## La mappa

```
PREREGISTRAZIONE.md      ipotesi, falsificatori, famiglia di 10 test, m fisso
HASH-CONGELATI.md        i 6 file congelati e le successioni
SUCCESSIONE-NN-*.md      ogni modifica a un file congelato, con l'effetto isolato
research/CENSIMENTO.md   quali modelli ogni infrastruttura serve, e quali cancella
analysis/analyze_c2.py   scritta prima dei dati
analysis/potenza.py      il calcolo di potenza, rieseguibile
src/harness/             il ciclo dell'agente, entrambi i trasporti
src/raccogli_c2.py       le 16 celle
src/completa_celle.py    il deficit per binario, e la catena delle riesecuzioni
configs/pricing.json     17 tariffe, ciascuna con la fonte; le stime sono marcate
results/                 CSV per cella + traiettorie per-turno. **Append-only.**
```

## Due cose che il lettore deve sapere prima dei risultati

**Pass-rate è un lower bound**, mai equivalenza semantica, e si riporta come tale ovunque.

**K=45 non alimenta un test di equivalenza.** La banda del falsificatore (±3pp) richiede
K = 99–119; a K=45 l'MDE è 4,87pp. Le ipotesi sono disgiuntive di conseguenza, e un esito
nullo si riporta come «l'IC esclude effetti sopra 4,9pp» — mai come «nessuna differenza».
È dichiarato nella pre-registrazione, non scoperto a valle.

## Sei meccanismi che tolgono un modello da una valutazione

Nessuno cercato: sono emersi provando a costruire il campione. Rifiuto di protocollo,
deprecazione, quota inesistente, disuso, giurisdizione, **chiamate parallele** — con
l'evidenza verbatim di ciascuno in `research/CENSIMENTO.md`.

Il sesto è il solo che **un preflight non può prevenire**: il censimento lo dichiara sano,
e la cella muore raccogliendo, quando il modello *decide* di chiamare due tool insieme.

Il caso più stretto è `gpt-oss-20b`: non comparabile su Databricks, rifiutato da Azure,
funzionante con tool nativo su Bedrock. **Stesso modello, tre infrastrutture, tre verdetti.**
