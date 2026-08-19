# Emendamento 05 — i p-value che il paper cita sono gli esatti, e lo script congelato resta congelato

**Data**: 2026-08-15, scritto **prima** che un solo p-value entri nella prosa.
**Trovato da**: il revisore metodologico del gauntlet del 2026-08-15, verificato per riesecuzione
da entrambe le sessioni di lavoro, indipendentemente.
**File congelato coinvolto**: `analysis/analyze_c2.py` — **non modificato**.

## Perché un emendamento e non una successione

Una successione documenta il passaggio di un file congelato da un hash a un altro. Qui
**nessun file cambia**: la decisione è di lasciare lo script congelato com'è e di dichiarare
la deviazione. L'hash di `analysis/analyze_c2.py` resta `c478df38…`, e `verifica_hash.sh`
continua a leggerlo identico.

Cambia il piano di analisi — quali p-value il paper cita — e non il codice. Quello è un
emendamento.

## Il fatto

`t_appaiato()` calcola il p-value con un'approssimazione normale del t di Student:

```python
_norm_cdf(abs(t) / (1 + 1/(4*(n-1))))
```

Confrontata con la t esatta a 44 gradi di libertà, su tutti e otto i contrasti appaiati
(`results/P-ESATTI-STUDENT-2026-08-15.txt`, script `analysis/p_esatti_student.py`):

| id | p congelato | p esatto (Student) | differenza |
|---|---|---|---|
| T1 | 0,0289 | 0,0333 | +0,0044 |
| T2 | 0,0893 | 0,0945 | +0,0052 |
| T3 | 0,0143 | 0,0177 | +0,0034 |
| T4 | 0,2529 | 0,2564 | +0,0035 |
| T5 | 0,0862 | 0,0915 | +0,0052 |
| T6 | 0,0169 | 0,0205 | +0,0037 |
| T7 | 0,3201 | 0,3228 | +0,0027 |
| T8 | 0,4443 | 0,4459 | +0,0015 |

**Sottostima in 8 casi su 8**, sempre nella direzione che fa sembrare l'effetto più
significativo. L'IC95 non è toccato: il fattore correttivo di Hill sul t critico coincide con
l'esatto a quattro cifre.

## Perché l'approssimazione c'era, e perché la ragione era buona

Il commento nel file congelato la dichiara: *«scipy non è garantito nell'ambiente di raccolta,
e un'analisi che non gira dove girano i dati è un'analisi che qualcuno rifarà a mano»*. È una
scelta difendibile e dichiarata, non una svista.

Il difetto non è la scelta. È che la deviazione è **sistematica e monodirezionale**, e che
nessuno l'aveva confrontata con un'implementazione di riferimento prima che il gauntlet lo
chiedesse. Un'approssimazione dichiarata e mai misurata è documentazione, non controllo — la
stessa classe di un hash dichiarato e mai riverificato.

## Effetto isolato sulle conclusioni: nessuno, e non è un'assunzione

`analysis/p_esatti_student.py` rifà **Holm su entrambe le serie**, con `m=10` fisso:

- con i p congelati: **0 test superano la propria soglia**;
- con i p esatti: **0 test superano la propria soglia**.

Nessun rango cambia, nessuna conclusione si muove.

Lo script porta il controllo che rende il confronto usabile: **riproduce la formula congelata
e ottiene esattamente lo 0,0143 che `analyze_c2.py` stampa per T3**. Senza quel controllo si
confronterebbero due conti diversi invece della stessa quantità con due formule — che è
precisamente l'errore commesso lo stesso giorno sul conteggio `list_strings` di C1, e corretto
per la stessa ragione.

## Cosa fa il paper

1. **Cita i p esatti.** Sono quelli corretti, e il costo di citarli è nullo perché l'esito non
   cambia.
2. **Riporta entrambe le serie**, in tabella o in appendice dell'artefatto, con questa
   differenza dichiarata in una frase. Non si presenta la serie finale come se fosse sempre
   stata quella.
3. **Non modifica lo script congelato.** Cambiare l'analisi a dati visti è la libertà che la
   pre-registrazione esiste per togliere, e vale anche quando la modifica è un miglioramento:
   la garanzia non è che l'analisi sia la migliore possibile, è che non sia stata scelta dopo
   aver visto i numeri.

## Cosa NON cambia

Il roster, i 45 binari congelati, le 8 run per cella, i 12 turni, la temperatura, la metrica
primaria, la famiglia dei dieci test, `m` fisso a 10, nessuna soglia, gli IC95, il calcolo di
potenza.
