# Successione 02 — ripresa delle celle parziali in `src/raccogli_c2.py`

**Data**: 2026-08-14. **Stato della raccolta**: tre celle iniziate, nessuna analisi eseguita.

## Il file

`src/raccogli_c2.py`

## Cosa è cambiato

La condizione di salto passa da **«il file esiste»** a **«ogni binario ha 8 run valide»**, e
quando la cella è parziale il driver la **completa** invece di saltarla: calcola il deficit per
binario con `src/completa_celle.py`, scrive l'elenco dei soli binari carenti, e riesegue con
`--runs <deficit massimo>` su un file col suffisso successivo della catena `("", "_redo",
"_redo2", "_redo3")`.

`comando()` prende ora tre parametri in più — elenco, run, suffisso — perché una ripresa non è
una ripetizione della cella intera.

## Perché

Un CSV interrotto a metà **esiste**. Con la condizione precedente sarebbe stato saltato per
sempre, e la cella sarebbe rimasta corta senza che nulla lo dicesse: `analyze_c2.py` l'avrebbe
rifiutata come parziale, ma solo alla fine, dopo che il tempo e il denaro erano spesi.

E un braccio parziale è peggio di un braccio assente: i binari si processano in ordine di
indice e i primi sono più facili, quindi la media su un prefisso stima i binari facili. In C1
un braccio a 0,936 a metà raccolta ha chiuso a 0,832.

## Cosa l'ha resa necessaria

Un mio collaudo della sorveglianza dei costi, in una cartella temporanea, usava
`pgrep -f "raccogli_c2.py"`: quel pattern cerca su **tutta la macchina** e ha ucciso la
raccolta vera. Tre celle sono rimaste parziali (351/360, 358/360, 39/360).

Nessun dato è andato perso — `results/` è append-only e i CSV erano integri — ma il driver non
sapeva riprendere. Il difetto del pattern è corretto in `sorveglia_costi.sh`, che ora identifica
i processi col **percorso assoluto** del progetto: è l'autocattura di `ps | grep` applicata al
kill, dove la vittima non è il grep ma l'esperimento.

## Effetto isolato sulla misura

**Nessuno sul contenuto.** Le run di ripresa sono identiche a quelle che sarebbero state
raccolte senza interruzione: stesso modello, stesso trasporto, stessi turni, stessa
temperatura, stesso elenco congelato di binari.

Due conseguenze da dichiarare, e sono entrambe visibili nell'artefatto:

1. **Sovra-raccolta possibile.** `--runs` è uniforme, quindi un binario con deficit 1 in una
   cella il cui deficit massimo è 4 riceve 4 run. L'analisi tiene le **prime 8 valide** per
   binario, quindi il numero pubblicato non cambia; la spesa sì, ed è nel ledger.
2. **Le riesecuzioni sono file distinti**, non righe aggiunte al file originale, perché
   `results/` è append-only. La catena si legge concatenando i suffissi — è la stessa
   convenzione di C1.

Il quinto suffisso non esiste: `prossimo_suffisso()` esce con errore invece di crearne uno che
nessuna analisi leggerebbe.

## Verifica

Ripresa reale della cella `gpt-oss-120b/databricks/text`, che era a 358/360:

```
RIPRESA: 2 binari carenti, 1 run each -> suffisso '_redo'
poi: CHIUSA (360 valide)
```

Il file originale è intatto e la ripresa è in `c2_gpt-oss-120b_databricks_text_redo.csv`.
