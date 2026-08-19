# Successione 08 — un braccio di ablazione per separare trasporto e batching

**Data**: 2026-08-15, scritto **prima** della modifica.
**Hash di `src/raccogli_c2.py` dopo questa successione**: `eb58dd2f86c26112746299d36407a9bbc56ee249379d3a94956ace0081aaf80b`
**Hash precedente**: quello dichiarato in `HASH-CONGELATI.md` alla riga della successione 06.
**Innesco**: il gauntlet sul paper. Il confondimento era già dichiarato; questo lo misura.

## Il file

`src/raccogli_c2.py`, più `src/run_minipilot.py` e `src/harness/agent_loop.py`, che congelati
non sono ma hanno prodotto dati e quindi ricadono nello stesso innesco.

## Cosa cambia

Tre cose, e nessuna tocca il percorso confermativo.

1. **`agent_loop.run_agent` accetta `max_calls_per_turn`.** Con `1`, sul trasporto nativo,
   esegue la prima chiamata di ogni turno e **registra le altre come scartate** invece di
   eseguirle. Il default è `None` e non cambia nulla.
2. **`run_minipilot.py` espone `--max-calls-per-turn`** e lo passa al ciclo.
3. **`raccogli_c2.py` guadagna `--ablazione`**, che raccoglie le celle del braccio nuovo in
   `results/ablazione/`, con prefisso `c2a_`, **e restringe da sé il roster** ai due modelli
   che raggruppano e al solo trasporto nativo. Il filtro sta nel codice e non nella riga di
   comando per una ragione trovata al dry-run: `--ablazione` nudo generava sedici celle per
   circa $140, sforando il tetto. Una guardia contro un errore che costa, non una comodità.

## Perché serve, e perché non basta dichiararlo

Il disegno pre-registrato confronta due trasporti che differiscono per **due** cose insieme: il
formato della chiamata, e il fatto che il protocollo testuale ammette **una sola** chiamata per
turno mentre il nativo ne ammette molte. Dove il modello raggruppa — haiku 1,437 chiamate per
turno, sonnet 1,332 — T3 e T4 misurano la somma delle due manipolazioni.

Finora il paper poteva solo **dichiarare** il confondimento. Un braccio nativo forzato a una
chiamata per turno lo **misura**: la differenza fra il nativo pieno e il nativo vincolato è
l'effetto del batching, e quel che resta confrontando il nativo vincolato col testuale è
l'effetto del protocollo.

## Perché è una successione e non un emendamento

Perché tocca un file congelato. Ma va detto con precisione cosa **non** cambia:

- Le sedici celle confermative, il loro roster, i 45 binari, le 8 run, i 12 turni, la
  temperatura: identici, e il default `None` garantisce che il codice si comporti come prima.
- La famiglia dei dieci test e `m = 10`: **il braccio di ablazione non entra in Holm.** Non è
  uno degli otto contrasti pre-registrati e non ne aggiunge un nono.
- L'analisi congelata: `analyze_c2.py` fa `glob` non ricorsivo su `results/*.csv`, e i CSV
  dell'ablazione stanno in `results/ablazione/`. Sono invisibili al confermativo per
  **costruzione**, come già l'esplorativo Azure — la separazione è strutturale e non affidata a
  un prefisso che qualcuno potrebbe cambiare.

**L'ablazione è esplorativa e si riporta come tale.** Serve a delimitare una limitazione
dichiarata, non a sostenere un'ipotesi.

## L'altra modifica, che è una correzione

`run_minipilot.py` compilava in `results/workv3/<prog>_r<run_id>`, senza la cella nel percorso:
sedici celle su 360 directory condivise, con driver concorrenti (`SUCCESSIONE-07`). Ora il
percorso porta il tag della cella, come `write_trajectory` fa già da sempre venti righe sopra.

**Non retroagisce.** I dati raccolti restano quelli che sono, con la loro minaccia dichiarata
nel paper. Questa modifica serve al braccio nuovo e a chiunque riesegua.

## Due funzioni che guardavano il braccio sbagliato

`completa_celle.deficit` e `completa_celle.prossimo_suffisso` costruivano il percorso del CSV
senza sapere di quale braccio si stesse parlando. La prima avrebbe fatto dire al driver «CHIUSA
già» per una cella di ablazione vuota, perché la cella **confermativa** con quel nome è chiusa:
la raccolta sarebbe uscita con successo, spendendo zero e senza produrre un file. La seconda ha
fatto nascere il primo CSV dell'ablazione come `_redo2`, prendendo il posto libero nella catena
del confermativo.

Entrambe ora passano da `percorso_cella()`, che è l'unico posto dove si decide dove sta il file
di una cella. La prima l'ha trovata `<revisione-avversariale-dell-apparato>` prima della raccolta; la seconda è
saltata fuori guardando il nome del primo file prodotto.

## Il costo, e perché si ferma qui

Il braccio minimo che risponde alla domanda è **haiku e sonnet, trasporto nativo vincolato, su
una sola infrastruttura**: sono i due modelli che raggruppano, e T3/T4 sono i contrasti
confondi. Due celle da 45 binari × 8 run = 720 run.

Alle tariffe misurate — haiku $8,70 e sonnet $19,36 per cella piena — la stima è **~$28**, che
va sommata ai $139,58 già spesi per un totale intorno a **$168 sul tetto di $200**
(`EMENDAMENTO-01`). Resta margine, e il tetto **non si alza**: se la stima fosse sbagliata di
un fattore due, la sorveglianza ferma la raccolta prima del limite, che è il suo mestiere.

Non si estende alle altre due celle (gpt-oss e llama) perché su quei modelli il tasso di
chiamate per turno è **esattamente 1,000**: l'ablazione non toglierebbe nulla, e il braccio
misurerebbe la stessa cosa due volte pagandola.

## Come si verifica che l'ablazione morda davvero

**Prima di spendere**: uno smoke su un binario che registri almeno una chiamata scartata.
Fatto, e ha trovato due difetti — un `tool_result` mancante che avrebbe ucciso ogni cella, e il
flag perso in scrittura che avrebbe fatto fermare una raccolta sana.

**Durante la raccolta, con una soglia e non con una presenza.** «Il campo compare» non basta:
una singola occorrenza non esclude che il braccio stia raccogliendo un duplicato del nativo.
Dalle traiettorie confermative già in mano, la quota di turni con più di una chiamata è:

| cella | turni con >1 chiamata | chiamate per turno |
|---|---|---|
| haiku / databricks | 38,0% | 1,437 |
| haiku / bedrock | 37,9% | 1,436 |
| sonnet / databricks | 32,6% | 1,332 |
| sonnet / bedrock | 32,7% | 1,333 |

Sull'intera cella di ablazione ci si attende quindi una quota di **turni con almeno uno scarto**
dello stesso ordine — **33–38%**. Una quota vicina a zero significa che il vincolo non sta
mordendo e il braccio sta pagando un duplicato del nativo: si ferma. Una quota molto più alta
significa che il modello sta reagendo al rifiuto cambiando strategia, e allora il braccio misura
anche quella reazione: si raccoglie lo stesso, ma si dichiara.

**Perché la soglia viene dai dati e non da un'intuizione**: gli altri due modelli del roster
stanno a **esattamente** 1,000 chiamate per turno su 386 e 361 traiettorie — non una media che
nasconde varianza, un vincolo che tiene sempre. È la ragione per cui l'ablazione li esclude, ed
è verificata invece che asserita.
