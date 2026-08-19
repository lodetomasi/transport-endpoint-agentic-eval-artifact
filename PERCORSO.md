# Percorso — cosa è stato fatto, quando, e dove sta

La regola del programma: **nel paper una menzione, nell'artefatto la catena.** Questo è la
catena. Il paper porterà una frase per ciascuna di queste voci; qui c'è la genealogia con le
date, l'evidenza e il file.

Un revisore che confronta i lotti nel deposito trova tutto ciò che segue. Trovarlo senza che
sia dichiarato si legge come occultamento; dichiararlo qui costa una riga e lo disinnesca.

---

## 1. La mappa

| dove | cosa |
|---|---|
| `PREREGISTRAZIONE.md` | ipotesi, falsificatori, famiglia di 10 test, `m` fisso, disegno |
| `HASH-CONGELATI.md` | i 5 file congelati e l'elenco delle successioni |
| `registro/SUCCESSIONE-0N-*.md` | ogni modifica a un file congelato: effetto isolato, hash precedente |
| `registro/EMENDAMENTO-0N-*.md` | ogni modifica al piano che non tocca un file congelato |
| `research/CENSIMENTO.md` | cosa ogni infrastruttura serve, cosa rifiuta, con quale messaggio |
| `analysis/analyze_c2.py` | l'analisi confermativa, scritta **prima** dei dati |
| `analysis/potenza.py` | il calcolo di potenza, rieseguibile |
| `analysis/replay_trasporto.py` | la decomposizione informazione/uso, esplorativa |
| `src/` | harness a due trasporti, tre provider, driver delle celle |
| `configs/` | tariffe con la fonte, elenco congelato dei binari |
| `results/` | CSV per cella + traiettorie per-turno. **Append-only** |
| `results/invalidati/` | lotti scartati, spostati e non cancellati |
| `results/README-validita.md` | il registro: lotto, causa, ricalcolo |

Guardie: `verifica_hash.sh` · `check_cost.sh` · `sorveglia_costi.sh` · `stato.sh`

---

## 2. Le decisioni, in ordine

### 2026-08-13 — il censimento, prima che il piano esistesse

Interrogati gli endpoint invece di leggere la documentazione. Sono emerse **sette celle di
sovrapposizione** fra Databricks e Bedrock, e i primi cinque meccanismi con cui
un'infrastruttura toglie un modello da una valutazione.

Il roster dei bracci pieni — `gpt-oss-120b`, `llama-3.3-70b`, `claude-haiku-4-5`,
`claude-sonnet-4-5` — è stato scelto **dopo** il censimento e per una regola dichiarata, non
per preferenza: enumerabile, e i pesi aperti come cella pulita perché ciascun cloud li ospita
davvero.

### 2026-08-13 — pre-registrazione **e analisi** congelate insieme

È la metà che C1 aveva lasciato aperta. Congelare solo le ipotesi lascia intatta la libertà che
la pre-registrazione doveva chiudere: quale test, su quale sottoinsieme, con quale esclusione.

### 2026-08-13 — la potenza, calcolata e non ipotizzata

Sul contrasto che **questo** capitolo misura: la differenza appaiata per binario, non il σ di
C1 che confrontava bracci diversi su binari diversi.

| | |
|---|---|
| SD entro-modello, pooling | **0,1062** |
| MDE a K=45 | **4,87pp** |
| K per rilevare la banda del falsificatore (±3pp) | **99–119** |

**K=45 non alimenta un test di equivalenza**, e questo ha cambiato il disegno: le ipotesi sono
disgiuntive, e un esito nullo si riporta come «l'IC esclude effetti sopra 4,9pp». Dichiarato
prima dei dati.

### 2026-08-14 — partizione per cloud

Il driver eseguiva le celle in sequenza, quindi un'infrastruttura lavorava e l'altra era ferma.
Partizionando, da 1,8 a 4,7 run/min. Il carico per endpoint **non aumenta**: prima uno riceveva
una cella alla volta e l'altro zero. → `EMENDAMENTO-02` per il ramo Azure, e la partizione in
`SUCCESSIONE-04`.

