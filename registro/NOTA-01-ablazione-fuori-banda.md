# Nota 01 — l'ablazione cade fuori dalla banda pre-dichiarata, e perché non si ferma

**Data**: 2026-08-15, scritta a raccolta ancora in corso e **prima** che questi dati entrino in
qualunque numero del paper.
**Riferimento**: `registro/SUCCESSIONE-08-ablazione-batching.md`, sezione «Come si verifica che
l'ablazione morda davvero».
**Lo script che produce i numeri**: `analysis/mordente_ablazione.py`.

## Cosa era stato dichiarato prima

La successione 08 ha fissato, prima di spendere, che la quota di turni con almeno una chiamata
scartata dovesse cadere fra il **33% e il 38%** — stimata dalla quota di turni con più di una
chiamata misurata nel nativo pieno (haiku 38,0%, sonnet 32,6%). E ha dichiarato le due letture
possibili di uno scostamento: quota vicina a zero significa che il vincolo non morde e il
braccio sta pagando un duplicato del nativo, quindi **si ferma**; quota molto più alta significa
che il modello reagisce cambiando strategia, quindi si raccoglie **dichiarandolo**.

## Cosa si osserva

**Numeri definitivi, a braccio chiuso il 2026-08-16** (la prima stesura di questa nota li
riportava su 154 traiettorie, quando la raccolta era al 21%; la conclusione non cambia, la
precisione sì). Su **1.084 traiettorie** e 5.541 turni con almeno una chiamata, la quota
complessiva è **19,7%**, sotto la banda. La scomposizione per indice di turno non è ambigua:

| | turni | con scarto |
|---|---|---|
| turno 1 | 1.084 | **1.084 — 100,0%** |
| turno 4 | 1.084 | 8 — 0,7% |
| tutti gli altri | — | **0 — 0,0%** |

Condizionando sul fatto che la traiettoria abbia già ricevuto un rifiuto: **100,0% prima**,
**0,2% dopo** (8 turni su 4.457). Non è zero assoluto — otto traiettorie su mille riprovano una
volta — e la formulazione esatta è «quasi mai», non «mai».

## La lettura, e perché non è la prima delle due dichiarate

Il vincolo **morde al massimo grado**: ogni singola traiettoria raggruppa al primo turno e viene
bloccata. La quota complessiva scende sotto la banda perché dopo un solo rifiuto il modello
**quasi non ci riprova più** — lo 0,2% dei turni successivi, otto su 4.457.

Cio' che la banda presupponeva — un tasso di raggruppamento costante lungo la traiettoria — è
falsificato dai dati. La stima veniva dal nativo pieno, dove nessun rifiuto arriva mai e il
tasso resta quello; nel braccio vincolato il primo turno lo azzera per il resto della run. La
banda era mal specificata, e lo era in un modo che i dati del nativo pieno non potevano
rivelare.

**Non ricade quindi nel caso «vicina a zero»**, che era la condizione di arresto: quel caso
descriveva un vincolo inerte, e qui il vincolo è massimamente attivo esattamente dove può
esserlo. La raccolta prosegue.

## E l'effetto che il braccio doveva misurare

Con il braccio chiuso, il numero per cui esisteva: vincolare il nativo a una chiamata per turno
**non abbassa il punteggio** — haiku +0,8pp [−2,6, +4,2], sonnet +1,6pp [−1,3, +4,4], appaiati
su 45 binari (`analysis/effetto_batching.py`). Entrambe le differenze sono positive e entrambi
gli intervalli contengono lo zero, contro un T3 di −10,4pp sullo stesso modello e sullo stesso
endpoint.

La perdita di raggruppamento non spiega quindi l'effetto del trasporto: né per direzione, né
per ordine di grandezza. Il confondimento che il disegno poteva solo dichiarare è delimitato, e
ciò che T3 misura è il protocollo.

## Cosa questo obbliga a scrivere nel paper

Due cose, e la seconda è un risultato che non stavo cercando.

1. **Il braccio non isola il solo batching.** La differenza fra nativo pieno e nativo vincolato
   include l'adattamento al rifiuto. Si riporta come **limite superiore** dell'effetto del
   batching, non come sua stima.
2. **Un solo rifiuto riconfigura il protocollo del modello per il resto della traiettoria**, in
   modo completo e permanente: 100% prima, 0% dopo, senza eccezioni su 156 traiettorie. Il
   trasporto non è soltanto un canale con un formato — è un canale che **insegna**. Ed è una
   ragione ulteriore per cui il confronto nativo/testuale non è simmetrico: nel testuale
   l'opzione di raggruppare non esiste mai, nel nativo vincolato esiste per un turno e poi il
   modello la abbandona da sé.

## Perché questa nota esiste

Perché la banda è stata mancata, e il modo in cui si sbaglia qui è scrivere la spiegazione dopo
aver deciso che i dati piacevano. La spiegazione è verificabile con un comando
(`python3 analysis/mordente_ablazione.py`), lo script contiene la condizione di arresto che
avrebbe fermato il braccio nel caso opposto, e questa nota è datata prima che una sola riga
dell'ablazione raggiunga il paper.

## Cosa resta da aggiornare altrove

`results/CARD-C2-v7.md`, riga 296, dice che il confondimento fra trasporto e batching e' «più
forte di come la v6 lo descriveva, **non delimitato**». Dal 16/08 e' delimitato. La card non si
riscrive — e' versionata e `results/` non si modifica — e la **v8 si emette a ri-raccolta
chiusa**, con i numeri dei due bracci insieme invece che in due passaggi. Il promemoria e' in
`chiusura.sh`, punto a-bis, perche' un proposito in una nota si dimentica e un passo in uno
script no.
