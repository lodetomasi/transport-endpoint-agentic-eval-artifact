# Result card — C2, versione 8 del 2026-08-17 — **corrente**

> **Sostituisce `CARD-C2-v7.md`. Tutti i numeri di questa card vengono dalla ri-raccolta su
> workspace isolati per cella, che `EMENDAMENTO-06` ha designato base primaria PRIMA che
> producesse una riga.** La raccolta originale resta come replica, e le due concordano sui
> quattro criteri congelati. Cinque cambiamenti:
>
> 1. **La base dei risultati e' cambiata**, non i risultati. 5.809 misurazioni nuove, 16 celle su
>    16, zero percorsi di compilazione condivisi contro 30 nell'originale — sotto 451 misurazioni
>    concorrenti che li avrebbero esposti. Il meccanismo e' rimosso per costruzione, non osservato
>    assente.
> 2. **I quattro criteri congelati sono soddisfatti tutti e quattro**: segni 6/8 (soglia 6),
>    famiglia nessun superamento di Holm in nessuna delle due raccolte e sotto entrambe le serie
>    di p, copertura 7/8, decomposizione della varianza riprodotta (0,1%→0,5%, K 705→668).
> 3. **Il confondimento trasporto/batching e' delimitato**, e la v7 lo dichiarava non delimitato.
>    Il braccio a una chiamata per turno da' +0,8pp su haiku e +1,6pp su sonnet, entrambi con
>    l'intervallo che contiene lo zero, contro -9,8pp del trasporto: la perdita del raggruppamento
>    non spiega l'effetto ne' in direzione ne' in ordine di grandezza. Resta un limite superiore e
>    non una stima, perche' il primo rifiuto cambia il comportamento per il resto della traiettoria.
> 4. **Un ottavo meccanismo di censimento**, trovato chiudendo l'ultimo binario: l'endpoint
>    rifiuta il nome del tool che il modello che esso stesso serve ha prodotto, perche' il token
>    di canale del formato di chat non viene separato e non passa la regex della propria API.
>    **Il trasporto testuale e' immune**, il nativo no — cioe' e' un'osservazione sull'asse che
>    questo studio misura.
> 5. **Quattro script producevano i numeri della raccolta sbagliata in silenzio**, con il percorso
>    fissato nel corpo e `--results` ignorato. Due li avevano fissati in DUE punti, cosi' che
>    correggerne uno faceva contare zero righe stampando «0» come se fosse una misura. La
>    correzione e' un parametro d'ambiente unico e una guardia sul denominatore nullo; il controllo
>    che la rende affidabile e' che sulla raccolta originale la catena riproduce i numeri della v7.
>
> **Questa e' la versione da leggere.** Le v1-v7 restano nel deposito perche' IR-5 rende
> `results/` append-only: ogni versione dichiara in testata cosa correggeva della precedente, e
> insieme sono la traccia di quali affermazioni non hanno retto a una verifica. Chi cita una
> versione precedente cita un difetto gia' corretto.
>
> Sostituiva a sua volta `CARD-C2-v6.md`, dopo il gauntlet sui risultati e la decisione di major
> revision dell'area chair (`reviews/results-2026-08-15.md`, piano in `TODO-REVISION.md`).**
> Quattro correzioni, nessuna delle quali ha richiesto una run nuova:
>
> 1. **§4 diceva il falso.** «Nessuna run esaurisce il budget di 12 turni» — sono 68 su 5 880,
>    **tutte native**. La correzione inverte l'argomento sul confondimento del batching invece
>    di aggiungere un numero.
> 2. **§1 apriva con un bound unico**, ±4,9pp, che viene dalla SD pre-registrata e non da questi
>    dati: l'MDE reale va da 0,49pp a 11,59pp e 5 contrasti su 8 superano quel bound. E il peso
>    probatorio — che non è su H1 — ora sta in testa, prima della tabella, invece che nel
>    registro interno.
> 3. **T9 e T10 avevano un secondo p mai citato** (0,0017 e 0,0258). Ora c'è, con la
>    spiegazione che sono **due domande diverse** e non due stime della stessa quantità.
> 4. **Il pavimento della metrica** non era misurato: ora è §5-bis, 0,11 contro 0,64.
>
> Sostituiva a sua volta `CARD-C2-v5.md`. Unica modifica: la v5 diceva che 13pp di esposizione
> differenziale «non spiegano» il salto da 0,1% a 130,7%, che ha il tono di un'esclusione
> formale mentre nessuno script qui la calcola — le due quantita' non sono commensurabili
> senza un modello che le colleghi. Sostituito con un argomento di ordine di grandezza,
> dichiarato come tale. Nessun numero cambia. Trovato dal sesto passaggio dello
> `stats-auditor`.**
>
> **Questa e' la versione da leggere.** Le v1-v5 restano nel deposito perche' IR-5 rende
> `results/` append-only: ogni versione dichiara in testata cosa correggeva della precedente, e
> insieme sono la traccia di quali affermazioni non hanno retto a una verifica. Chi cita una
> versione precedente cita un difetto gia' corretto.
>
> Sostituiva a sua volta `CARD-C2-v4.md`. La v4 asseriva che in C1 l'esposizione al canale del nome era
> simmetrica fra i bracci, 362/362 e 546/546, e ne concludeva che l'apparato non poteva
> contribuire alla divergenza con C2. Il numero era sbagliato: contato con un grep sull'intero
> file di traiettoria, che pesca `tools_offered` — la lista degli strumenti DISPONIBILI,
> presente in ogni riga di turno — invece di `tool_calls`. Restituisce il 100% per costruzione,
> su qualunque braccio. Il conto vero, con la selezione della pipeline confermativa, e' 100%
> contro 86,7%: l'asimmetria c'e', 13,3 punti, e la conclusione della v4 cade. Trovato dal
> quinto passaggio dello `stats-auditor` e riverificato con uno script tracciabile.**
>
> Sostituiva a sua volta `CARD-C2-v3.md`. Tre correzioni, tutte trovate dal quarto passaggio dello
> `stats-auditor`: la v3 scriveva che T1 sta «fra un terzo e la meta'» di rumore quando e' al
> 57,2%, contraddicendo la propria tabella tre righe sopra; non dichiarava che a parita' di
> effetto una SD alta abbassa la potenza invece di alzarla, lasciando leggibile al contrario
> l'osservazione su T3 e T6; e attribuiva alla sola convenzione statistica una divergenza fra
> C1 e C2 che dipende anche dall'apparato. Nessun numero cambia: cambiano tre frasi.**
>
> Sostituiva a sua volta `CARD-C2-v2.md`, che a sua volta sostituiva `CARD-C2.md`; entrambe restano nel
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