### 2026-08-14 — tetto da $150 a $200

A $12,12 spesi con proiezione $124,88. IR-6 vieta di alzare il budget **nel momento in cui lo
si sta per toccare**; qui il margine passa dal 20% al 60% mentre la proiezione resta sotto
entrambi i valori. La distinzione è scritta in `EMENDAMENTO-01`, perché fra sei mesi le due
situazioni si assomigliano nel registro e non nei fatti.

### 2026-08-14 — il gauntlet sul disegno, prima dei risultati

Dieci agent: quattro sweep bibliografici, novità, metodologo, avversario, riproducibilità,
chair, gap-hunter. **È il gate più economico del sistema**, e ha trovato le due cose delle
sezioni 3 e 4.

---

## 3. I difetti trovati, e cosa costavano

Ognuno è emerso trattando come sospetto un numero che sembrava a posto — nessuno ha fatto
scattare un test.

| difetto | come è emerso | cosa sarebbe costato |
|---|---|---|
| Le tre colonne di cella nel `writerow` **sbagliato** | smoke su due binari | intestazione a 20 campi, righe a 17: l'analisi leggeva `modello`/`infra`/`trasporto` come `None` |
| `_PRICING_PATH` cercava le tariffe accanto al client | smoke | **5.760 run a costo zero** e un claim sul costo falso |
| Credenziali dei due cloud, meccanismi diversi | smoke | 8 celle per ore, poi `NoCredentialsError` sulla nona |
| La guardia sui prezzi rifiutava **dopo** la chiamata | misura: 4,51 s contro 0,00 s | un modello senza tariffa fatturato e poi respinto |
| `verifica_hash.sh` accettava **un** documento di successione qualunque | controllo negativo | un documento scritto per A avrebbe coperto B in silenzio |
| `pgrep -f "raccogli_c2.py"` cercava su tutta la macchina | **ha ucciso la raccolta vera** | autocattura di `ps \| grep` applicata al kill |
| Il driver **saltava** le celle parziali perché il file esisteva | ripresa dopo il kill | celle corte per sempre |
| `--binari-file` accettava un elenco **vuoto** | file di prova coi soli commenti | zero run in silenzio |
| `inf` è riservato in patsy | T10 «non calcolabile» senza ragione | un test pre-registrato indistinguibile da uno assente |
| `stato.sh` contava i file invece della catena | lettura del pannello | «0/16 chiuse» con una cella a 352/360 |
| **Il turno finale su Bedrock** | gauntlet, poi verificato | § 4 |

E due controlli che sono passati o falliti **per la ragione sbagliata**: un finto driver
«ucciso» che non era mai stato vivo, e un generatore di dati sintetici che distruggeva
l'appaiamento e faceva fallire il test per colpa propria.

---

## 4. Le due cose che il gauntlet ha cambiato

### 4.1 Su Bedrock il turno finale senza tool **non è esprimibile**

Il disegno vuole zero tool all'ultimo turno — documentato da una misura del 2026-08-09: con la
lista ristretta, `gpt-oss-120b` chiama comunque un tool non offerto. Converse **esige**
`toolConfig` se la storia contiene `toolUse`, e `toolChoice` ammette solo `auto`, `any`, `tool`
— **`none` non esiste**, verificato.

Il danno non era dove sembrava. Le 29 righe rotte erano `infra_failure=True` e già escluse da
ogni media. Il problema era **chi sopravvive**: solo le run che avevano sottomesso **prima** del
turno finale. Un secondo effetto di selezione, dentro l'asse che lo studio misura.

→ `SUCCESSIONE-05`. Lotto invalidato e spostato in `results/invalidati/`, cella riraccolta da
zero. **Il vincolo è un risultato**, non un difetto nostro: va accanto ai meccanismi di
cancellazione.

### 4.2 La claim di apertura era falsa

