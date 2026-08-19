# Emendamento 03 — il nome dell'algoritmo arrivava al modello, da tre canali

**Data**: 2026-08-14, scritto **prima** della modifica.
**Trovato da**: `<revisione-avversariale-dell-apparato>` (il primo canale), poi verificato di persona — e il
secondo e il terzo il critico non li aveva visti.
**Stato**: raccolta **ferma**, 2.390 misurazioni, $17,08 spesi.

## Non è un cambio di disegno: è una decisione vincolante implementata a metà

`PREREGISTRAZIONE.md` §6 dichiara già, fra le decisioni vincolanti derivate da difetti reali di
C1:

> **Tabella dei simboli rimossa** da ogni binario. Con i simboli il binario dice il nome
> dell'algoritmo e il baseline saliva a 0,894.

L'intento c'era. L'implementazione copriva **il binario** e non **il resto dell'apparato**.

## I tre canali

### 1. Il prompt, incondizionatamente

```python
USER_PROMPT = """Binary under analysis: {binary_id}
Ghidra project is already loaded with this binary. Begin your investigation."""
```

`binary_id` è il nome del file decompilato — `prog36_pascal_triangle` — e nomina l'algoritmo da
ricostruire **nel primo messaggio, prima di qualunque tool call**. Identico in
`monolithic.py`.

**Prova, non ipotesi**: il candidato già raccolto per `prog36` contiene
`pascal_triangle[i][j] = ...`, mentre il decompilato che il modello ha visto mostra solo
`FUN_00101020`, `main`, `putchar`, e nessun corpo contiene la parola.

### 2. `.strtab` via `list_strings`, e questo è il peggiore

Le stringhe estratte da Ghidra portano la sezione nel campo `address`. In **`.strtab`** — la
tabella dei simboli — stanno due cose:

```
.strtab::00000095  prog36_pascal_triangle.c     il nome del sorgente, 61 binari su 61
.strtab::000000a8  quicksort                    i nomi delle FUNZIONI originali
```

Il secondo l'ha mancato anche il critico dell'apparato, ed è il più grave: un binario può
non chiamarsi come l'algoritmo e avere comunque `quicksort` fra i simboli.

`.strtab` è **il 42% di tutte le stringhe estratte** (1.998 su 4.708). Il filtro è sulla
sezione, non su una lista di parole: toglie ciò che il linker ha lasciato, e nient'altro.

### 3. L'output del programma — e questo NON si tocca

Dieci binari su 61 nominano l'algoritmo nelle proprie stringhe di `.rodata`:
`NOT_PALINDROME`, `NOT_ANAGRAM`, `LINES=%ld WORDS=%ld CHARS=%ld`.

Sono **il comportamento osservabile che il candidato deve riprodurre**. Toglierle non renderebbe
il compito pulito: lo renderebbe impossibile. È un limite del corpus da **dichiarare**, e
colpisce entrambi i trasporti allo stesso modo, quindi non introduce l'asimmetria del canale 2.

## Perché il secondo non si cancella nella differenza appaiata

I due trasporti incontrano quel canale con frequenza diversa, misurata sulle traiettorie già
raccolte:

| | run che chiamano `list_strings` |
|---|---|
| nativo | **73%** (773/1050) |
| testuale | **42%** (473/1112) |

Il braccio nativo riceve il nome dell'algoritmo **una volta e mezzo più spesso**. Parte di ciò
che il disegno misura come effetto del trasporto sarebbe stato **quanto spesso ciascun trasporto
inciampa nel nome della soluzione** — dentro l'unico asse che lo studio esiste per misurare
pulito.

È lo stesso difetto che in C1 portò il baseline a 0,894, in una forma che la rimozione dei
simboli dal binario non tocca.

## La correzione

| canale | correzione |
|---|---|
| prompt | il modello vede il solo **indice del corpus** (`prog36`), non il nome descrittivo. Il nome pieno resta nelle colonne CSV, nei percorsi e nelle traiettorie |
| `.strtab` | filtrata la **sezione**: 1.998 stringhe su 4.708. Le stringhe di `.rodata` restano tutte |
| output del programma | nessuna: si dichiara, 10 binari su 61 |

`prog36` non ha semantica: è una posizione nel corpus. Un revisore che volesse ricostruire quale
binario sia guarda il CSV, dove il nome pieno c'è.

## Cosa si fa dei dati raccolti

**Tutti invalidati.** Le 2.390 misurazioni sono state prodotte con tutti e tre i canali aperti, e
la contaminazione non è separabile a valle: non esiste un modo di sapere, riga per riga, quanto
del risultato venga dal nome.

Vanno in `results/invalidati/` — spostate, non cancellate — e la raccolta riparte da zero. Costa
i **$17,08** già spesi, su un tetto di $200 e una proiezione di $125.

Riraccogliere è la scelta cara e giusta: dichiarare il canale e tenerlo aperto avrebbe lasciato
un effetto di selezione **asimmetrico fra i due bracci** dentro il contrasto principale, e
nessuna analisi a valle lo separa.

## Cosa NON cambia

- Il roster, i 45 binari congelati, 8 run per cella, 12 turni, la temperatura.
- La famiglia dei dieci test, `m` fisso, nessuna soglia.
- Il calcolo di potenza: la SD viene dai dati di C1, che non sono toccati da questa correzione
  perché anche lì il canale era aperto **in entrambi i bracci confrontati**.

## C1 è affetto in modo identico, e va dichiarato

Stesso template di prompt, agentico **e** monolitico, e gli stessi 61/61 binari.

L'impatto sui suoi numeri principali è però delimitato, e la ragione è precisa: **+35,0pp è un
confronto monolitico contro monolitico sugli stessi binari**, quindi entrambi i bracci ricevono
le stesse stringhe e la fuga si cancella per sottrazione. E l'asimmetria sulle stringhe fra
agentico e monolitico C1 **l'aveva già dichiarata e misurata** — è ciò per cui esiste
`replay_traiettorie.py`, +5,50pp [+1,20, +9,80].

Il fatto nuovo non è l'asimmetria: è **cosa** trasportano quelle stringhe. Per C1 è una frase di
limitazione, con il numero che la delimita — non un ritiro.
