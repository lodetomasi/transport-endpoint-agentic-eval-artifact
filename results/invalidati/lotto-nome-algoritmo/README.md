# Lotto invalidato — il nome dell'algoritmo raggiungeva il modello

**Data**: 2026-08-14. **Entità**: 2.390 misurazioni, $17,08, 6 celle iniziate su 16.
**Causa e correzione**: [`EMENDAMENTO-03`](../../../registro/EMENDAMENTO-03-nome-algoritmo.md).

## Perché tutto, e non una parte

Il nome dell'algoritmo da ricostruire raggiungeva il modello da **tre** canali, tutti aperti
per l'intera durata di questa raccolta:

| canale | cosa arrivava |
|---|---|
| il prompt | `Binary under analysis: prog36_pascal_triangle`, nel primo messaggio, prima di ogni tool call |
| `.strtab` via `list_strings` | il nome del sorgente (`prog36_pascal_triangle.c`, 61 binari su 61) **e i nomi delle funzioni originali** (`quicksort`, `parse_expr`) |
| output del programma | `NOT_PALINDROME`, `LINES=%ld WORDS=%ld` — 10 binari su 61 |

I primi due sono corretti. **Il terzo resta**, ed è un limite dichiarato del corpus, non un
difetto: quelle stringhe sono il comportamento osservabile che il candidato deve riprodurre, e
toglierle renderebbe il compito impossibile invece che pulito. Colpisce entrambi i trasporti
allo stesso modo.

## Perché non si separa a valle

Non esiste un modo di sapere, riga per riga, quanto del risultato venga dal nome. E il secondo
canale **non si cancella nella differenza appaiata**, perché i due trasporti lo incontravano con
frequenza diversa — misurato su queste stesse traiettorie:

| | run che chiamano `list_strings` |
|---|---|
| nativo | **73%** (773/1050) |
| testuale | **42%** (473/1112) |

Il braccio nativo riceveva il nome una volta e mezzo più spesso. Sarebbe stato un effetto di
selezione **asimmetrico fra i bracci**, dentro l'unico asse che lo studio esiste per misurare
pulito.

## Cosa c'è qui dentro

I CSV per cella e le traiettorie per-turno di tutto ciò che era stato raccolto, incluse le due
celle di `gpt-oss-120b/databricks` che erano **chiuse** e il braccio esplorativo Azure.

Restano perché `results/` è append-only: chiunque può rifare i conti su ciò che è stato
scartato, e confrontare le stesse celle prima e dopo la correzione. È l'unico modo di dire
quanto valeva il nome — una misura che questo lotto rende possibile e che senza di esso non
esisterebbe.
