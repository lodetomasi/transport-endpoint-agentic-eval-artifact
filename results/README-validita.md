# Registro di validità — `results/`

`results/` è **append-only** (IR-5). Un file invalidato non si cancella: si annota qui con la
ragione, il lotto e il ricalcolo, e resta nel deposito.

Vale anche per i CSV che contengono solo rifiuti di piattaforma. Un braccio non eseguibile non
è un braccio mancante — è un risultato di questo studio, e il messaggio verbatim dell'endpoint
è il dato.

| file | data | stato | ragione |
|---|---|---|---|
| **tutto il lotto** (14 CSV + 25 cartelle di traiettorie) | 2026-08-14 | **invalidato, raccolta ripartita da zero** | Il nome dell'algoritmo raggiungeva il modello da tre canali: il prompt, la sezione `.strtab` via `list_strings` (nome del sorgente **e nomi delle funzioni**), e l'output del programma. I primi due corretti, il terzo dichiarato come limite del corpus. **Ricalcolo**: 2.390 misurazioni e $17,08 invalidati; l'analisi vedeva 6 celle e ora ne vede 0. Dettaglio in [`invalidati/lotto-nome-algoritmo/`](invalidati/lotto-nome-algoritmo/), causa in [EMENDAMENTO-03](../registro/EMENDAMENTO-03-nome-algoritmo.md). |
| `c2_gpt-oss-120b_bedrock_native*.csv` | 2026-08-14 | **invalidata e riraccolta** | 29 righe su 453 portano `ValidationException: The toolConfig field must be defined when using toolUse and toolResult content blocks`. Sono `infra_failure=True` e la regola di qualità già le esclude, quindi **non entrano in nessuna media**. Il problema è chi SOPRAVVIVE: una traiettoria arriva al turno finale con `toolUse` in storia solo se non ha già sottomesso via tool, quindi le run che passano sono esattamente quelle che hanno sottomesso **prima** del turno finale — un secondo effetto di selezione dentro l'asse che lo studio misura. Causa e correzione in [SUCCESSIONE-05](../registro/SUCCESSIONE-05-toolconfig-converse.md). **Ricalcolo**: il lotto è stato spostato in `invalidati/` — non cancellato — e la cella riraccolta da zero col client corretto, 360 run, ~$1,20. Un top-up avrebbe sommato run non distorte a un campione distorto, e la miscela non si separa a valle. Prima dello spostamento l'analisi vedeva la cella con 424 run valide su una base selezionata; dopo, 0 su 45 binari carenti, cioè il deficit pieno. |
| `results.csv` | 2026-08-13 | **fuori dalla raccolta** | Sola intestazione, zero righe. Prodotto collaudando il runner a `--runs 0` prima che la raccolta iniziasse, quindi non contiene misurazioni. Resta qui perché `results/` è append-only e la regola non ammette eccezioni decise caso per caso: è precisamente quando si giudica «questo non conta» che si apre la porta. Nessuna analisi lo legge — il driver scrive `c2_<modello>_<infra>_<trasporto>.csv` e `check_cost.sh` filtra su `c2_*`. |

## Come si annota un invalidamento

Tre cose, e la terza è quella che manca sempre:

1. **quale lotto** — nome del file e intervallo di righe, non «alcune run»;
2. **la causa**, con l'evidenza (messaggio verbatim, diff dello script, commit);
3. **il ricalcolo** — il numero prima e dopo. Un'annotazione senza ricalcolo dice che qualcosa
   è cambiato senza dire di quanto, ed è il caso in cui un revisore deve rifare i conti da solo.

## 2026-08-15 — smoke della ri-raccolta (SUCCESSIONE-09)

`c2r_gpt-oss-120b_databricks_native_SMOKE.csv` — 1 binario, 1 run, $0,0011. Serviva a
verificare, prima di spendere $138,83, che il braccio nuovo scriva solo sotto i propri percorsi
`c2r_` e non tocchi i 5.912 file della raccolta originale. Verificato: impronta dei file
esistenti identica prima e dopo.

**Spostato in `results/riraccolta/smoke/`, non cancellato** (IR-5). Sta in una sottocartella
perche' `carica()` fa glob non ricorsivo: se restasse accanto ai CSV del braccio, la sua unica
riga entrerebbe nella cella `gpt-oss-120b/databricks/native` e il binario `prog16_word_count_fsm`
avrebbe nove run invece di otto, con `v[:8]` che ne prenderebbe una dallo smoke. Non e' un
dettaglio di ordine: e' contaminazione, e il posto giusto e' una cartella che l'analisi non
guarda.

## 2026-08-16 — la cella haiku dell'ablazione contiene due raccolte, entrambe valide

`c2a_claude-haiku-4-5_databricks_native1_redo2.csv` (358 misure, 15/08 19:43–21:29) e
`c2a_claude-haiku-4-5_databricks_native1.csv` (360 misure, 15/08 22:38–16/08 00:26) sono due
raccolte **complete e indipendenti della stessa cella**, prodotte da un difetto del driver
descritto in `registro/NOTA-02-doppia-raccolta-haiku.md`: con la catena dei suffissi bucata, il
driver riceve l'elenco completo dei 45 binari invece dei soli carenti.

**Nessuna delle due è invalidata**, e la distinzione conta: un lotto si invalida quando porta un
canale sistematico e asimmetrico fra i bracci confrontati (è il criterio applicato al lotto del
nome-algoritmo). Qui non c'è contaminazione — c'è una misura in doppio, che è una cosa diversa e
utile.

L'analisi congelata usa le otto run della **seconda** raccolta, perche' `carica()` legge in
ordine alfabetico e `media_per_binario` prende `v[:8]`. Determinato dall'ordinamento, non da una
scelta: dichiarato qui perche' non vada dedotto dal codice.

Le due insieme misurano il rumore fra raccolte a parità di tutto il resto: **+0,12pp**, 42 binari
identici su 43 (`python3 analysis/test_retest_ablazione.py`). È il metro con cui si leggerà il
confronto fra raccolta originale e ri-raccolta.