**Raccolta chiusa**: 2026-08-15. 16 celle su 16, 5 809 misurazioni valide + 68 righe
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
| T6 | llama — bedrock vs databricks, nativo | 45 | **−7,94pp** | [−14,5, −1,4] | 0,0155 | 0,0050 |
| T3 | haiku — testo vs nativo, databricks | 45 | **−9,83pp** | [−18,2, −1,5] | 0,0181 | 0,0056 |
| T1 | gpt-oss — testo vs nativo, databricks | 45 | **−6,56pp** | [−12,6, −0,5] | 0,0290 | 0,0063 |
| T5 | gpt-oss — bedrock vs databricks, nativo | 45 | +3,26pp | [−0,6, +7,1] | 0,0893 | 0,0071 |
| T9 | eterogeneità fra modelli | 720 | — | — | 0,1011² | 0,0083 |
| T2 | llama — testo vs nativo, databricks | 45 | +2,22pp | [−0,5, +5,0] | 0,1055 | 0,0100 |
| T7 | haiku — bedrock vs databricks, nativo | 45 | +0,22pp | [−0,1, +0,6] | 0,2054 | 0,0125 |
| T8 | sonnet — bedrock vs databricks, nativo | 45 | −0,94pp | [−2,7, +0,8] | 0,2812 | 0,0167 |
| T10 | interazione trasporto × infrastruttura | 720 | −4,12pp | [−10,56, +2,32]¹ | 0,3448² | 0,0250 |
| T4 | sonnet — testo vs nativo, databricks | 45 | −1,00pp | [−5,2, +3,2] | 0,6358 | 0,0500 |

