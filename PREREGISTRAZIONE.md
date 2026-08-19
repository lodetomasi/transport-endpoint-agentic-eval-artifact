# Pre-registrazione — C2: l'interfaccia dei tool è un parametro libero

**Stato**: congelata prima che esista una sola riga di dati di C2.
**Data**: 2026-08-13.
**Progetto precedente**: C1, `~/<capitolo-precedente>` — i cui dati sono usati **solo**
per calibrare la potenza, mai come evidenza per le ipotesi qui sotto.

---

## 1. Separazione esplorativo / confermativo

Sono **esplorativi**, e non entrano in nessun test qui pre-registrato:

- le differenze fra trasporti già misurate in C1 (Llama-3.3 +3,0pp, Haiku −10,4pp): sono il
  seme di questo studio e i dati che ne calibrano la potenza, quindi sono già stati visti;
- il censimento in `research/CENSIMENTO.md`, che descrive quali modelli ciascuna
  infrastruttura serve e quali rifiuta.

È **confermativo** tutto ciò che segue, su dati raccolti dopo questa data.

## 2. La claim

> La capacità agentica misurata è funzione del trasporto delle chiamate ai tool — function
> calling nativo contro protocollo testuale — e dell'infrastruttura che lo implementa. Nessuna
> valutazione agentica pubblicata dichiara quale usa.

Il contributo non è che «il trasporto conta». È che **il trasporto è un grado di libertà non
dichiarato dell'apparato di misura**, e che si comporta in due modi qualitativamente diversi:
sposta un numero *e* cancella un modello dal campione. Il secondo è un effetto di selezione, e
una selezione non si delimita, perché il modello assente non ha una riga da correggere.

## 3. Ipotesi

Quattro modelli (`gpt-oss-120b`, `llama-3.3-70b`, `claude-haiku-4-5`, `claude-sonnet-4-5`), due
infrastrutture (Databricks `<profilo-databricks>`, Bedrock `<profilo-bedrock>` us-east-1), due trasporti (tool
nativi, protocollo `TOOL_CALL:` nel testo), gli stessi 45 binari held-out di C1.

| id | ipotesi |
|---|---|
| **H1** | Per almeno un modello, la differenza fra trasporti a infrastruttura fissa esce dalla banda ±3pp con IC95 che la esclude. |
| **H2** | Per almeno un modello, la differenza fra infrastrutture a trasporto fisso esce dalla banda ±3pp con IC95 che la esclude. |
| **H3** | L'effetto del trasporto **non è costante fra modelli**: la varianza fra modelli dell'effetto è maggiore di zero. |
| **H4** | L'effetto del trasporto **non è costante fra infrastrutture**: esiste interazione trasporto × infrastruttura. |

H1 e H2 sono **disgiuntive** di proposito, e la ragione sta in §7: rifiutare «tutti i modelli
stanno dentro ±3pp» richiede un solo modello fuori banda, mentre *confermarla* richiede un test
di equivalenza su ciascun modello, e K=45 non lo alimenta. L'asimmetria è dichiarata prima, non
scoperta dopo.

## 4. Falsificatori

- **H1 falsa se** su tutti e quattro i modelli, su entrambe le infrastrutture, la differenza fra
  trasporti sta entro ±3pp con IC95 contenuto nella banda (equivalenza TOST), **e** nessun
  modello del roster viene escluso da un rifiuto di protocollo.
- **H2 falsa se** l'analogo vale scambiando trasporto e infrastruttura.
- **H3 falsa se** il modello misto con effetto casuale del modello sulla pendenza del trasporto
  non migliora l'adattamento rispetto a quello a pendenza fissa (LRT, α=0,05).
- **H4 falsa se** il termine di interazione trasporto × infrastruttura ha IC95 che contiene lo
  zero su tutti i modelli.

**Se tutti e quattro cadono**: il risultato è che l'infrastruttura di servizio è una variabile
più stabile di quanto la sua documentazione lasci supporre, e questo studio è la misura che lo
stabilisce insieme allo strumento che chiunque può rieseguire sul proprio apparato. Si scrive
così, non «non siamo riusciti a trovare un effetto».

