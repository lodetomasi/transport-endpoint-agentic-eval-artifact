# Successione 03 — implementazione di T9 e T10 in `analysis/analyze_c2.py`

**Data**: 2026-08-14, scritto **prima** della modifica.

## Il file

`analysis/analyze_c2.py`

## Il problema

`PREREGISTRAZIONE.md` §7 congela una famiglia di **dieci** test e fissa `m = 10`. T9
(eterogeneità dell'effetto trasporto fra modelli, che è H3) e T10 (interazione trasporto ×
infrastruttura, che è H4) erano nella famiglia ma **non implementati**: lo script li emetteva
con `p` non calcolabile.

Lasciarli così ha due conseguenze, e la seconda è peggiore della prima:

1. le soglie di Holm restano divise per una famiglia di dieci mentre solo otto test possono
   passare — conservativo, ma è la lettura che si era scelta;
2. **H3 e H4 non verrebbero mai testate.** Sono le due ipotesi che chiudono la scappatoia del
   revisore: se l'effetto del trasporto fosse costante, basterebbe dichiararlo e correggerlo;
   se varia per modello e per infrastruttura, non esiste correzione e va misurato ogni volta.
   Sono la parte del contributo che rende la cosa un problema di metodo.

## Cosa T9 e T10 possono vedere adesso

**Niente**, e si verifica dai file su disco. Al momento della scrittura sono raccolte tre
celle, tutte del solo `gpt-oss-120b`:

| cella | valide |
|---|---|
| `gpt-oss-120b/databricks/native` | 374/360 |
| `gpt-oss-120b/databricks/text` | 360/360 |
| `gpt-oss-120b/bedrock/native` | ~117/360 |

- **T9** confronta l'effetto del trasporto **fra modelli**: con un modello solo non esiste.
- **T10** richiede, per uno stesso modello, entrambi i trasporti su **entrambe** le
  infrastrutture. `gpt-oss-120b/bedrock/text` non è iniziata.

Quindi la scelta implementativa non è informata da nulla che i due test misurerebbero. Non è
un'assicurazione — è un fatto verificabile dai CSV nel deposito.

## Cosa cambia

Implementazione di §7 alla lettera, con `statsmodels` 0.14.6 (presente nell'ambiente di
raccolta: un'analisi che non gira dove girano i dati è un'analisi che qualcuno rifarà a mano).

**T9** — modello misto `pass_rate ~ trasporto`, pendenza casuale del trasporto per modello,
binario come componente di varianza; LRT contro la pendenza fissa.

**T10** — termine di interazione `trasporto × infrastruttura` nello stesso modello.

## Due letture, e si riportano entrambe

Il modello misto qui ha **quattro** livelli di modello: una componente di varianza stimata su
quattro gruppi è al limite di ciò che si può stimare, e l'LRT su una varianza al confine dello
spazio dei parametri non è χ² puro — è la mistura che il confine richiede. È lo stesso punto su
cui in C1 lo slope casuale stava al confine (varianza 0,0007, LRT p=0,29 con la mistura e 0,41
col χ²₂ puro).

Perciò accanto a ciascuno si calcola un **test esatto e senza assunzioni di modello**, sulle
stesse quantità:

- **T9 esatto**: ANOVA a una via sulle differenze appaiate per binario, raggruppate per
  modello. Chiede se i quattro effetti del trasporto hanno la stessa media.
- **T10 esatto**: per ogni modello, `d_i = (testo−nativo)_databricks − (testo−nativo)_bedrock`
  sul binario *i*, e t appaiato su `d`. È esattamente l'interazione, senza modello misto.

Il valore che entra in Holm è quello **pre-registrato**, cioè il misto. L'esatto si riporta
accanto, e se i due divergono si dice — non si sceglie.

## Cosa NON cambia

- La famiglia resta di dieci test, `m = 10` fisso, nell'ordine di §7.
- Nessuna soglia si muove.
- Gli otto test da T1 a T8 sono intatti.
- Il rifiuto sui bracci parziali resta.

## Verifica su dati sintetici a risposta nota, e cosa ha rivelato

Sedici celle finte con la difficolta' del binario **condivisa** fra i file — l'appaiamento e'
la struttura che rende informativo il test, e il primo generatore che ho scritto la
distruggeva rigenerandola in ogni file, facendo fallire il controllo per colpa propria.

**Con interazione iniettata** (haiku −12pp su Databricks contro −1pp su Bedrock, gli altri tre
modelli identici sui due cloud):

| | misto (pre-registrato) | esatto |
|---|---|---|
| T9 eterogeneita' | p = 0,0027 | p < 0,0001 |
| **T10 interazione** | **p = 0,1429** | **p < 0,0001** |

**Senza interazione** (stesso effetto trasporto sulle due infrastrutture):

| | misto | esatto |
|---|---|---|
| T10 interazione | p = 0,9508 | p = 1,0000 |

Il negativo e' pulito su entrambi. Il positivo no: **il modello misto pre-registrato manca
un'interazione reale da 11 punti** concentrata su un modello dei quattro, perche' un termine
mediato su quattro gruppi la diluisce; il test esatto la vede.

Questo si dichiara adesso, prima dei dati, e non si corregge cambiando il test: il valore che
entra in Holm resta quello di §7. Ma la lettura del capitolo, se l'interazione ci sara' e sara'
concentrata, sara' che **il test pre-registrato non era potente contro la forma di interazione
piu' plausibile**, e che l'esatto lo era. Saperlo prima significa poterlo scrivere come una
proprieta' misurata del piano invece che come una scoperta imbarazzante a valle.

## Un difetto corretto nel farlo

`inf` e' un nome riservato in patsy, che lo interpreta come infinito: la formula
`pass_rate ~ tr * inf` sollevava `PatsyError`, e un `except Exception` nudo lo trasformava in
"non calcolabile" senza dire perche'. Un test pre-registrato che diventa non calcolabile in
silenzio e' indistinguibile da un test che non c'e'. Colonna rinominata, e la ragione del
guasto ora si stampa.