¹ IC non stampato dallo script congelato, calcolato a parte in `results/T10-IC-2026-08-15.txt`
con la stessa convenzione di segno; il modello è l'unità di replicazione (n = 4, t(3) = 3,182).
Col binario come unità sarebbe [−6,44, −1,26], che tratta 180 coppie come indipendenti quando
sono quattro gruppi da 45.

² Lo script congelato stampa accanto un **secondo** p per T9 (**0,0017**) e T10
(**0,0258**), che questa card fino alla v6 non citava. Va detto cosa sono, perché non sono una
seconda stima della stessa quantità: il modello misto usa **entrambe** le infrastrutture e
tratta il modello come effetto casuale a quattro livelli — poco potente per costruzione contro
un'eterogeneità concentrata su un modello solo, come `registro/SUCCESSIONE-03` aveva previsto
per iscritto prima dei dati. Il test «esatto» è invece un'ANOVA a una via **sui soli
Databricks**, che tratta i 45 binari come repliche indipendenti dentro ogni gruppo-modello.
**Due domande diverse su scopi di dati diversi.** In Holm entra il misto perché è quello
pre-registrato in §7, non perché sia l'unico calcolabile.

**Nessun contrasto esce dalla banda ±3pp con IC95 che la esclude.**

### La frase che i dati sostengono

> Nessun contrasto, dopo Holm a m = 10, colloca l'effetto del trasporto o dell'infrastruttura
> fuori dalla banda che la **varianza di quel contrasto** consente — e quella banda va da
> **0,49pp** (haiku fra le due infrastrutture) a **11,59pp** (haiku fra i due trasporti).

**Nessun singolo numero descrive la potenza risolutiva di questo studio, e va letta per
contrasto.** La versione precedente di questa card diceva «una banda di circa ±4,9pp»: quel
valore viene dalla SD conservativa **pre-registrata** (0,1167), e descrive il disegno, non
questi dati. Con le SD osservate, **5 contrasti su 8 hanno un MDE reale superiore** — e i tre
nominalmente significativi lo superano di 1,7-2,4 volte (`results/MDE-REALE-2026-08-15.txt`).

**Non equivale a «nessuna differenza»**: K = 45 non alimenta un test di equivalenza a 3pp, che
ne richiederebbe 99–119. È dichiarato in `PREREGISTRAZIONE.md` §7, prima dei dati.

### Dove cade il peso probatorio, detto prima dei numeri

Non su H1. Il contributo che questi dati sostengono meglio è il **censimento dei meccanismi di
cancellazione** e l'**incrocio trasporto × infrastruttura come disegno**, non la magnitudine di
un effetto di trasporto — che è in larga parte pre-decisa dal seme di C1 e ridimensionata da
BFCL, dove per GPT-4-1106 il testo *vince* di 6pp. È dichiarato prima di vedere l'esito
(`PERCORSO.md` §8), che è l'unico momento in cui vale.

### Le frasi che non si possono scrivere

- «il trasporto testuale peggiora haiku di 9,8pp» — punto nominale non corretto, potenza 21,0%
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
| T3 haiku, trasporto | 0,2774 | 2,38× | **21,0%** |
| T6 llama, infra | 0,2189 | 1,88× | **30,9%** |
| T1 gpt-oss, trasporto | 0,2002 | 1,72× | **35,8%** |
| T4 sonnet, trasporto | 0,1409 | 1,21× | 62,1% |
| T5 gpt-oss, infra | 0,1292 | 1,11× | 69,6% |
| T2 llama, trasporto | 0,0916 | 0,78× | 93,7% |
| T8 sonnet, infra | 0,0585 | 0,50× | 100,0% |
| T7 haiku, infra | 0,0117 | 0,10× | 100% |

**I tre contrasti nominalmente significativi sono i tre meno potenti dello studio.** È la firma
del winner's curse, e va scritta accanto ai punti, non dopo.