## 5. Metrica primaria

**Pass-rate** sui test unitari del programma originale, rieseguiti sul candidato ricostruito.

È un **lower bound** dell'equivalenza semantica, mai equivalenza (Liu & Wang, ISSTA 2020), e si
riporta come tale in ogni punto del paper. L'unità di analisi è la **cella**: (modello ×
infrastruttura × trasporto × binario), media di 8 run.

Una riga è una misurazione se e solo se `qualita_run.e_misurazione` la accetta. La regola è
**una sola** e condivisa fra raccolta e analisi: in C1 un campo `infra_failure` scritto
dall'harness e letto da nessuno dei tre script di analisi produsse 204 righe mediate come
pass_rate = 0, e il confine cross-modello che ne uscì fu pubblicato e poi ritirato.

## 6. Disegno

| | |
|---|---|
| binari | i **45 held-out** di C1, congelati per nome in `configs/binari_holdout.txt`, sha256 `972e11f3…` |
| run per cella | 8 |
| celle | 4 modelli × 2 infrastrutture × 2 trasporti = 16 |
| run totali | 16 × 45 × 8 = **5 760** |
| turni | N = 12, identico a C1 |
| temperatura | 0,0 dove il modello la accetta; dichiarata per modello nei record |
| costo previsto | **$122,21 ≈ 112 €** ai listini in `configs/pricing.json` |

**Perché gli stessi 45 e non un corpus nuovo**: tenere il corpus identico rende il confronto con
C1 diretto invece che argomentato, e sposta l'unica differenza sul trasporto. Un corpus nuovo
aggiungerebbe una variabile che questo studio non vuole muovere.

### Decisioni vincolanti, derivate da difetti reali di C1

