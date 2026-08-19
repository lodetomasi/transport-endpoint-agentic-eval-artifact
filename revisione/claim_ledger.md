# Claim ledger — C2, revisione EMSE

Stati ammessi: *direct observation*, *confirmatory inference*, *exploratory inference*, *sensitivity
result*, *interpretation*, *recommendation*, *future hypothesis*.

| ID | claim | evidenza | stato | scope | dove nel manoscritto |
|---|---|---|---|---|---|
| C01 | Otto meccanismi con cui un endpoint rimuove un modello prima del punteggio o ne distrugge le misure dall'interno | messaggio verbatim dell'endpoint per ciascuno; `research/CENSIMENTO.md`, `results/censimento-sonde/`, traiettorie rilasciate | direct observation | il roster assemblato per questo studio, sotto le configurazioni di `mechanism_config.tsv` | abstract; §1 contributo 1; §6, Tab. 5; §9 |
| C02 | 8 delle 21 coppie modello-piattaforma tentate non hanno prodotto un punteggio; 5 su 18 sulle due piattaforme misurate | `analysis/denominatore_roster.py`, enumerazione esplicita | direct observation | denominatore dichiarato, non campionato | abstract; §6 apertura |
| C03 | Le 8 rimozioni tracciano a 7 cause distinte, di cui 6 fra i meccanismi nominati | stesso script | direct observation | idem | §6 apertura; `census_ledger.tsv` |
| C04 | I meccanismi stanno a tre livelli di rilevabilita': 4 / 3 / 1 | `probe_matrix.tsv`, con la sonda minima per ciascuno | direct observation, **tranne M1 il cui livello e' un limite superiore** | le configurazioni provate | abstract; §1; §6, Tab. 5; §9 |
| C05 | Un controllo di capacita' a richiesta singola non copre la classe | segue da C04 | interpretation | evaluations agentiche multi-turno con tool | abstract; §6; §9 |
| C06 | Nessuno dei dieci test pre-registrati supera la propria soglia di Holm | `analysis/analyze_c2.py` sulla ri-raccolta; Tab. 6 riporta la serie congelata con le soglie | **confirmatory inference** | 4 modelli, 2 cloud, 2 trasporti, 45 binari | abstract; §5.3, Tab. 6; §9 |
| C07 | La serie esatta di Student e la sign-flip danno lo stesso esito di famiglia | `p_esatti_student.py`, `permutazione.py` | **sensitivity result** | idem | §5.3; App. A, Tab. 10 |
| C08 | Un modello a run-level (GEE cluster-robust) riproduce la lettura del test congelato | `glmm_esplorativo.py` | **sensitivity result** | i tre contrasti che copre | §8; App. B |
| C09 | Le SD osservate dei contrasti appaiati coprono un fattore 23,7 | `scomposizione_varianza.py` | direct observation | gli otto contrasti | abstract; §5.4; §7.2 |
| C10 | L'effetto risolvibile per contrasto va da 0,49pp a 11,59pp, e cinque su otto superano i 4,87pp assunti | `potenza_per_contrasto.py` | **diagnostic**, condizionale alla dispersione osservata | idem | §5.3; §5.4; Tab. 6 |
| C11 | Su T3 e T6 la leva che vincola e' il numero di task, non le run: 0,5%/668 e 9,1%/380 | `scomposizione_varianza.py` + bootstrap sui binari | exploratory inference | i due contrasti ad alta varianza | §5.1; §5.2; §7.1; §9 |
| C12 | La saturazione della metrica non produce da sola cio' che la decomposizione attribuisce all'eterogeneita' | `granularita_diretta.py` con due regole di esclusione e randomizzazione a 20.000 giri | exploratory inference, **delimitata**: in 2 casi su 4 un sottoinsieme casuale da' una quota uguale o maggiore ~1 volta su 5 | questo corpus | §5.1.1 |
| C13 | La calibrazione ereditata non era verificabile prima di raccogliere | provenienza del lotto invalidato, `results/README-validita.md` | direct observation | la calibrazione specifica ereditata | §5.2; §7.1; §9 |
| C14 | Se una calibrazione di varianza si trasferisca fra apparati resta aperto | due raccolte di UN apparato non lo decidono | **future hypothesis**, dichiarata tale | — | §1 contributo 4; §5.2; §7.1; §7.5 prop. 7; §9 |
| C15 | Temperatura zero non e' determinismo | `validita.py`: 91–100% contro 20–24% di binari con otto run identiche | direct observation | 4 modelli, 16 celle | abstract; §5.8; §9 |
| C16 | La stabilita' del punteggio puo' differire fra due servizi a identita' di modello fissa | 1 confronto su 8 con bande di Wilson disgiunte anche dopo Bonferroni | **exploratory inference, existence demonstration** — esplicitamente NON una claim di popolazione | quel modello, quell'asse | abstract; §5.8; §9 |
| C17 | T6 e' una differenza fra due servizi come distribuiti, la cui sorgente non e' identificata | Tab. 6 + §5.7: turni usati 6 vs 4, latenza, token dichiarati dal provider | confirmatory (il contrasto) + direct observation (le quantita') + **nessuna attribuzione causale** | la cella llama/native | §5.7; Tab. 6 nota; §9 |
| C18 | Il divario dei token in ingresso e' una differenza di CONTABILITA' dichiarata dal provider, scomponibile in lunghezza della traiettoria e conteggio al primo turno | `runtime_t6.py`, `contesto_t6.py` | direct observation, con copertura di ricostruzione dichiarata parziale | le due celle di T6 | §5.7 |
| C19 | 68 traiettorie su 5.880 (1,16%) esauriscono il budget di turni, tutte nel braccio nativo; la saturazione e' localizzata nelle due celle gpt-oss native | `saturazione_turni.py`, per cella | direct observation | la ri-raccolta | §5.7.1; Tab. 8 |
| C20 | Ogni effetto riportato e' condizionale al budget fisso di 12 turni | segue da C19 | interpretation | — | §5.7.1; Tab. 9 |
| C21 | Le due implementazioni valutate non isolano il formato di serializzazione dal volume di contesto | §8, misura per cella | direct observation | le due implementazioni valutate | §8 |
| C22 | Le affermazioni empiriche sul trasporto testuale valgono per **il protocollo prompted-text valutato**, una chiamata per turno | costruzione dell'harness | scope bound | — | §5.9; §8 |
| C23 | La ri-raccolta e' la base primaria perche' il meccanismo della workdir condivisa e' rimosso per costruzione | 30 percorsi condivisi nell'originale, 0 su 451 misure concorrenti | direct observation | — | §5 apertura; §8; §9 |
| C24 | I quattro criteri di concordanza sono **diagnostici pre-specificati**, non una regola pre-registrata e non indipendenti dall'esito originale | `recollection_provenance.tsv`, `chronology.tsv` | **provenance statement**, con i tre fatti che la fissano | — | §8; Tab. 7 didascalia; §9 |
| C25 | La pre-registrazione e' stata congelata 32 minuti prima della prima riga di qualunque lotto e 22 ore prima della prima riga del lotto conservato | storia committata | direct observation, verificabile da terzi | — | §3; §8 |
| C26 | T9 e T10 sono stati implementati sotto emendamento datato dopo l'inizio della raccolta, quando esistevano 861 righe di un solo modello | `SUCCESSIONE-03` + timestamp delle righe | provenance statement | — | abstract; §1; §3; §4 Tab. 2; §9 |
| C27 | La checklist di Tab. 9 e' l'output trasferibile insieme al metodo di decomposizione | — | **recommendation** | — | abstract; §1; §7.4 |
| C28 | Gli ultimi due campi della checklist non sono espliciti nelle linee guida che il paper estende | confronto con quella sola fonte, dichiarato | interpretation, **limitato a una fonte** | — | §7.4 didascalia |
| C29 | Una valutazione che non dichiara il proprio trasporto non e' riproducibile dalla sola sezione di metodo | segue da C01, C06, C17, C21 | interpretation | — | §1; §9 |
| C30 | La rimozione di un modello lascia intatto l'ordine fra due cloud e cambia la distanza riportata | ricalcolo togliendo un modello alla volta su 4 modelli | exploratory inference, **segno e ordine di grandezza, non un coefficiente** | 4 modelli | §6.4 |

## Verbi forti, verificati uno per uno

Diciotto occorrenze di *establishes / demonstrates / shows / settles / causes* nel corpo. Nessuna sta
sopra il proprio stato: le tre di §6 e §9 sono su osservazioni dirette, quella di §5.8 e' un *can*
esistenziale, quelle di §5.2 e §7.1 sono negazioni (*cannot establish*), e le restanti nominano cio' che
una tabella mostra. Nessuna osservazione diretta e' stata indebolita a *may suggest*: l'obiettivo e' la
forza calibrata, non la prosa timida.