Haiku non conserva nemmeno la propria SD fra i due capitoli: 0,0945 in C1, 0,2774 qui. La SD non
è una proprietà del modello trasportabile fra studi né fra assi di contrasto.


### Quale leva morde: rumore o eterogeneita'

`results/SCOMPOSIZIONE-VARIANZA-2026-08-15.txt`. La SD della differenza appaiata ha due
sorgenti, che si riducono con leve diverse: il **rumore** entro-binario con piu' run,
l'**eterogeneita'** vera fra binari solo con piu' binari. Tutte e otto le righe:

| | asse | SD oss | % rumore | K a 3pp | K con run infinite |
|---|---|---|---|---|---|
| T3 haiku | trasporto | 0,2774 | **0,5%** | 671 | **668** |
| T6 llama | **infrastruttura** | 0,2189 | 9,1% | 418 | **380** |
| T4 sonnet | trasporto | 0,1409 | 20,6% | 173 | 137 |
| T1 gpt-oss | trasporto | 0,2002 | 46,1% | 350 | 189 |
| T2 llama | trasporto | 0,0916 | 61,0% | 73 | 28 |
| T5 gpt-oss | infrastruttura | 0,1292 | 93,1% | 146 | 10 |
| T7 haiku | infrastruttura | 0,0117 | 101,4%¹ | 1 | **0** |
| T8 sonnet | infrastruttura | 0,0585 | 110,5%¹ | 30 | **0** |

**La leva dipende dalla cella, non dall'asse.** I due contrasti in cui piu' run non servirebbe
a niente sono T3 e T6, che stanno su **assi diversi** e su modelli diversi; i due in cui la
varianza e' tutta rumore sono contrasti d'infrastruttura, ma un quarto contrasto
d'infrastruttura — T6 — e' il caso di eterogeneita' piu' estremo dopo T3. In mezzo stanno T4 (20,6%),
T1 (46,1%), T2 (61,0%) e T5 (93,1%): distribuiti su tutto l'intervallo invece che addensati,
e nessuno dei quattro si presta a una delle due letture estreme.

Quello che accomuna T3 e T6 non e' l'asse: sono i **due contrasti con la SD osservata piu' alta
e il p nominale piu' basso**. **Non e' un artefatto**: a K fisso il t appaiato vale
delta·√K/SD, quindi a parita' di effetto una SD piu' alta produce un p piu' ALTO e una potenza
piu' BASSA, non il contrario. Qui |delta| e SD crescono insieme, con lo stesso ordinamento sugli
otto contrasti, ed e' proprio la firma di un effetto eterogeneo: grande su alcuni binari, nullo
su altri, con media e varianza che salgono insieme. Dove l'effetto appare piu' grande, e' anche il posto in cui varia
di piu' da un binario all'altro — cioe' e' grande **su alcuni binari e non su altri**, che e'
un'affermazione diversa da «l'effetto medio e' grande», e piu' debole.

Nessuno dei due diventa stimabile con il budget di questo studio: servirebbero **380 e 668
binari** contro i 45 raccolti, e con run infinite non cambierebbe.

¹ Rumore stimato maggiore della SD osservata, cioe' varianza residua negativa. O le run delle
due condizioni non sono indipendenti come il modello assume (stesso binario, stesso stack), o
e' rumore di stima con 45 binari e 8 run. Entrambe le letture portano alla stessa conclusione
operativa, e vanno dichiarate invece che nascoste.

### La calibrazione presa da C1 aveva invertito il meccanismo

`PREREGISTRAZIONE.md` §7, calibrata sui dati di C1, dichiarava: *«per haiku-4-5 l'84% e' rumore
fra run e il pavimento e' K=13»*. Sullo stesso contrasto in C2: **0,1% di rumore, pavimento
K=668**.

**Il confronto isola due cose insieme, e va detto.** Il numero di §7 nasce da uno stimatore
diverso — `potenza.py` usa la media delle SD, questo file la media delle varianze, e divergono
per Jensen proprio quando alcuni binari sono deterministici e altri no. Rifatto su C1 con lo
stimatore coerente (`results/STIMATORI-C1-C2-2026-08-15.txt`), C1 da' **130,7%** di rumore e
pavimento **K=0**: l'inversione si accentua invece di sparire.

