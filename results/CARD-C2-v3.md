# Result card — C2, versione 3 del 2026-08-15

> **Sostituisce `CARD-C2-v2.md`, che a sua volta sostituiva `CARD-C2.md`; entrambe restano nel
> deposito perché `results/` è append-only.** La v2 attribuiva T6 all'asse del trasporto quando
> è un contrasto d'infrastruttura, e ne traeva una dicotomia «i due assi si comportano in modo
> opposto» che le sue stesse otto righe smentiscono. Trovato dal terzo passaggio dello
> `stats-auditor`. La v3 riscrive quel paragrafo con tutte e otto le righe e nessuna dicotomia,
> e dichiara che il confronto con la calibrazione di C1 usa due stimatori diversi.
>
> Rispetto alla v1:
> Unica differenza: la sezione 2 porta la scomposizione rumore-contro-eterogeneità
> (`SCOMPOSIZIONE-VARIANZA-2026-08-15.txt`), che non esisteva quando la v1 è stata scritta e
> che il secondo passaggio dello `stats-auditor` ha richiesto come condizione per chiudere il
> nodo `test`. Nessun numero della v1 cambia: se ne aggiungono.


**Raccolta chiusa**: 2026-08-15. 16 celle su 16, 5 805 misurazioni valide + 68 righe
non-misurazione conservate come record, **$139,58** su un tetto di $200.
**Analisi**: `analysis/analyze_c2.py`, congelata per hash prima che esistesse una riga di dati.
Output integrale in `results/ANALISI-2026-08-15.txt`.

Ogni numero di questa card traccia a un file in `results/`. La card non interpreta: dice cosa
c'è e cosa non c'è.

---

## 1. Il risultato pre-registrato

**Nessuno dei dieci test sopravvive a Holm.** m = 10 fisso, come dichiarato in
`PREREGISTRAZIONE.md` §7.

| id | contrasto | K | delta | IC95 | p | soglia Holm |
|---|---|---|---|---|---|---|
| T3 | haiku — testo vs nativo, databricks | 45 | **−10,44pp** | [−19,0, −1,9] | 0,0143 | 0,0050 |
| T6 | llama — bedrock vs databricks, nativo | 45 | **−8,89pp** | [−16,3, −1,4] | 0,0169 | 0,0056 |
| T1 | gpt-oss — testo vs nativo, databricks | 45 | **−6,39pp** | [−12,2, −0,5] | 0,0289 | 0,0063 |
| T9 | eterogeneità fra modelli | 720 | — | — | 0,0661 | 0,0071 |
| T5 | gpt-oss — bedrock vs databricks, nativo | 45 | +3,44pp | [−0,6, +7,5] | 0,0862 | 0,0083 |
| T2 | llama — testo vs nativo, databricks | 45 | +3,50pp | [−0,6, +7,6] | 0,0893 | 0,0100 |
| T4 | sonnet — testo vs nativo, databricks | 45 | +2,11pp | [−1,6, +5,8] | 0,2529 | 0,0125 |
| T7 | haiku — bedrock vs databricks, nativo | 45 | −0,06pp | [−0,2, +0,1] | 0,3201 | 0,0167 |
| T10 | interazione trasporto × infrastruttura | 720 | −3,85pp | [−12,05, +4,35]¹ | 0,3830 | 0,0250 |
| T8 | sonnet — bedrock vs databricks, nativo | 45 | −0,72pp | [−2,6, +1,2] | 0,4443 | 0,0500 |

¹ IC non stampato dallo script congelato, calcolato a parte in `results/T10-IC-2026-08-15.txt`
con la stessa convenzione di segno; il modello è l'unità di replicazione (n = 4, t(3) = 3,182).
Col binario come unità sarebbe [−6,44, −1,26], che tratta 180 coppie come indipendenti quando
sono quattro gruppi da 45.

**Nessun contrasto esce dalla banda ±3pp con IC95 che la esclude.**

### La frase che i dati sostengono

> Nessun contrasto, dopo Holm a m = 10, colloca l'effetto del trasporto o dell'infrastruttura
> fuori da una banda di circa ±4,9pp per nessun modello misurato.

**Non equivale a «nessuna differenza»**: K = 45 non alimenta un test di equivalenza a 3pp, che
ne richiederebbe 99–119. È dichiarato in `PREREGISTRAZIONE.md` §7, prima dei dati.

### Le frasi che non si possono scrivere

- «il trasporto testuale peggiora haiku di 10,4pp» — punto nominale non corretto, potenza 19,4%
- «l'effetto varia per modello», citando T9 — il test pre-registrato per H3 non lo mostra
- «tre modelli su quattro mostrano un effetto del trasporto» — vero solo a α non corretto, e va
  detto insieme all'esito di Holm, mai in nota

---

## 2. Potenza raggiunta, contro quella pre-registrata