«nessuna valutazione pubblicata dichiara quale trasporto usa» è falsificabile con una
citazione: la **Berkeley Function-Calling Leaderboard** (Patil et al., ICML 2025) pubblica *FC
mode* contro *Prompting mode* per ogni modello. GPT-4-1106: 85,65% testo contro 79,65% nativo —
il testo **vince** di 6pp, direzione opposta al −10,7pp di Haiku.

La claim ristretta e vera: nessuna valutazione **agentica multi-turno su compito downstream**
incrocia il trasporto con l'identità del cloud gestito a parità di pesi, né censisce la
cancellazione di un modello come effetto di selezione di prima classe.

*Da applicare a `PREREGISTRAZIONE.md` §2, `research/CENSIMENTO.md`, `README.md` e
`DIREZIONI.md` §C2 (in `<altro-repository>`) — è una riformulazione, non un cambio di disegno.*

---

## 5. I sei meccanismi di cancellazione

Nessuno cercato: sono emersi **costruendo il campione**. Evidenza verbatim in
`research/CENSIMENTO.md`.

| | caso |
|---|---|
| rifiuto di protocollo | Gemma-3-12B su Databricks, `400` sul multi-turno |
| deprecazione | Llama-3.1-8B ritirato da Azure, ancora servito da Databricks |
| quota inesistente | `gpt-oss-20b`: il catalogo Azure lo offre, il sistema delle quote no |
| disuso | Claude Sonnet 4 e Opus 4.1 su Bedrock, *«not been actively using the model in the last 30 days»* |
| giurisdizione | Llama-4-Maverick su Bedrock, EULA Meta — mentre 3.3 e 3.1 girano |
| **chiamate parallele** | Llama-3.3-70B su Azure |

Il sesto è il solo che **un preflight non può prevenire**: turno 1 passa, turno 2 con una
chiamata passa, e una storia con **due** chiamate nello stesso turno viene rifiutata. Il
censimento lo dichiara sano e la cella muore raccogliendo, quando il modello *decide* di
chiamarne due insieme.

Il caso più stretto resta `gpt-oss-20b`: **tre infrastrutture, tre verdetti.**

**Non sono un tasso.** Il probe ha sondato ~7 modelli e non è un campione casuale: ogni
meccanismo è una prova di esistenza col proprio denominatore dichiarato.

---

## 6. La prima misura arrivata, e non è costata niente

`analysis/replay_trasporto.py` legge dalle traiettorie cosa **ciascun trasporto ha davvero
chiesto**. Su `gpt-oss-120b/databricks`, 45 binari:

| | nativo | testo |
|---|---|---|
| funzioni acquisite, mediana | **1,0** | **0,0** |
| differenza per binario | **−0,73** (SD 0,69) | |
| turni | 3–13 | 2–3 |
| `list_strings` chiamato | sì | **mai** |

Col trasporto testuale il modello **smette di chiamare tool prima**. Se regge sulle altre
celle, l'effetto è in buona parte un deficit di **acquisizione**, non di sfruttamento — e le due
cose hanno rimedi diversi.

**Va letta insieme a un confondimento noto**: `agent_loop.py` esegue *tutte* le tool call di un
turno nativo, mentre il protocollo testuale ne forza **una**. A 12 turni fissi il nativo estrae
più informazione a parità di turni nominali. È lo stesso meccanismo di C1 — budget negato a un
braccio — e va misurato e dichiarato come covariata **prima** di vedere se H1 si conferma.

---

## 6-bis. Il confondimento delle chiamate per turno, misurato prima di H1

`agent_loop.py` esegue **tutte** le tool call di un turno nativo; il protocollo testuale ne
forza **una** (`_parse_text_tool_call` legge una sola riga per risposta). A dodici turni fissi
per entrambi i bracci, un modello capace di chiamate multiple estrae più informazione a parità
di turni **nominali** — strutturalmente lo stesso meccanismo di C1, un budget negato a un
braccio, applicato al trasporto invece che al contesto.

