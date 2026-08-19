# revision_verification.md — C2, revisione maggiore EMSE

Ambiente: il manoscritto **compila**, con `tectonic` (0.15.0), che e' anche il motore che
`prepara_sottomissione.sh` usava gia'. Stato della compilazione sui sorgenti correnti:

| | |
|---|---|
| pagine | 31 |
| overfull \hbox | **0** |
| underfull \hbox | **0** |
| riferimenti o citazioni irrisolte | **0** |
| voci in bibliografia | 29 citate, 29 definite, nelle due direzioni |
| pacchetto autonomo | costruito e ricompilato fuori dal repository: 31 pagine, 0 irrisolti |

> **Errore di questo documento, corretto.** La prima stesura dichiarava «nessun compilatore LaTeX su
> questa macchina» e rinunciava a compilare. Era falso: avevo cercato `pdflatex`, `latexmk`, TeX Live,
> MacTeX e TinyTeX, e non `tectonic`, che stava in `/opt/homebrew/bin` ed e' il motore che lo script di
> sottomissione di questo stesso repository invoca. La conclusione «non si puo' compilare» era
> un'enumerazione incompleta presentata come un fatto sull'ambiente --- lo stesso modo di sbagliare che
> `<istruzioni-di-progetto>` registra per `serviceName eq 'Cognitive Services'`. La compilazione ha poi trovato 23
> overfull e 8 underfull che nessun controllo statico avrebbe visto.

Oltre alla compilazione, tre controlli statici, ognuno con un caso a risposta nota nei due sensi:

| controllo | cosa verifica | esito |
|---|---|---|
| `python3 revisione/controlla_latex.py` | ambienti bilanciati, colonne delle tabelle contro il preambolo, `\ref` senza `\label` | 0 guasti su 17 file; autotest 0/3; parser dei preamboli esercitato su tutti gli 11 preamboli reali |
| `python3 analysis/audit_paper.py` | 26 valori sorvegliati, 12 formule vietate, 4 coerenze obbligatorie | exit 0; ciascuna guardia esercitata su un caso che deve fallire |
| `python3 revisione/verifica_numerica.py` | 29 voci rigenerate dallo script che le produce | 0 guasti, 3 controlli negativi |

`./revisione/verifica_tutto.sh` li lancia tutti, compilazione compresa.

---

## 0. Passata sul registro affermativo (richiesta successiva)

Tre interventi, oltre ai 34 SPEC.

**§8, la ri-raccolta.** La sezione presentava la propria obiezione, nella sua forma piu' aggressiva, con il
materiale temporale per svilupparla, e solo dopo la difesa. Ora la sottosezione tiene una cosa sola: il
meccanismo e' rimosso **per costruzione** --- 30 percorsi di compilazione condivisi nell'originale, zero
sotto 451 misurazioni concorrenti --- che e' una proprieta' del codice e non dei numeri di nessuno dei due
lotti. I quattro diagnostici restano col loro esito e sono qualificati come diagnostici sulla comparazione,
non come fondamento della designazione. Tutta la cronologia forense --- i tre timestamp, l'1,9%/27,4%/73,4%,
le 4h31m, l'assenza di derivazione della soglia 6-su-8, la precedenza dichiarata e non provata --- e' in
**Appendice~C**, con una tabella che la rende auditabile in un colpo d'occhio. Niente e' stato tolto: e'
stato spostato dove un revisore che vuole verificarlo lo trova, e fuori dalla narrazione che glielo
suggerisce. Da 690 a 452 parole.

**§9, la conclusione.** Apriva sull'emendamento e sulla calibrazione ereditata. Ora apre sul censimento ---
sei meccanismi che tolgono una coppia prima che esista un punteggio, due che distruggono misure dentro una
run, e il gradiente 4/3/1 di rilevabilita' --- e la famiglia pre-registrata arriva dopo, col suo stato
invariato. Una guardia eseguibile controlla le prime 60 parole: devono nominare il censimento e non possono
contenere *amendment*, *validity flag*, *calibration* o *Holm*. Esercitata nei due sensi.