Ma i due capitoli differiscono **anche per l'apparato**: in C2 i tre canali di fuga del nome
dell'algoritmo sono chiusi (`registro/EMENDAMENTO-03`), in C1 no. E l'esposizione al canale
**non era simmetrica fra i bracci** nemmeno in C1
(`results/ESPOSIZIONE-LIST-STRINGS-C1-2026-08-15.txt`, script in
`analysis/esposizione_list_strings_c1.py`): sulle prime 8 run valide per binario, cioe' la
stessa selezione della pipeline confermativa di C1, il braccio **nativo chiama `list_strings`
nel 100% delle run (360/360)** e il **testuale nell'86,7% (312/360)** — **13,3 punti** di
differenza. Meno dei 31pp che hanno invalidato il primo lotto di C2 (73% contro 42%), ma non
zero.

**Quindi il confronto C1 -> C2 non separa lo stimatore dall'apparato, e non si puo' sostenere
che l'apparato sia ininfluente.** L'inversione della calibrazione resta il fatto principale, e
la ragione e' di ordine di grandezza e va dichiarata come tale: 13 punti di differenza
nell'esposizione stanno un ordine di grandezza sotto uno scarto di oltre cento punti fra 0,1% e
130,7%, e **non bastano da soli a rendere l'apparato plausibile come causa unica**. Non e'
un'esclusione: le due quantita' non sono commensurabili senza un modello che le colleghi — una
e' un tasso di eventi binari, l'altra una quota di varianza su pass-rate — e quel modello qui
non c'e'. Si riporta come «non separata», mai come «isolata».

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
| haiku / bedrock / native | **0,0000** | **100%** |
| haiku / le altre tre celle | 0,0059–0,0236 | 91–96% |
| sonnet / tutte e quattro | 0,059–0,075 | 62–67% |
| llama / bedrock / native | 0,0546 | 67% |
| llama / databricks / native | 0,1002 | **24%** |
| gpt-oss / bedrock | 0,169–0,200 | 20–24% |
| gpt-oss / databricks | 0,207–0,208 | 20–22% |

Media 0,0890; in media il **56%** dei binari ha otto run identiche.

Due letture, entrambe da riportare:

1. **La varianza run-a-run a temperatura nominale zero è reale e dipende dal modello.** Haiku è
   deterministico, gpt-oss non lo è per niente. L'IC strettissimo di T7 non è potenza alta: è
   assenza di rumore.
2. **Lo stesso modello ha determinismo diverso sui due cloud** — llama 24% su Databricks
   contro 67% su Bedrock sul nativo, ed è l'**unico** dei confronti in cui le bande di Wilson non
   si toccano: $[14,2; 38,7]$ contro $[52,1; 78,6]$. Su gpt-oss la differenza che l'originale
   mostrava (13–16% contro 20–24%) si riduce qui a 20–22% contro 20–24%, e non sostiene la
   claim: la si scrive dove il campionamento la regge, cioè in un confronto su otto. È un altro parametro
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
**La v6 diceva qui che nessuna run esaurisce il budget di 12 turni, e ne concludeva che il
batching è opportunità persa e non turni bruciati. Era falso, e la correzione inverte
l'argomento invece di aggiungere un numero** (`results/BUDGET-ESAURITO-2026-08-15.txt`):

| braccio | traiettorie | al budget pieno | |
|---|---|---|---|
| nativo | 2 955 | **55** | 1,9% |
| testuale | 2 918 | **0** | 0,0% |

Il budget si esaurisce **solo** nel braccio che può raggruppare le chiamate — 68 run su 5 880,
tutte native, nessuna testuale. Per quelle il batching non è un vantaggio inutilizzato: è ciò
che ha permesso di arrivare in fondo. I casi più netti sono su `llama/databricks/native`, dove
`prog45_josephus` tocca il budget su tre run su otto.