`analysis/chiamate_per_turno.py` lo misura dai log già raccolti, e il pooling fra modelli
**nascondeva la storia**: mediato su tutto è 1,01×, cioè niente.

| modello | nativo, call/turno | turni con >1 chiamata | |
|---|---|---|---|
| `claude-haiku-4-5` | **1,272** | **27%** | confondimento **reale** |
| `gpt-oss-120b` | 1,000 | 0% | trascurabile |
| `llama-3.3-70b` | 1,000 | 0% | trascurabile |

Il confondimento è **strutturalmente possibile ma i modelli devono usarlo perché morda**, e
quasi nessuno lo usa. Dove morde è precisamente il modello con l'effetto di trasporto più grande
del seme di C1 (−10,7pp): per Haiku parte di quel delta può essere budget di chiamate, non
trasporto.

Si riporta come **covariata dichiarata**, misurata prima che i dati confermativi di Haiku
esistano — non si corregge cambiando il disegno pre-registrato. Il numero di Haiku poggia su 92
turni ed è provvisorio; si ricalcola a cella chiusa.

## 6-ter. Il nome dell'algoritmo arrivava al modello — e la raccolta è ripartita da zero

**2026-08-14.** Trovato da `<revisione-avversariale-dell-apparato>`, verificato di persona, e due dei tre canali il
critico non li aveva visti. → `registro/EMENDAMENTO-03-nome-algoritmo.md`.

| canale | stato |
|---|---|
| il prompt: `Binary under analysis: prog36_pascal_triangle` | corretto — il modello vede `prog36` |
| `.strtab` via `list_strings`: nome del sorgente **e nomi delle funzioni** | corretto — filtrata la sezione, 1.998 stringhe su 4.708 |
| output del programma: `NOT_PALINDROME`, `LINES=%ld WORDS=%ld` | **resta**, dichiarato: 10 binari su 61 |

Il secondo **non si cancella nella differenza appaiata** — nativo 73% delle run contro testuale
42%. Sarebbe stato un effetto di selezione asimmetrico dentro l'asse che lo studio misura.

**2.390 misurazioni e $17,08 invalidati**, spostati in
`results/invalidati/lotto-nome-algoritmo/`. Restano confrontabili con le stesse celle dopo la
correzione: è l'unico modo di dire quanto valeva il nome.

**C1 è affetto, e l'asimmetria favorisce il braccio che vince**: il monolitico riceve le stringhe
sempre (il nome sta in posizione 50 dei primi 60, su 61/61), l'agentico nel 69% delle run. Ma
`replay_traiettorie.py` la chiude per costruzione, e il prompt singolo resta avanti di **+5,50pp
[+1,20, +9,80]**. `+35,0pp` non è toccato: è monolitico contro monolitico sugli stessi binari.

## 7. Il conto

| | |
|---|---|
| C1, raccolta (25.382 run) | 178 € |
| C1, gauntlet di review | 21 € |
| C2, previsto a chiusura | ~115 € |
| **totale sui due studi** | **~335 €** su un vincolo di 500 € |

Riconciliato **contro la fattura**, non contro le tariffe dichiarate: `gpt-oss-120b` su
Databricks, $4,1272 dai CSV contro $4,1287 in `system.billing.usage` — **scarto 0,04%**.

Due trappole nella lettura della fattura, in `configs/README.md`: Cost Explorer ha ore di
ritardo, e i modelli Anthropic su Bedrock **non fatturano sotto «Amazon Bedrock»** ma sotto
servizi propri. Filtrare sul nome singolo mostrerebbe quasi zero proprio dove stanno $104 dei
$125.

---

## 7-bis. La raccolta è chiusa, e il primo verdetto è sull'apparato

**2026-08-15.** 16 celle su 16, 5 805 misurazioni, **$139,58** su un tetto di $200. L'analisi
congelata gira e **nessuno dei dieci test sopravvive a Holm** — il p più piccolo è 0,0143 contro
una soglia di 0,0050. Nessun contrasto esce dalla banda ±3pp con IC che la esclude.