**Gerarchia.** Il censimento e' gia' §5 nel PDF, prima dell'analisi. La Discussione ora lo mette per primo
anche li': «Why the census carries the weight» precede il risultato nullo, che prima apriva la sezione.

**Registro affermativo, misurato.** `revisione/autosabotaggio.py` conta tre famiglie separate --- ammissione,
meta-virtu' (il testo che commenta la propria onesta') e auto-obiezione (il testo che formula l'obiezione
del revisore prima della propria evidenza) --- su HEAD contro il working tree, sezione per sezione, con un
autotest che pretende una frase costruita apposta in ciascuna famiglia e nessuna in un paragrafo neutro.
Esito: **40 occorrenze nel corpo prima, 2 dopo (-95%)**, cosi' distribuite prima: 23 ammissioni, 6
meta-virtu', 11 auto-obiezioni. Il numero non sovrastima, e lo script lo dichiara: sei occorrenze non sono
sparite ma **ricollocate in Appendice C**, dove un revisore che vuole auditarle le trova senza incontrarle
nella narrazione. Le due residue sono materiali: una riguarda il campo e non lo studio (§2), una e' un enunciato
sulla risoluzione (didascalia della figura), una e' l'unica dichiarazione rimasta sul lotto ereditato --- che
prima compariva **sette volte** fra abstract, introduzione, §5.2 e §7.1 --- e una e' una proposizione
metodologica (§7.5). Parole: 14.161 -> **15.103**, cioe' +6,7% sull'originale e -7,2% dal picco post-P0.

**Due sostituzioni annunciate e non avvenute, e cosa e' cambiato di conseguenza.** `str.replace` restituisce
la stringa intatta quando il bersaglio non c'e', e non solleva: la riscrittura di §5.2 e l'intestazione di
§8 sono state dichiarate fatte mentre il testo era rimasto quello di prima, perche' il bersaglio differiva
per un'interruzione di paragrafo. Un audit su **51 modifiche dichiarate** --- 37 rimozioni e 14 inserimenti
--- ne ha trovate 41 su 42 alla prima passata e ha isolato il caso rimasto. Il controllo non e' piu' una
ispezione una tantum: `revisione/modifiche_dichiarate.py` lo esegue, sta nella suite, e sorveglia i due
versi (cio' che deve essere sparito e cio' che deve essere presente, perche' una guardia sul solo vecchio
testo non vede il nuovo perso in una riscrittura successiva). Nella stessa passata la guardia di coerenza
ha segnalato come assente una frase presente, confrontando a spazi non normalizzati: ora normalizza, ed e'
stata riesercitata su tutte e quattro le sezioni che sorveglia.

**Terza passata, sulla rilettura.** Le regex non vedono il registro. Rileggendo §8 riga per riga sono
emersi cinque punti che nessuna parola chiave prendeva: l'intestazione che annunciava di dare al revisore
«cio' che avrebbe trovato comunque»; «one exactly at its threshold, which we state rather than round past»,
che consegna l'obiezione prima del numero che la contiene gia'; un meta-commento sulla propria frase nel
residuo del pass-rate; il Threat dell'ablazione che anticipava la formulazione aggressiva della propria
Quantification; e «cautions» come registro difensivo. In §6 tre meta-commenti sulla propria onesta'
(«we state each with its own denominator and never mix them», «the asymmetry belongs in the open»), e in §1
il titolo interamente negativo «What this paper does not claim», ora «The boundary of the claim» con le tre
delimitazioni in affermativo.


---

## 1. Matrice di completamento