`analysis/potenza.py` calibrava SD 0,1062 (pooled) e 0,1167 (conservativa) **sui soli dati di
C1**, su due modelli e sul solo asse del trasporto: per l'asse infrastruttura non esisteva alcun
pilota.

| contrasto | SD osservata | rapporto | potenza a MDE 4,87pp |
|---|---|---|---|
| T3 haiku, trasporto | 0,2844 | 2,44× | **19,4%** |
| T6 llama, infra | 0,2481 | 2,13× | **24,3%** |
| T1 gpt-oss, trasporto | 0,1950 | 1,67× | **36,7%** |
| T5 gpt-oss, infra | 0,1339 | 1,15× | 66,4% |
| T2 llama, trasporto | 0,1374 | 1,18× | 64,1% |
| T4 sonnet, trasporto | 0,1232 | 1,06× | 73,8% |
| T8 sonnet, infra | 0,0630 | 0,54× | 99,9% |
| T7 haiku, infra | 0,0037 | 0,03× | 100% |

**I tre contrasti nominalmente significativi sono i tre meno potenti dello studio.** È la firma
del winner's curse, e va scritta accanto ai punti, non dopo.

Haiku non conserva nemmeno la propria SD fra i due capitoli: 0,0945 in C1, 0,2844 qui. La SD non
è una proprietà del modello trasportabile fra studi né fra assi di contrasto.


### Quale leva morde: rumore o eterogeneita'

`results/SCOMPOSIZIONE-VARIANZA-2026-08-15.txt`. La SD della differenza appaiata ha due
sorgenti, che si riducono con leve diverse: il **rumore** entro-binario con piu' run,
l'**eterogeneita'** vera fra binari solo con piu' binari. Tutte e otto le righe:

| | asse | SD oss | % rumore | K a 3pp | K con run infinite |
|---|---|---|---|---|---|
| T3 haiku | trasporto | 0,2844 | **0,1%** | 705 | **705** |
| T6 llama | **infrastruttura** | 0,2481 | 9,3% | 537 | **487** |
| T4 sonnet | trasporto | 0,1232 | 33,4% | 132 | 88 |
| T2 llama | trasporto | 0,1374 | 33,8% | 165 | 109 |
| T1 gpt-oss | trasporto | 0,1950 | 57,2% | 332 | 142 |
| T7 haiku | infrastruttura | 0,0037 | 100%¹ | 0 | **0** |
| T5 gpt-oss | infrastruttura | 0,1339 | 110%¹ | 156 | **0** |
| T8 sonnet | infrastruttura | 0,0630 | 141%¹ | 35 | **0** |

**La leva dipende dalla cella, non dall'asse.** I due contrasti in cui piu' run non servirebbe
a niente sono T3 e T6, che stanno su **assi diversi** e su modelli diversi; i tre in cui la
varianza e' tutta rumore sono contrasti d'infrastruttura, ma un quarto contrasto
d'infrastruttura — T6 — e' il caso di eterogeneita' piu' estremo dopo T3. In mezzo, T1, T2 e T4
stanno fra un terzo e la meta' di rumore, e non si prestano a nessuna delle due letture.

Quello che accomuna T3 e T6 non e' l'asse: sono i **due contrasti con la SD osservata piu' alta
e il p nominale piu' basso**. Dove l'effetto appare piu' grande, e' anche il posto in cui varia
di piu' da un binario all'altro — cioe' e' grande **su alcuni binari e non su altri**, che e'
un'affermazione diversa da «l'effetto medio e' grande», e piu' debole.

Nessuno dei due diventa stimabile con il budget di questo studio: servirebbero **487 e 705
binari** contro i 45 raccolti, e con run infinite non cambierebbe.

¹ Rumore stimato maggiore della SD osservata, cioe' varianza residua negativa. O le run delle
due condizioni non sono indipendenti come il modello assume (stesso binario, stesso stack), o
e' rumore di stima con 45 binari e 8 run. Entrambe le letture portano alla stessa conclusione
operativa, e vanno dichiarate invece che nascoste.

### La calibrazione presa da C1 aveva invertito il meccanismo

`PREREGISTRAZIONE.md` §7, calibrata sui dati di C1, dichiarava: *«per haiku-4-5 l'84% e' rumore
fra run e il pavimento e' K=13»*. Sullo stesso contrasto in C2: **0,1% di rumore, pavimento
K=705**.

Non e' una sottostima della grandezza: e' il **meccanismo capovolto**. Il capitolo precedente
diceva che per haiku bastavano piu' run; questi dati dicono che per haiku le run non servono a
nulla. E' il caso piu' netto della tesi del programma — una quantita' che sembra una proprieta'
del modello e' una proprieta' dell'apparato che l'ha misurata.

---

## 3. Temperatura 0,0 non è determinismo

`results/VALIDITA-2026-08-15.txt`, quarto controllo — l'unico dei quattro la cui risposta non
era nota in anticipo. SD fra le 8 run dello **stesso** binario, e quota di binari le cui 8 run
danno un risultato identico:

| cella | SD entro-binario | binari con 8 run identiche |
|---|---|---|
| haiku / databricks / native | **0,0000** | **100%** |
| haiku / le altre tre celle | 0,0015–0,0038 | 98% |
| sonnet / tutte e quattro | 0,065–0,076 | 60–64% |
| llama / bedrock / native | 0,0558 | 62% |
| llama / databricks / native | 0,1322 | **16%** |
| gpt-oss / bedrock | 0,173–0,201 | 20–24% |
| gpt-oss / databricks | 0,232–0,233 | **13–16%** |

Media 0,0936; in media il **55%** dei binari ha otto run identiche.

Due letture, entrambe da riportare:

1. **La varianza run-a-run a temperatura nominale zero è reale e dipende dal modello.** Haiku è
   deterministico, gpt-oss non lo è per niente. L'IC strettissimo di T7 non è potenza alta: è
   assenza di rumore.
2. **Lo stesso modello ha determinismo diverso sui due cloud** — gpt-oss 13–16% su Databricks
   contro 20–24% su Bedrock, llama 16% contro 62% sul nativo. È un altro parametro
   dell'apparato che nessuna valutazione dichiara, ed è confondimento e risultato insieme.

---

## 4. Le covariate dichiarate prima dell'esito

**Chiamate per turno** (`analysis/chiamate_per_turno.py`). Il protocollo testuale ne impone una
per costruzione; nel nativo:

| modello | call/turno | turni con >1 chiamata | |
|---|---|---|---|
| haiku | 1,437 | 38% | confonde T3 |
| sonnet | 1,332 | 33% | confonde T4 |
| gpt-oss | 1,000 | 0% | trascurabile |
| llama | 1,000 | 0% | trascurabile |

Il confondimento è strutturalmente possibile per tutti, ma morde solo dove il modello lo usa.
Nessuna run esaurisce il budget di 12 turni: è opportunità persa, non turni bruciati.

**Materiale acquisito** (`analysis/replay_trasporto.py`, celle chiuse). Differenza media di
funzioni acquisite fra nativo e testo, per binario: llama/databricks −0,96 (SD 0,88);
haiku −0,38 su entrambi i cloud; gpt-oss/databricks −0,27; sonnet −0,13; gpt-oss/bedrock +0,00;
llama/bedrock −0,02.

**Accordo di acquisizione fra i due cloud** — quanti dei 45 binari il modello acquisisce
identici su Databricks e Bedrock: haiku 45/45, sonnet 41/45, gpt-oss 40/45, llama 12/45, e
l'ordine coincide con quello di |delta| fra cloud (0,06 / 0,72 / 3,44 / 8,89pp).
**Esplorativo, n = 4, e non è una conferma indipendente**: ordina come la SD già in tabella di
potenza, ed è compatibile con la sola varianza campionaria.

---

## 5. Attrito

`results/ATTRITO-gpt-oss-2026-08-15.txt`. gpt-oss scarta 2,9–4,6% delle righe contro 0,28–1,1%
degli altri tre, concentrate su 10 binari su 45. Pass-rate dei binari colpiti meno quello dei
sani: databricks/native −0,017, **databricks/text −0,156**, bedrock/native +0,061,
bedrock/text +0,055. Nessuna direzione coerente — un filtro che selezionasse per difficoltà
avrebbe segno costante. Si dichiara come limitazione delimitata con questi quattro numeri.

La ripresa riporta ogni binario ad almeno 8 run valide in tutte e 16 le celle, quindi K = 45
non è degradato.

---

## 6. I due lotti invalidati, che sono anch'essi un risultato

`results/README-validita.md`. Nessuno dei due è stato cancellato: `results/` è append-only.

| lotto | costo | causa |
|---|---|---|
| `bedrock_native*` | ~$1,20 | su Bedrock il turno finale senza tool **non è esprimibile**: `toolChoice` ammette `auto`, `any`, `tool` — `none` non esiste. Sopravvivevano solo le run che avevano sottomesso prima del turno finale |
| tutto il lotto del 2026-08-14 | **$17,08**, 2 390 misurazioni | il nome dell'algoritmo raggiungeva il modello da tre canali, e il secondo era **asimmetrico fra i bracci**: nativo 73% delle run contro testuale 42% |

Il secondo lotto resta confrontabile con le stesse celle dopo la correzione, ed è l'unico modo
di misurare quanto valeva il nome.

---

## 7. Cosa questa card non contiene

- Nessun test di equivalenza: K = 45 non lo alimenta, ed era dichiarato prima.
- Nessuna stima dell'effetto del trasporto **al netto** del batching: richiederebbe un'ablazione
  con nativo forzato a una chiamata per turno, che non è nei dati raccolti.
- Nessuna interpretazione causale dell'accordo di acquisizione: n = 4.
- Il braccio Azure resta fuori dalla famiglia dei dieci test, in `results/esplorativo/`
  (`registro/EMENDAMENTO-02`).