Gli effetti puntuali però non sono piccoli: **T3 −10,44pp** (haiku, trasporto) replica il −10,4pp
di C1 su un altro apparato e dopo aver chiuso tre canali di fuga; **T6 −8,89pp** (llama, fra i due
cloud a modello e trasporto fissi) è l'effetto che questo capitolo esisteva per cercare. Le tre
cose vanno dette insieme, e l'ordine conta: `results/CARD-C2-v7.md`.

Lo `stats-auditor` ha risposto **FAIL condizionato**, e la ragione è la più scomoda possibile: la
SD osservata arriva a **2,44×** la conservativa pre-registrata, e i tre contrasti nominalmente
significativi (T3, T6, T1) sono **esattamente i tre meno potenti** dello studio — potenza 19,4%,
24,3%, 36,7% contro l'80% dichiarato. È la firma del winner's curse, e va scritta accanto ai
punti invece che dopo.

### Temperatura 0,0 non è determinismo, e non lo è in modo diverso su ogni stack

Il quarto test di validità (`analysis/validita.py`, nuovo) era l'unico dei quattro senza risposta
nota. Fra le 8 run dello **stesso** binario:

| | SD entro-binario | binari con 8 run identiche |
|---|---|---|
| haiku | 0,0000–0,0038 | **98–100%** |
| sonnet | 0,065–0,076 | 60–64% |
| llama | 0,056–0,132 | 16–62% |
| gpt-oss | 0,173–0,233 | **13–24%** |

In media il 55% dei binari ha otto run identiche. Due conseguenze: l'IC strettissimo di T7
(−0,06pp, [−0,2, +0,1]) **non è potenza alta, è assenza di rumore**; e lo stesso modello ha
determinismo diverso sui due cloud — gpt-oss 13–16% su Databricks contro 20–24% su Bedrock. È un
altro parametro dell'apparato che nessuno dichiara, ed è confondimento e risultato insieme.

### Una cosa che sembrava un meccanismo e non lo è

L'accordo di acquisizione fra i due cloud (haiku 45/45, sonnet 41/45, gpt-oss 40/45, llama 12/45)
ordina monotonamente il |delta| di pass-rate fra cloud. Sembrava spiegare *perché* l'infrastruttura
sposta il numero. **Ordina però esattamente come la SD già in tabella di potenza**, ed è compatibile
con la sola varianza campionaria: più instabilità run-a-run, stima più rumorosa. Esplorativo,
n = 4, e **non** una conferma indipendente. Trovato dall'auditor, non da noi.

---

## 8. Cosa resta aperto

1. ~~**Riformulare la claim** dopo BFCL~~ — **fatto il 2026-08-15**,
   [`EMENDAMENTO-04`](registro/EMENDAMENTO-04-claim-dopo-bfcl.md), applicato a `README.md` e
   `research/CENSIMENTO.md`. **Non** a `PREREGISTRAZIONE.md`, che è congelata e ora anche locked
   per hash: riscrivere una claim congelata perché una revisione l'ha falsificata è la libertà
   che la pre-registrazione esiste per togliere. La verifica IR-1 ha corretto anche
   l'attribuzione — il confronto FC/Prompt sta nella **leaderboard** e in una discussione del
   repo, non nel paper ICML, e GPT-4-1106 non è più listato in V4.
2. ~~**Misurare le chiamate per turno**~~ — **fatto**, ricalcolato a celle chiuse: haiku 1,437
   call/turno (38% dei turni con più di una), sonnet 1,332 (33%), gpt-oss e llama 1,000. Confonde
   T3 e T4, non T1 e T2.