1. **Nessun markdown attorno al codice C.** Un candidato avvolto in ``` misurava la
   formattazione, non la ricostruzione.
2. **Ordine nativo delle funzioni**, mai per dimensione. In C1 l'ordinamento per dimensione nel
   baseline era un vantaggio non dichiarato.
3. **Tabella dei simboli rimossa** da ogni binario. Con i simboli il binario dice il nome
   dell'algoritmo e il baseline saliva a 0,894.
4. **Un turno di solo reasoning non è un fallimento**, e non si registra come pass_rate = 0.
5. **La guardia sui prezzi rifiuta prima della chiamata.** Fino al 2026-08-13 il controllo stava
   dopo, e un modello senza tariffa veniva fatturato per una chiamata prima di essere respinto:
   misurato a 4,51 s contro 0,00 s.
6. **`max_completion_tokens`, mai un fallback silenzioso.** Su Azure `gpt-5.1` rifiuta
   `max_tokens` con 400 mentre altri accettano entrambi; un try-uno-poi-l'altro renderebbe la
   richiesta effettivamente inviata dipendente da un ramo d'errore.

### Il trasporto testuale, definito

Il protocollo è in `src/harness/agent_loop.py`, costante `TEXT_TOOL_PROTOCOL`. Il modello
termina la risposta con una sola riga `TOOL_CALL: {"name": ..., "arguments": {...}}`; l'output
del tool torna come messaggio `user`. Il campo `tools` della richiesta **non viene inviato**.

Un turno che produce prosa senza `TOOL_CALL:` e senza codice C è un turno senza chiamata, non un
fallimento: in C1 il ciclo testuale trattava la prosa come risposta finale e chiudeva al turno 1.

## 7. Piano statistico

**Test primario per H1 e H2**: t appaiato per binario, entro modello e entro infrastruttura.
**H3**: modello misto `pass_rate ~ trasporto + (trasporto | modello) + (1 | binario)`, LRT contro
la pendenza fissa. **H4**: termine di interazione nello stesso modello.

**Famiglia pre-registrata per Holm**, dieci test, congelata qui e non modificabile:

| | test |
|---|---|
| T1 | `gpt-oss-120b` — nativo vs testo, Databricks |
| T2 | `llama-3.3-70b` — nativo vs testo, Databricks |
| T3 | `claude-haiku-4-5` — nativo vs testo, Databricks |
| T4 | `claude-sonnet-4-5` — nativo vs testo, Databricks |
| T5 | `gpt-oss-120b` — Databricks vs Bedrock, trasporto nativo |
| T6 | `llama-3.3-70b` — Databricks vs Bedrock, trasporto nativo |
| T7 | `claude-haiku-4-5` — Databricks vs Bedrock, trasporto nativo |
| T8 | `claude-sonnet-4-5` — Databricks vs Bedrock, trasporto nativo |
| T9 | eterogeneità dell'effetto trasporto fra modelli (LRT) |
| T10 | interazione trasporto × infrastruttura |

**m resta 10 anche se un braccio non è eseguibile.** Togliere un test dalla famiglia a dati visti
abbassa le soglie di Holm dei sopravvissuti: si tiene m fisso e non si testa l'incompleto. È la
lettura conservativa, ed è quella che si riporta.

### Potenza, calcolata sui dati di C1 e non ipotizzata

`analysis/potenza.py`, rieseguibile. La SD rilevante è quella della **differenza appaiata per
binario**, non il σ di C1: C1 confrontava bracci diversi su binari diversi, e l'appaiamento
toglie la varianza fra binari.

| | |
|---|---|
| SD entro-modello, pooling per varianza | **0,1062** |
| SD del modello peggiore, conservativa | **0,1167** |
| MDE a K=45, 80% di potenza | **4,43pp** pooled, **4,87pp** conservativa |
| K per rilevare 3pp | **99** pooled, **119** conservativa |

**K=45 non alimenta un test di equivalenza a 3pp, e questo è dichiarato prima dei dati.** Un
risultato nullo si riporta come «l'IC esclude qualunque effetto sopra 4,9pp», mai come «nessuna
differenza».

Il pavimento spiega perché non basta aggiungere run: per `llama-3.3-70b` il 60% della varianza
della differenza è eterogeneità vera fra binari, e con run infiniti resterebbe SD 0,0903, cioè
K≥72. Per `haiku-4-5` l'84% è rumore fra run e il pavimento è K=13. Le due leve non sono
intercambiabili, e quale morda dipende dal modello.

## 8. Regole di onestà

- Ogni numero traccia a un file in `results/`; `results/` è **append-only**, gli invalidati si
  annotano in `results/README-validita.md`.
- Lo script di analisi è congelato per hash **insieme** a questa pre-registrazione, prima che i
  dati esistano. Congelare le ipotesi e scrivere l'analisi a dati visti lascia aperta tutta la
  libertà che la pre-registrazione doveva chiudere.
- Ogni emendamento è un file datato con l'effetto isolato della modifica. Il registro sta
  nell'artefatto pubblico; nel paper ne resta **una menzione, non una narrazione**.
- Un braccio non eseguibile — un endpoint che rifiuta il protocollo — non è un braccio
  incompleto: si dichiara `NON_ESEGUIBILE` con il messaggio verbatim, e **in questo studio è un
  risultato**, non un intoppo.
- Nessuna soglia si modifica dopo aver visto i dati.

## 9. Cosa non rivendichiamo

- Non che un trasporto sia **migliore**. Si misura che la scelta sposta il numero, non quale
  scelta sia giusta.
- Non che l'effetto valga fuori dal reverse engineering di binari offuscati, dai quattro modelli
  del roster, o dalle due infrastrutture misurate.
- Non equivalenza semantica: pass-rate è un lower bound.
- Non che i cinque meccanismi di cancellazione osservati siano esaustivi. Sono cinque trovati
  costruendo un campione, e la classe è aperta.

## 10. Artefatto

Deposito anonimo con: i 45 binari e i loro test, i decompilati, l'harness con entrambi i
trasporti, `configs/pricing.json` con la fonte di ogni tariffa, questa pre-registrazione con il
suo hash, lo script di analisi con il suo, il registro degli emendamenti, e i CSV grezzi
compresi quelli invalidati con la ragione.