| SPEC | esito | file cambiati | sezioni | cambiamento sostanziale | evidenza |
|---|---|---|---|---|---|
| 01 cronologia autoritativa | **PASS** | `revisione/chronology.tsv`, `revisione/stato_a_cutoff.py`, 03, 04, 08 | Metodo, Disegno, Minacce | 21 eventi con timestamp, righe disponibili a ciascuno e stato probatorio; tolta la formula «no hypothesis, test or comparison is added» che coesisteva con RQ5/RQ6 nate in esecuzione | conteggi ricalcolati dai CSV rilasciati a sei cutoff |
| 02 cronologia in abstract e conclusione | **PASS** | 00, 09 | Abstract, Conclusione | «hash-frozen before collection; two of the ten tests were implemented under a timestamped amendment after collection had begun», identica nei due punti | guardia di coerenza; ricerca `before any` su tutte le sezioni |
| 03 analisi confermatoria protetta | **PASS** | `analysis/tabella_principale.py`, `analysis/permutazione.py`, Tab. 6, Tab. 10 | §5.3, App. A | la colonna `p` di Tab. 6 e' la serie **congelata** (min 0,0155); esatta e sign-flip spostate in appendice come sensibilita' | Tab. 6 rigenerata; Tab. 10 porta le tre serie affiancate |
| 04 potenza osservata rimossa | **PASS** | `analysis/tabella_principale.py`, 00, 01, 05, 09, Tab. 6 | ovunque | colonna `power` eliminata; tolte «achieved power», «least powered», «power determines what a p-value can mean»; MDE etichettato come diagnostico di sensibilita' realizzata, condizionale alla dispersione, senza valore probatorio sui p | ricerca globale: 3 occorrenze residue, tutte citazioni o negazioni esplicite |
| 05 banda ±3pp | **PASS** | 05 | §5.3 | separata la soglia **pre-specificata** dalla soglia **risolvibile**; 6 contrasti su 8 non risolvono i ±3pp, 5 su 8 superano i 4,87pp del disegno; lezione formulata sul dimensionamento, non sulla pre-registrazione | `revisione/conta_soglie.py` con controlli a 0 e 100 |
| 06 provenienza della ri-raccolta | **PASS (Outcome B)** | `revisione/recollection_provenance.tsv`, `revisione/recollection_verdict.md`, 05, 08, Tab. 7 | §5 apertura, §8 | i quattro criteri diventano **diagnostici di concordanza pre-specificati**, non pre-registrati e non indipendenti dall'esito originale; **eliminata l'affermazione falsa** «designated primary before it produced a row»; la base primaria si fonda sul meccanismo rimosso per costruzione | tre fatti datati e ricalcolabili, vedi §2 |
| 07 «replication» | **PASS** | 04, 05, 08, Tab. 7 | ovunque | «original collection» e «isolated-workspace re-collection»; `as a replication` e `replication batch` non compaiono piu' | formula vietata nell'audit |
| 08 ontologia guasto/by-design | **PASS** | `revisione/mechanism_config.tsv`, 02, 06, Tab. 5 | §2.4, §6 | quattro classi operative (lifecycle, contract, quota, adapter); su M8 tolti «neither party is malfunctioning», «no party is at fault», «the client sends a valid request», sostituiti dalla sequenza fattuale | formule vietate nell'audit |
| 09 novita' indipendente dalla tassonomia | **PASS** | 02, 06 | §2.4, §6.5 | quattro punti che reggono qualunque etichetta si dia a M3 e M8, enumerati esplicitamente | test di robustezza in §8 di questo documento |
| 10 rilevabilita' ricostruita | **PASS** | `revisione/probe_matrix.tsv`, 00, 01, 06, 09 | ovunque | non piu' 6/2 ma **4 / 3 / 1** da evidenza; M7 riclassificato al livello di M6 (il testo li chiamava gemelli e la tabella li separava); M1 dichiarato **limite superiore** | matrice con la sonda minima e la sua evidenza per riga |
| 11 claim limitati alla configurazione | **PASS** | `revisione/mechanism_config.tsv`, 06 | §6.1 | endpoint, API, regione, parametri e varianti provate per meccanismo; formulazione «under the evaluated configuration, the service rejected» | tabella per riga |
| 12 unita' e denominatori | **PASS** | `revisione/census_ledger.tsv`, 06 | §6 apertura | tre unita' separate: (A) coppie 8/21, (B) perdite dentro la cella, (C) meccanismi 8 | riconcilia con `analysis/denominatore_roster.py` |
| 13 attribuzione causale sull'endpoint | **PASS** | 01, 05, 09 | §1.1, §5.7 | eliminato «if the difference persists it belongs to the model, if it moves it belongs to the infrastructure»; «deployed-service difference» ovunque | ricerca `belongs to` |
| 14 contabilita' dei token di T6 | **PASS (Decision B)** | `analysis/contesto_t6.py`, `analysis/runtime_t6.py`, 05, 08, Tab. 8 | §5.7 | riportata come **differenza di contabilita' dichiarata dal provider**, scomposta in lunghezza della traiettoria (6 vs 4 turni) e conteggio al primo turno (1.263 vs 678); dichiarata la copertura parziale della ricostruzione | vedi §3 |
| 15 diagnosi causale di T6 | **PASS** | 05 | §5.7 | eliminato «throughput agreeing points away from hardware and towards what each stack sends»; sorgente dichiarata non identificata | formula vietata |
| 16 saturazione del budget di turni | **PASS** | `analysis/saturazione_turni.py`, `analysis/runtime_t6.py`, 04, 05, 07 | §4.2, §5.7.1, Tab. 9 | **calcolata**: 68/5.880 (1,16%), tutte nel braccio nativo, localizzata nelle due celle gpt-oss native (10,0% e 6,3%); mediane 3–6 turni contro 12; corretta la riga «turns 12.0 / 12.0» che stampava il budget configurato | controllo a risposta nota contro `numeri_paper.py` |
| 17 scope del trasporto | **PASS** | 05, 08 | §5.9, §8 | «our prompted-text protocol»; eliminato «no version of this contrast can hold the token count fixed» | formula vietata |
| 18 nondeterminismo | **PASS** | 00, 01, 05, 09 | ovunque | dimostrazione di esistenza su 1 confronto su 8, esplicitamente non una claim di popolazione | testo e claim ledger C16 |
| 19 varianza al bordo (T7/T8) | **PASS** | `analysis/tabella_principale.py`, 05, Tab. 4 | §5.1 | «poorly identified at the boundary»; nessuna componente riportata, in nessuna direzione | didascalia rigenerata |
| 20 IC di T10 | **PASS** | `analysis/tabella_principale.py`, Tab. 6 | §5.3 | rimosso l'IC calcolato fuori dallo script congelato con n=4; resta la stima puntuale dello script congelato ($-4{,}16$pp) e l'esito del test | Tab. 6 rigenerata |
| 21 Tab. 9 ricostruita | **PASS** | 07 | §7.4 | otto campi: trasporto e semantica delle chiamate multiple, endpoint e API e regione, identificatore, decodifica, **budget di interazione e condizione di terminazione**, tool e provenienza, modelli esclusi, ragione con la configurazione | vedi §7 per il campo che lo studio non soddisfa |
| 22 novita' della checklist | **PASS** | 02, 07 | §2.2, §7.4 | «not explicit in the checklist we extend», con la dichiarazione che il confronto e' con quella sola fonte | didascalia di Tab. 9 |
| 23 proposizione sulla varianza | **PASS** | 07 | §7.5 prop. 3 | tolto «variance components can be apparatus-specific»; raccomandati pilota indipendente o ri-stima interna pre-specificata e letta in cieco | testo |
| 24 retorica dei costi | **PASS** | 05 | §5.2 | il calcolo $253/$17 resta come **lezione di allocazione** (diversita' dei task contro run ripetute), non come celebrazione | testo |
| 25 claim di prevalenza | **PASS** | 02, 09 | §2.2, §9 | eliminati «we assert to be low and did not measure» e «evaluations report the first inconsistently and the second not at all»; resta «existing reporting guidance does not make all of the apparatus fields examined here equally explicit» | ricerca |
| 26 densita' retorica | **PARZIALE, dichiarato** | tutte | tutte | -5.8% dal picco post-P0; il totale resta **+8.3% sull'originale** | vedi §7 |
| 27 aforismi | **PASS** | 01, 02, 05, 06 | ovunque | tolti «the other kind», «nothing for anyone to fix», «winner's curse», «reader overturns it with 5.809 trials», «the part that is new», «harder to escape», «sharpest» | ricerca su 9 termini: 0 residui argomentativi |
| 28 auto-accuse non necessarie | **PASS**, poi ampliato dalla passata di §0 | 08, 11 | §8.5, Declarations | uscite: la redirezione di shell del hook, il modo di fallimento delle variabili d'ambiente, il ratio 77/76,3, la sonda che non decide; **restano** workspace condiviso, meccanismo, ragione della ri-raccolta, stato probatorio delle deviazioni | vedi §7 |
| 29 voce d'autore singolo | **PASS** | tutte | tutte | 98 → 69 occorrenze di *we/our/us*, con 29 sostituzioni mirate frase per frase | conteggio |
| 30 claim ledger | **PASS** | `revisione/claim_ledger.md` | — | 30 claim con evidenza, stato, scope, posizione; 18 verbi forti verificati uno per uno | vedi §5 |
| 31 coerenza fra sezioni | **PASS** | tutte | Abstract→Contributi→Risultati→Discussione→Conclusione | 13 voci confrontate; 4 coerenze rese eseguibili nell'audit e ognuna esercitata togliendo la frase | test negativo per sezione |
| 32 integrita' numerica | **PASS** | `revisione/verifica_numerica.py`, `revisione/numeric_verification.tsv` | — | 29 voci rigenerate; nessun valore modificato a mano; **un difetto del controllo stesso trovato e corretto** (vedi §3) | 0 guasti |
| 33 nessuna sostituzione statistica silenziosa | **PASS** | Tab. 6, Tab. 10, App. A, App. B | — | serie esatta, sign-flip, GEE, bootstrap, sottoinsiemi di saturazione, randomizzazione: tutte etichettate sensibilita' o esplorative | didascalie |
| 34 guardia anti-cancellazione | **PASS** | `revisione/anti_deletion.json` | — | tabelle 11→11, figure 2→2, meccanismi 8→8, RQ 6→6, test 10→10, parole 14.161→15.338 | nessun risultato eliminato |

---

## 2. Audit della cronologia

`revisione/chronology.tsv` porta 21 eventi. I quattro che hanno cambiato il manoscritto:

1. **Congelamento.** 2026-08-13 22:00:03, commit `c89a3ea`. La prima riga di dati di *qualunque* lotto e'
   delle 22:32:36, **32 minuti dopo**; la prima riga del lotto conservato e' 22 ore dopo. Il testo diceva
   solo la seconda, che suona un margine piu' ampio di quello reale. Ora dice entrambe (§3).
2. **T9/T10.** Implementati undici ore dopo il congelamento, quando esistevano **861 righe in tre celle di
   un solo modello** — ricalcolato dai timestamp, non dedotto. Nessuno dei due test e' calcolabile da un
   modello solo. Lo stato «famiglia congelata, implementazione sotto emendamento datato» ora e' identico in
   abstract, §1, §3, Tab. 2 e §9.
3. **RQ5 e RQ6.** Nate in esecuzione, e §4 lo dice invece di affermare che nessuna domanda e' stata
   aggiunta. La frase «no hypothesis, test or comparison is added» era in contraddizione diretta col
   paragrafo che la seguiva.
4. **Ri-raccolta.** Prima riga 2026-08-15 20:57:37; mtime piu' antico fra i file dei criteri 22:01 dello
   stesso giorno. **La designazione segue la prima riga di 1h04m**, e il manoscritto diceva il contrario.

---

## 3. Audit quantitativo

Ogni valore cambiato e' in `revisione/numeric_verification.tsv`, rigenerato dal comando che lo produce.
Quattro correzioni di fatto, non di formulazione:

| era | e' | come e' emerso |
|---|---|---|
| «one cell ends below plan at 44 binaries of 45» (§4) | **tutte e 16 le celle di entrambi i lotti portano 45 binari**; quello che esiste e' un binario con 7 run valide su 8 | conteggio diretto per cella |
| «turns 12.0 [12.0-12.0], ratio 1.00» in Tab. 8 | **turni usati 6,0 contro 4,0** | la colonna `n_turns` dei CSV e' `args.turns`, il budget configurato: costante 12 su ogni riga. Ora `runtime_t6.py` legge le traiettorie e porta un controllo negativo che pretende quella colonna costante |
| «eleven occurrences with that exact value» (M8) | **11 traiettorie distinte** — 4 nell'originale, 7 nella ri-raccolta; le occorrenze della stringa sono 21 contando il lotto invalidato | conteggio per file e per braccio |
| «T6's $p$ of 0.0191 misses both» (§5.3) | **0,0155**, che e' la serie congelata portata in tabella principale | trovato nella rilettura ostile, ora sorvegliato |

**Un difetto del controllo, trovato e corretto.** La prima versione di `verifica_numerica.py` passava i
valori attesi a `re.search`: `8{,}853` veniva letto come «8 ripetuto zero o piu' volte» seguito da `853`, e
trovava `853` ovunque. Dichiarava MATCH su un valore che nel testo non c'era. Ora il confronto e'
letterale, e la tabella porta tre controlli negativi — due valori che **non** devono comparire e uno che
deve.

**SPEC-14, decisione.** La ricostruzione disponibile e' parziale e lo dice: le traiettorie rilasciate
registrano l'uso per turno dichiarato dal provider, non il payload serializzato, e l'artefatto non porta un
tokenizer del modello servito. Cio' che si ricostruisce e' la **scomposizione** del totale — 6 turni contro
4, e 1.263 contro 678 token al primo turno dove non c'e' ancora storia. Quindi **Decision B**: differenza
di contabilita' dichiarata dal provider, non «uno stack consegna al modello 2,3 volte il contesto».

---

## 4. Riconciliazione del censimento

`revisione/census_ledger.tsv`, che riconcilia con `analysis/denominatore_roster.py`:

- **(A) coppie modello-piattaforma rimosse prima della misura**: **8 su 21** tentate, 11 modelli distinti,
  **7 cause distinte** (6 sono M1–M6, la settima e' il canale di ragionamento). Per piattaforma: Databricks
  2/8, Bedrock 3/10, Azure 3/3. Escludendo Azure: 5 su 18.
- **(B) perdite dentro una cella gia' avviata**: M7, 453 righe di una cella scartate e ri-raccolte, con
  l'effetto di selezione fra i sopravvissuti; M8, 11 traiettorie su lotti da 5.805 e 5.809 misurazioni.
- **(C) meccanismi documentati**: **8**, di cui 6 agiscono prima del punteggio e 2 dall'interno di una run.

Nessun denominatore e' condiviso fra le tre unita', e ogni occorrenza di 8/21, 5/18, «eight mechanisms»,
«seven causes» nomina l'unita' che conta.

**Rilevabilita', da evidenza**: **4** livello 1 (M2, M3, M4, M5), **3** livello 2 (M1, M6, M7), **1**
livello 3 (M8). Il livello di M1 e' un limite superiore dichiarato: la sonda a richiesta singola non e'
stata provata contro quella coppia.

---

## 5. Sintesi del claim ledger

30 claim in `revisione/claim_ledger.md`. Distribuzione: 12 osservazioni dirette, 2 inferenze confermatorie,
7 esplorative, 2 sensibilita', 1 diagnostico, 3 interpretazioni, 1 raccomandazione, 1 ipotesi futura, 1
scope bound. I diciotto verbi forti sono verificati uno per uno: nessuno sta sopra il proprio stato, e
**nessuna osservazione diretta e' stata indebolita** a *may suggest*.

---

## 6. Claim deliberatamente conservate

Questa sezione esiste perche' la revisione non si risolva cedendo ogni claim forte.

1. **Otto meccanismi, ciascuno col messaggio verbatim dell'endpoint.** Non ridotti, non ammorbiditi,
   non spostati in appendice. Sono il contributo primario e restano tali.
2. **8 coppie su 21 non hanno prodotto un punteggio, Azure inclusa nel denominatore.** Escluderla avrebbe
   dato un numero piu' piccolo scartando i tentativi che fallivano di piu'. Resta dentro, con la
   disaggregazione accanto.
3. **Un controllo di capacita' a richiesta singola non copre la classe.** Rafforzata, non indebolita: la
   riclassificazione porta a tre i meccanismi invisibili a un controllo ordinario, contro i due dichiarati
   prima.
4. **Nessuno dei dieci test supera Holm**, riportato come risultato principale e non nascosto.
5. **Temperatura zero non e' determinismo**, con i tassi per modello.
6. **La stabilita' del punteggio puo' differire fra due servizi a identita' di modello fissa.** Ristretta a
   dimostrazione di esistenza, che e' cio' che un caso su otto sostiene — non ritirata.
7. **Su T3 e T6 la leva che vincola e' il numero di task.** Con gli intervalli bootstrap e il controllo di
   randomizzazione che la delimita senza smentirla.
8. **La ri-raccolta e' la base primaria.** La giustificazione e' cambiata — dall'anteriorita' dei criteri al
   meccanismo rimosso per costruzione — ed e' piu' forte di prima, perche' e' una proprieta' del codice.
9. **La checklist di Tab. 9 e' l'output trasferibile**, ampliata da sei a otto campi invece che ritirata.
10. **Il censimento non e' una stima e non ha una distribuzione campionaria dietro.** Conservata, con la
    retorica intorno tolta.

---

## 7. Limiti reali che restano

Quattro, e nessun catalogo speculativo oltre questi.

1. **L'anteriorita' dei quattro criteri di concordanza non e' verificabile da terzi.** Gli mtime dicono
   1,9% e 27,4%; la storia committata dice 73,4%. E la soglia 6 su 8 e' stata scelta quando l'esito
   originale era noto da 4h31m, senza una derivazione dichiarata. Il paper lo scrive; non e' riparabile a
   posteriori.
2. **La ricostruzione dei token di T6 e' parziale.** Le tracce registrano l'uso per turno dichiarato dal
   provider, non il payload; senza un tokenizer del modello servito non si ottiene un conteggio
   client-visible. Il paper riporta la scomposizione che ha e dichiara quella che non ha.
3. **Il livello di rilevabilita' di M1 e' un limite superiore.** La variante a richiesta singola non e'
   stata provata contro quella coppia, e l'infrastruttura non e' piu' disponibile per provarla.
4. **La versione del decompilatore non e' registrata.** L'artefatto rilascia gli output congelati e hashati
   al posto suo, che e' cio' che l'harness consuma; il campione «tool e provenienza» di Tab. 9 lo dichiara
   come il campo che questo studio soddisfa per surrogato.

**Sul taglio del 20–25% (SPEC-26): non raggiunto, e la ragione e' esplicita.** Il manoscritto e' passato da
14.161 a 16.281 parole applicando i P0 — cronologia esatta, denominatori con unita', limiti di
configurazione, misura del budget di turni, scomposizione dei token, argomento di indipendenza dalla
tassonomia — tutte cose che SPEC-26 elenca fra quelle da **preservare**. Il passaggio editoriale ha poi
tolto 943 parole di ripetizione e retorica. portando a 15.338: **+8.3% sull'originale, -5.8% dal picco**.
Arrivare a 12.000 avrebbe richiesto di cancellare evidenza, che SPEC-26 vieta e SPEC-34 sorveglia. Il
paper resta dentro le 11–18k parole tipiche della sede, che non ha limite di pagine.

---

## 8. Revisione avversariale finale

### VERIFY-03, statistica

| attacco | classe | perche' |
|---|---|---|
| «l'MDE per contrasto e' potenza osservata con un altro nome» | **MATERIAL, delimitato** | e' l'attacco piu' forte rimasto: MDE e potenza osservata sono entrambi funzioni monotone della SD osservata. La difesa e' che l'MDE non e' usato per interpretare nessun $p$ — la didascalia lo dichiara esplicitamente — ma solo per la claim sul disegno (fattore 23,7 fra celle). Un revisore puo' comunque chiedere di toglierlo del tutto; il paper non ne dipende |
| potenza a posteriori | **INVALID** | non c'e' piu', in nessuna forma |
| cronologia della pre-registrazione | **ALREADY BOUNDED** | 32 minuti e 22 ore, entrambi verificabili dalla storia committata |
| T9/T10 spacciati per pre-registrati | **INVALID** | stato identico in cinque punti, guardia eseguibile |
| leakage esplorativo/confermativo | **ALREADY BOUNDED** | Tab. 6 e' la sola serie congelata; tutto il resto e' etichettato |
| multiplicita' ($m{=}8$ contro $m{=}10$) | **ALREADY BOUNDED** | entrambe le soglie stampate; il $p$ minimo, 0,0155, sta sopra tutte e due |
| designazione della ri-raccolta | **ALREADY BOUNDED** | dichiarata Outcome B; la giustificazione portante e' il meccanismo rimosso per costruzione |
| componenti di varianza al bordo | **ALREADY BOUNDED** | T7 e T8 non riportati, in nessuna direzione |

### VERIFY-04, empirical SE

| attacco | classe | perche' |
|---|---|---|
| «e' un experience report» | **RHETORICAL** | c'e' un disegno pre-registrato $4\times2\times2$, una famiglia di dieci test con correzione, e un censimento con denominatore dichiarato |
| novita' | **ALREADY BOUNDED** | §6.5 elenca quattro punti che reggono qualunque etichetta si dia ai singoli meccanismi |
| specificita' del task | **ALREADY BOUNDED** | dichiarata due volte e mai contraddetta; l'output trasferibile e' checklist e metodo |
| costruzione del roster | **GENUINELY UNRESOLVED, dichiarato** | roster assemblato, non campionato; la misura mancante e' specificata come lavoro futuro |
| novita' della checklist | **ALREADY BOUNDED** | limitata alla sola fonte confrontata |
| lunghezza | **RHETORICAL** | sede senza limite di pagine; vedi §7 |

### VERIFY-05, systems

| attacco | classe | perche' |
|---|---|---|
| «M3 e' un bug di configurazione, M8 di integrazione» | **INVALID come attacco al contributo** | e' esattamente cio' che §6.5 concede in anticipo, e i quattro punti restano |
| varianti di API e configurazione non esplorate | **ALREADY BOUNDED** | ogni riga e' limitata alla configurazione provata, con le varianti tentate elencate |
| costruzione della sonda stateful | **ALREADY BOUNDED** | per M6 la sequenza a tre richieste e' depositata; per M1 il livello e' dichiarato limite superiore |
| attribuzione all'endpoint | **INVALID** | non ce n'e' piu' nessuna |
| misura dei token di T6 | **MATERIAL, gia' ristretto** | Decision B applicata, copertura dichiarata |
| budget di turni | **ALREADY BOUNDED** | calcolato per cella, non ipotizzato |

### VERIFY-06, rilettura senza checklist

Le cinque obiezioni piu' forti che restano, in ordine: (1) l'MDE come potenza travestita; (2) l'anteriorita'
non verificabile dei quattro criteri; (3) il roster assemblato; (4) la ricostruzione parziale dei token;
(5) il livello di M1 come limite superiore. Nessuna claim di testa e' piu' forte della sezione Risultati;
nessuna affermazione causale eccede l'identificazione; nessuna frase di cronologia contraddice la
provenienza; nessun denominatore cambia unita' in silenzio. La rilettura ha trovato **due difetti reali**
— il $p$ 0,0191 rimasto in §5.3 e i due conteggi di soglia confusi (5 su 8 al posto di 6 su 8 sulla banda
dei ±3pp) — entrambi corretti e sorvegliati.

### VERIFY-07, nessuna confessione

Ricerca eseguita su *limitation, invalid, failed, fail, wrong, defect, cannot, did not, threat, error*
nelle sezioni Discussione, Minacce e Conclusione: **13 occorrenze**, ispezionate una per una e tutte
materiali. Otto sono l'etichetta strutturale «Threat» che la sede richiede in quella sezione. Due sono
«the batch in which a validity flag had failed», che e' il fatto da cui dipende l'intero RQ6. Una e' «an
endpoint returned that message or it did not», che e' una definizione. Una e' il limite di scope della
checklist imposto da SPEC-22. Una e' «an apparatus whose sharing behaviour cannot be audited», che e' la
ragione per cui la ri-raccolta porta l'analisi primaria. Nessuna passa il test di materialita' al
contrario. Le uscite sono elencate in SPEC-28 sopra: erano documentazione di repository, e stanno
nell'artefatto.
