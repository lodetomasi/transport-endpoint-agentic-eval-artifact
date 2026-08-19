# Nota 02 — la cella haiku dell'ablazione raccolta due volte, e cosa ne è uscito

**Data**: 2026-08-16, scritta appena i numeri non hanno torto.
**Lo script che li produce**: `analysis/test_retest_ablazione.py`.

## Il fatto

La cella `claude-haiku-4-5 / databricks / native` del braccio di ablazione contiene **45 binari
× 16 run** invece di 8. Due raccolte complete della stessa cella:

| file | finestra | misurazioni |
|---|---|---|
| `..._native1_redo2.csv` | 15/08 19:43 → 21:29 | 358 |
| `..._native1_redo.csv` | 15/08 22:52 | 2 |
| `..._native1.csv` | 15/08 22:38 → 16/08 00:26 | 360 |

Costo dello spreco: circa **$8,70**, la tariffa misurata di una cella haiku piena.

## Perché è successo: due difetti concatenati

**Il primo è vecchio e documentato.** `SUCCESSIONE-08` registra che il primo CSV dell'ablazione
nacque come `_redo2` perché `prossimo_suffisso` guardava la catena del braccio sbagliato. La
catena rimase **bucata**: esisteva `_redo2` senza che esistessero `` e `_redo`.

**Il secondo è in `src/raccogli_c2.py:247-249`**, ed è quello nuovo:

```python
suffisso = cc.prossimo_suffisso(eti, infra, trasporto, braccio)
if suffisso:
    elenco = ...manca_<cella>.txt      # solo i binari carenti
```

La restrizione ai binari carenti si applica **solo se il suffisso non è vuoto**. Con la catena
bucata il primo posto libero era quello senza suffisso, quindi il driver ha ricevuto l'elenco
completo dei 45 binari e `runs` pari al deficit massimo — e ha rifatto tutta la cella invece dei
due binari che mancavano.

L'assunzione implicita era «suffisso vuoto ⇒ cella nuova ⇒ raccogli tutto». È vera finché la
catena si riempie in ordine, e la successione 08 aveva già documentato che qui non era così.

**Un terzo, minore ma da dire.** Ho ucciso il driver alle 22:51 per collaudare il supervisore.
Il `kill` sul driver **non uccide il worker figlio**: `run_minipilot` ha continuato a raccogliere
fino alle 00:26. `sorveglia_costi.sh` fa la cosa giusta — uccide entrambi — ma il mio kill
manuale no, e per due ore ha girato un worker che nessuno stava più governando.

## Che cosa usa l'analisi, e perché va dichiarato

`carica()` legge i file in ordine alfabetico e `media_per_binario` prende `v[:8]`. L'ordine è
`native1.csv`, `native1_redo.csv`, `native1_redo2.csv`, quindi **l'analisi usa le otto run della
seconda raccolta** e ignora la prima. Non è sbagliato — è una raccolta coerente e completa — ma
è determinato da un accidente di ordinamento alfabetico e non da una decisione. Lo si dichiara
qui perché nessuno lo deduca dal codice.

## Il risultato che ne è uscito, e che non si poteva comprare

Due raccolte complete della stessa cella, stesso apparato, stesso protocollo, separate da tre
ore. È un **test-retest** che il disegno non prevedeva:

| | |
|---|---|
| media raccolta 1 | 0,7651 |
| media raccolta 2 | 0,7663 |
| differenza | **+0,12pp** |
| binari con punteggio identico | **42 su 43** |
| scarto massimo su un binario | 0,05 |
| deviazione standard delle differenze | 0,0076 |

**Perché conta.** `EMENDAMENTO-06` chiede se la differenza fra raccolta originale e ri-raccolta
sia attribuibile all'apparato o al fatto che due raccolte differiscono comunque. Quella domanda
non aveva un metro, e ora ne ha uno: su questa cella il rumore fra due raccolte è **0,12pp**,
contro i −10,4pp del contrasto T3. Una differenza di quest'ordine è rumore; una di ordine
superiore no.

**Il limite di questo numero, dichiarato.** Vale per una cella e per haiku, che è il modello più
stabile del roster — 98–100% dei binari con otto run identiche. È un **limite inferiore** del
rumore, non una stima per l'intera griglia, e si riporta così.

## Cosa si fa dei dati

Restano dove sono. `results/` è append-only e le 358 misurazioni della prima raccolta non sono
invalide: sono una misura legittima della stessa cella, e sono metà del test-retest. Sono
annotate in `results/README-validita.md`.

## Cosa non si fa adesso

Il difetto della riga 248 **non si corregge durante la raccolta**: `raccogli_c2.py` è congelato,
una successione scritta ora andrebbe scritta mentre due bracci scrivono, e il difetto non
minaccia nulla di attivo — verificato cella per cella, la ri-raccolta usa il suffisso vuoto solo
dove i binari carenti sono davvero 45. Si corregge a raccolte chiuse, con la successione scritta
prima, come vuole la regola.