**Il confondimento di T3 e T4 è quindi più forte di come la v6 lo descriveva, non delimitato**,
e va riportato così.

**Materiale acquisito** (`analysis/replay_trasporto.py`, celle chiuse). Differenza media di
funzioni acquisite fra nativo e testo, per binario: llama/databricks −0,96 (SD 0,88);
haiku −0,38 su entrambi i cloud; gpt-oss/databricks −0,27; sonnet −0,13; gpt-oss/bedrock +0,00;
llama/bedrock −0,02.

**Accordo di acquisizione fra i due cloud** — quanti dei 45 binari il modello acquisisce
identici su Databricks e Bedrock: haiku 45/45, sonnet 41/45, gpt-oss 40/45, llama 12/45, e
l'ordine coincide con quello di |delta| fra cloud (0,06 / 0,72 / 3,44 / 7,94pp).
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

## 5-bis. Il pavimento della metrica, misurato invece che assunto

`results/BASELINE-ECONOMICO-2026-08-15.txt`, script `analysis/baseline_economico.py`. Richiesto
dal seggio avversariale del gauntlet, che ha attaccato il pass-rate sostenendo che ha un
pavimento raggiungibile senza ricostruire nulla. **L'attacco è riuscito, e il baseline lo
delimita.**

Il baseline non è costato una run: era già nei dati. Alcune traiettorie non chiamano **nessun
tool** — il modello risponde al primo turno senza mai guardare il decompilato — e il loro
pass-rate è esattamente «quanto si prende senza fare il compito».

| | run | pass-rate medio |
|---|---|---|
| senza **nessuna** tool call | 58 | **0,1132** — mediana 0,00, massimo 0,40 |
| con almeno una | 5 756 | **0,6378** |
| | | **+0,5254** |

Il pavimento **esiste e non è zero**: cinque test unitari per binario premiano anche una firma
plausibile. Il caso peggiore è `prog34_fibonacci_memo`, dove su haiku/bedrock/text otto run su
otto prendono **0,40 con zero tool call e un solo turno** — il modello non ha letto una riga di
decompilato e porta a casa due test su cinque.

Ma il confronto è netto, **0,11 contro 0,64**, e la conclusione è che la metrica non è vuota:
è un lower bound **con il proprio pavimento misurato**, che è esattamente come va riportata. Non
serve aumentare il numero di test per binario né pesarli in questo ciclo — costerebbe nuova
raccolta, e il numero già calcolato risponde all'attacco.

## 6. I due lotti invalidati, che sono anch'essi un risultato

`results/README-validita.md`. Nessuno dei due è stato cancellato: `results/` è append-only.

| lotto | costo | causa |
|---|---|---|
| `bedrock_native*` | ~$1,20 | su Bedrock il turno finale senza tool **non è esprimibile**: `toolChoice` ammette `auto`, `any`, `tool` — `none` non esiste. Sopravvivevano solo le run che avevano sottomesso prima del turno finale |
| tutto il lotto del 2026-08-14 | **$17,08**, 2 390 misurazioni | il nome dell'algoritmo raggiungeva il modello da tre canali, e il secondo era **asimmetrico fra i bracci**: nativo 73% delle run contro testuale 42% |

Il secondo lotto resta confrontabile con le stesse celle dopo la correzione, ed è l'unico modo
di misurare quanto valeva il nome.

---

## 6-bis. La ri-raccolta, e i quattro criteri fissati prima di vederla

Sedici celle condividevano la directory di compilazione, perche' la chiave della workdir non
conteneva la cella. La finestra fra scrittura e lettura e' 0,89 s, e la sonda che i dati
ammettevano non decide: righe vicine concordano 8,2 punti **meno** di righe distanti, cioe' il
segno opposto a quello atteso da una collisione, e quel segno si annulla controllando per il
modello. Una sonda che non chiude la domanda non e' una mitigazione, quindi l'esperimento e'
stato rifatto su workspace isolati per cella.

**Le due quantita' vanno separate**, e confonderle sovrastimerebbe il risultato:

| | originale | ri-raccolta |
|---|---|---|
| concorrenza (una riga di altra cella entro 2 s) | 843 | 451 |
| **percorsi di compilazione condivisi** | **30** | **0** |

La concorrenza e' una proprieta' del far girare sedici celle insieme e non sparisce con
l'isolamento; i percorsi condivisi sono il meccanismo, e spariscono. Zero sotto 451 misurazioni
concorrenti che li avrebbero esposti.

**I quattro criteri, congelati per hash in `analysis/confronto_riraccolta.py` prima che la
ri-raccolta producesse una riga:**

| criterio | soglia | esito |
|---|---|---|
| concordanza dei segni | ≥ 6/8 | **6/8** — esattamente al limite |
| esito della famiglia | nessun superamento di Holm | **nessuno**, in entrambe le raccolte e sotto entrambe le serie di p |
| copertura degli IC95 | ≥ 6/8 | **7/8** |
| decomposizione della varianza | stesso ordine di grandezza | **0,1%→0,5%**, K 705→668; T6 9,3%→9,1%, 487→380 |

L'unico contrasto fuori dall'intervallo originale e' T7, il cui IC nell'originale e'
$[-0,2,+0,1]$ perche' quella cella e' quasi priva di rumore: un intervallo cosi' stretto e' un
bersaglio esigente, non un disaccordo sull'effetto. Gli effect size si muovono fino a 3,1pp
(T4, il piu' piccolo e il meno stabile), e nessuna conclusione del capitolo dipende da uno di
essi preso singolarmente.

**Cosa stabilisce la ri-raccolta**, ed e' piu' utile della concordanza: il risultato
confermativo non poggia su un apparato la cui condivisione di risorse non e' verificabile.

## 6-ter. L'ottavo meccanismo: l'endpoint rifiuta l'output del modello che serve

Trovato chiudendo l'ultimo binario della ri-raccolta. Il modello a pesi aperti emette la
chiamata nel proprio formato di chat, che separa i canali di ragionamento con token speciali; il
layer di serving non separa quel token dal nome del tool, che arriva come
`decompile_function<|channel|>commentary` — **undici occorrenze con quel valore esatto** — e
l'API valida il nome che ha appena ricevuto contro `[a-zA-Z0-9_-]+`, non lo accetta, e rifiuta
l'intera richiesta. Non il turno: la traiettoria.

Nessuna delle due parti sta sbagliando: il modello emette il proprio formato nativo, il client
manda una richiesta valida, il validatore fa il suo lavoro. Il serving stack non chiude il
cerchio fra il formato del modello che ospita e la validazione della propria API.

**Due proprieta' lo rendono un meccanismo e non un guasto.** Non e' riparabile dal lato di chi
misura, quindi non smette di accadere: su `prog39_horner` sono servite **quindici run per
ottenerne sette valide**. Ed e' **specifico del trasporto** — sotto il protocollo testuale il
nome non viaggia nel campo `toolUse` e il validatore non lo vede. Il trasporto testuale e'
immune a un meccanismo che uccide il nativo, sull'asse che questo studio esiste per misurare.

Una cella su sedici in entrambe le raccolte: il modello a pesi aperti, sul cloud che non l'ha
addestrato, solo sul trasporto nativo. Quel binario entra nell'analisi con le sette run che ha,
perche' il filtro congelato richiede una lista non vuota e non otto elementi; escluderlo muove
il contrasto di 0,14pp e il suo p di 0,021, e nessuna delle due versioni si avvicina alla soglia
di Holm. Si dichiara invece di scegliere.

## 7. Cosa questa card non contiene

- Nessun test di equivalenza: K = 45 non lo alimenta, ed era dichiarato prima.
- Nessuna stima dell'effetto del trasporto **al netto** del batching: richiederebbe un'ablazione
  con nativo forzato a una chiamata per turno, che non è nei dati raccolti.
- Nessuna interpretazione causale dell'accordo di acquisizione: n = 4.
- Il braccio Azure resta fuori dalla famiglia dei dieci test, in `results/esplorativo/`
  (`registro/EMENDAMENTO-02`).