3. **Related work**: **quattro** citazioni dirette, non quindici deboli. Alle tre di partenza
   (BFCL, *Silent Hyperparameter*, *AgentCompass*) si aggiunge **The Leaderboard Illusion**
   (arXiv:2504.20879, Singh et al., 29 apr. 2025), trovata dal revisore di novità e verificata
   per fetch il 2026-08-15. È il vicino più prossimo alla terza gamba della claim: tratta già la
   rimozione differenziale come effetto di selezione — *«proprietary closed models are sampled at
   higher rates and have fewer models removed from the arena than open-weight and open-source
   alternatives»* — con i numeri (19,2% e 20,4% dei dati dell'arena a Google e OpenAI, contro
   29,7% a **83** modelli open-weight messi insieme).
   **Il livello causale è diverso e va detto così**: là è selezione curatoriale e politica su
   un'arena pubblica, qui è **rifiuto tecnico dell'infrastruttura di serving** — un 400, una
   quota che non esiste, una deprecazione. Ma un revisore che lo conosce chiederà perché non
   c'è, esattamente come è successo con BFCL.
4. **Dichiarare che la claim è stata ristretta due volte**, e che tolte tutte le clausole resta
   contenuto non banale. Segnalato dallo stesso revisore: una claim che si restringe ogni volta
   che si trova un controesempio è un pattern che un referee riconosce, e conviene affrontarlo
   nel testo invece di aspettarlo.
5. **Il braccio esplorativo Azure non ha dati validi** — invalidato col lotto del nome e mai
   riraccolto (`results/VALIDITA-BRACCIO-AZURE-2026-08-15.md`). `README.md` lo annuncia ancora
   come raccolto.
4. Correggere l'etichetta «test esatto sulle stesse quantità» per T9: il misto usa entrambe le
   infrastrutture, l'esatto solo Databricks.
5. Ricondurre a una sola fonte il seme di C1: `PREREGISTRAZIONE.md` §1 dice «+3,0 / −10,4»,
   `DIREZIONI.md` di `<altro-repository>` dice «+2,8 / −10,7». `potenza.py` ricalcola dai CSV, quindi la potenza non è
   affetta — ma il testo deve dire un numero solo.
6. L'immagine Docker nel deposito.

**Verdetto del chair, condizionato a 1–3**: registered report. Il peso probatorio cade sul
censimento delle cancellazioni e sull'incrocio trasporto × infrastruttura, **non su H1** — che è
in larga parte pre-deciso dal seme di C1 e ridimensionato da BFCL. Va detto prima di vedere
l'esito, non dopo.


---

## 9. Riprendere da qui

**Stato al 2026-08-15, sera.** Raccolta **chiusa**: 16 celle su 16, 5.805 misurazioni,
$139,58 di un tetto di $200. Il grafo di ricerca è al nodo `write`, con `test` e
`gate_evidence` chiusi alle spalle. Il paper è scritto: 11 sezioni, 4 tabelle, 2 figure.

```bash
cd ~/c2-tool-transport
python3 ~/<tooling>/graph.py status    # dove siamo sul grafo
./verifica_hash.sh                                          # i 5 congelati sono intatti?
python3 ~/<tooling>/paper.py scan paper --strict
```

**Non riavviare la raccolta.** È finita, la sorveglianza ha rilevato la quiete da sé e ha
chiuso con «spesa finale $139,5774 di $200». Le istruzioni di riavvio che stavano qui prima
sono state rimosse perché eseguirle ora produrrebbe run che nessuna cella aspetta.

### Cosa resta, in ordine

1. **`gate_paper`**: il gauntlet completo su `paper/`, `/<gauntlet-di-revisione> paper/ paper`. Pretende
   `ironrules.py verify` a zero, zero Fatal aperti, verdetto di riproducibilità
   *Reproducible*, e decisione accept o minor-revision.
2. **Il conteggio delle pagine**, che nessuno ha ancora fatto: `pdflatex` non è nella shell di
   questa sessione. Il limite è **10+2** (<sede-anonima>, track Agentic AI4SE, double-anonymous). Con
   676 righe di contenuto è probabile che si sfori. **Il taglio non deve cadere sul censimento**
   — è dove il chair colloca il peso probatorio, e in C1 la sezione analoga fu compressa a mezza
   pagina dopo che un revisore l'aveva chiamata «un contributo a sé». I candidati sono la
   genealogia (che nel paper vuole una menzione, non una narrazione) e la sezione artefatto.
