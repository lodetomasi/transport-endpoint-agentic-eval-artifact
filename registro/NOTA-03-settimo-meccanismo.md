# Nota 03 — un settimo meccanismo: l'endpoint rifiuta l'output del modello che serve

**Data**: 2026-08-17, trovato chiudendo l'ultimo binario della ri-raccolta.
**Verbatim dell'endpoint** (Bedrock, `us-east-1`, API Converse):

> `ValidationException: 1 validation error detected: Value at
> 'messages.10.member.content.1.member.toolUse.name' failed to satisfy constraint: Member must
> satisfy regular expression pattern: [a-zA-Z0-9_-]+`

## Cosa succede, in ordine

1. `gpt-oss-120b` emette una chiamata a tool nel proprio formato di chat, che usa token speciali
   per separare i canali di ragionamento.
2. Il layer di serving di Bedrock non separa quel token dal nome del tool. Nelle traiettorie il
   nome arriva come **`decompile_function<|channel|>commentary`** — quattro occorrenze registrate
   con quel valore esatto.
3. L'API Converse valida il nome contro `[a-zA-Z0-9_-]+`, non lo accetta, e **rifiuta l'intera
   richiesta**.
4. La traiettoria muore. Non il turno: la run.

**L'endpoint rifiuta l'output del modello che esso stesso serve.** Non sbaglia il modello, che
emette il proprio formato nativo; non sbaglia l'esperimento, che manda una richiesta valida. Il
serving stack non chiude il cerchio fra il formato del modello che ospita e la validazione della
propria API.

## Perché è un meccanismo e non un guasto

Il criterio che il paper usa per distinguere le due cose e' la riparabilita': un guasto, riparato,
smette di accadere. Questo no — l'endpoint sta funzionando come configurato, il validatore fa il
suo lavoro, e la risposta corretta alla richiesta e' un rifiuto. Non c'e' niente da riparare dal
lato di chi misura, e riprovare non aiuta: **su `prog39_horner` sono state necessarie quindici
run per ottenerne sette valide**.

## Dove colpisce

| cella | binari colpiti |
|---|---|
| `gpt-oss-120b / bedrock / native` (originale) | `prog25_balanced_multitype`, `prog39_horner` |
| `gpt-oss-120b / bedrock / native` (ri-raccolta) | `prog25_balanced_multitype`, `prog49_bst`, `prog52_bfs_grid`, `prog39_horner` |

**Una sola cella su sedici**, in entrambe le raccolte: il modello a pesi aperti sul cloud che non
l'ha addestrato, e solo sul trasporto nativo. Sul trasporto testuale il nome del tool non passa
per il campo `toolUse` e il validatore non lo vede — cioe' **il trasporto testuale e' immune a un
meccanismo che uccide il nativo**, che e' un'osservazione sull'asse che questo studio misura.

Undici occorrenze in tutto fra i due batch.

## La conseguenza sperimentale, e come si riporta

`prog39_horner` resta a **sette run valide su otto** nella ri-raccolta. La catena dei suffissi di
quella cella e' esaurita — `''`, `_redo`, `_redo2`, `_redo3` — e il driver si rifiuta di creare un
quinto file perche' `valide_per_binario` itera su una lista fissa e non lo leggerebbe. La guardia
ha ragione: un file che nessuna analisi legge e' peggio di un file assente.

**Quel binario NON esce dall'analisi, e la prima stesura di questa nota diceva il contrario.**
L'avevo asserito senza verificarlo: `media_per_binario` filtra su `and v` — lista non vuota — non
su `len(v) >= RUN_ATTESI`. Quindi include il binario con le sette run che ha, mediandole, e **K
resta 45**. Il comportamento e' quello del file congelato e non si cambia; si dichiara.

Verificato l'impatto sul contrasto che quella cella alimenta:

| T5 (gpt-oss, bedrock vs databricks, nativo) | K | differenza | IC95 | p |
|---|---|---|---|---|
| come l'analisi congelata lo calcola | 45 | $+3{,}26$pp | $[-0{,}6, +7{,}1]$ | 0,0893 |
| escludendo il binario a sette run | 44 | $+3{,}12$pp | $[-0{,}8, +7{,}1]$ | 0,1107 |

Lo scarto e' **0,14pp sul contrasto e 0,021 su p**, e nessuna delle due versioni si avvicina alla
soglia di Holm (0,0071 al rango di T5). La scelta di includere o escludere non cambia una
conclusione, ed e' per questo che si puo' dichiarare invece di dover decidere.

Cio' che va scritto nel paper e' quindi: un binario di quella cella ha sette run invece di otto
perche' l'endpoint ha rifiutato l'ottava, l'analisi congelata lo include mediando su sette, e la
differenza rispetto all'escluderlo e' due decimi di punto percentuale.

**Questo non e' un dato mancante da giustificare: e' il soggetto del paper.** L'endpoint ha
prodotto un'unita' sperimentale mancante — non un punteggio basso, una riga che non esiste — ed e'
esattamente la seconda delle quattro proposizioni che il paper enuncia. Il modo di riportarlo e'
dire quale binario, su quale cella, con quale messaggio, e con quante run e' entrato.

## Cosa NON si fa

Non si insiste. Riprovare significherebbe pagare altre run per un meccanismo sistematico, e
soprattutto significherebbe scegliere quante volte riprovare in base al risultato — cioe'
esattamente la liberta' che la pre-registrazione esiste per chiudere.