3. **La tensione del titolo**, dichiarata e non risolta: il sottotitolo promette *how much of an
   agent's score is bought by the interface*, e la risposta confermata è che con questa potenza
   non è misurabile. L'abstract lo disinnesca alla seconda frase, ma un referee che legge solo
   titolo e abstract vede una promessa e mezza mantenuta.
4. **La convenzione sui nomi dei vendor**: Census non li nomina, per il doppio anonimato. Se
   Method e Design li nominano, una delle due cede — non si possono avere entrambe.

### Cosa NON rifare

- La raccolta, l'analisi congelata, il calcolo di potenza, la famiglia dei dieci test.
- Il censimento: sei meccanismi verificati e datati.
- Le citazioni: nove chiavi, tutte fetchate, zero orfani in entrambe le direzioni.

### Le cinque cose che questa giornata ha insegnato, e che costerebbe rifare da capo

1. **Tutti gli errori stavano in numeri nuovi asseriti in prosa senza uno script dietro.** Le
   tabelle congelate hanno retto a tre ricalcoli indipendenti senza una correzione. Sei
   passaggi di audit, sei difetti, tutti nella stessa classe. La regola che ne segue —
   *nessun numero entra in prosa senza un file in `results/`, **committato**, che lo produca* —
   ha la sua clausola finale perché è passata di lì l'unica affermazione falsa della giornata.
2. **Un controllo può passare per la ragione sbagliata.** Il parser delle figure leggeva 3
   contrasti su 8 perché il regex non accettava gli estremi positivi degli intervalli; i 3 che
   restavano erano esattamente i 3 nominalmente significativi, e il controllo a risposta nota
   confermava. Un controllo che non sa quante righe *dovrebbe* leggere non è un controllo.
3. **Il noise floor si misura sulla classe dei difetti, non sulla loro dimensione.** Dopo
   quattro passaggi con un finding ciascuno sembrava rumore del revisore; il quinto ha trovato
   un numero inventato da un grep difettoso. Contare i findings non basta: contano di che tipo
   sono.
4. **Le guardie hanno fermato tre volte chi le ha scritte.** Due mascheramenti di exit code e
   un lock preso a nome di un altro. Nessun falso positivo, tranne uno istruttivo: la guardia
   IR-3 ha bloccato un comando perché la stringa `|| true` compariva *dentro il testo* di una
   nota che descriveva il blocco precedente.
5. **`results/` non è append-only come lo descrivevamo.** L'hook blocca pattern di comando
   noti, non la sovrascrittura per redirezione: `echo >` tronca un CSV con exit 0. La garanzia
   reale è la cronologia git committata, e il documento va corretto perché oggi promette una
   proprietà tecnica che ha solo in parte.

---

## 10. Il gauntlet sui risultati, in una tabella

2026-08-15, quattro seggi in isolamento più l'area chair. Decisione: **major revision**, tutte
le voci chiudibili a costo-dati-zero. Verbali in `reviews/reviewer-*-results-2026-08-15.md`,
meta-review in `reviews/results-2026-08-15.md`, piano in `TODO-REVISION.md`.

| seggio | verdetto | il finding che è costato di più |
|---|---|---|
| metodologo | 3/5 | `SUCCESSIONE-04` dichiarava che una risorsa condivisa si sarebbe vista come `infra_failure`; il codice mostra che quel campo è letto **prima** che la funzione che potrebbe sporcarlo venga chiamata |
| avversariale | 6 attacchi, 4 riusciti | il pass-rate ha un pavimento raggiungibile senza leggere il decompilato — e la card affermava il falso sul budget dei turni |
| riproducibilità | parzialmente riproducibile | ha preparato il deposito e ci ha eseguito dentro uno script: crashava, perché la redazione riscrive un percorso e non c'era override |
| novità | thin but real | due vicini mai citati, di cui uno dichiara di **non essere riuscito** a riempire la casella che il nostro censimento riempie sei volte |
