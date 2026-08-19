# Redazione del deposito

Questo deposito e' un **oggetto diverso** dal repository di lavoro: esportato senza `.git`,
senza le cartelle di memoria dell'assistente, e con i nomi che identificano autore e
organizzazione sostituiti da segnaposto.

**La sede e' a cieco singolo, quindi la redazione NON serve all'anonimato** — questo documento
diceva «la venue e' a doppio anonimato», che era vero della destinazione precedente e falso di
questa, e un'affermazione falsa dentro l'artefatto e' peggio che dentro il paper: nell'artefatto
nessun revisore la corregge. Cio' che la redazione protegge e' l'**infrastruttura aziendale** —
nomi di workspace, profili cloud, percorsi assoluti — che non appartiene a un pacchetto di
riproduzione in nessun regime di anonimato. L'autore del manoscritto e' dichiarato.

La redazione e' **meccanica e dichiarata**, non selettiva: ogni occorrenza di ciascuna
stringa qui sotto e' stata sostituita ovunque comparisse, senza eccezioni per file.

## Le sostituzioni

| cercato | sostituito | perche' |
|---|---|---|
| _(withheld: nome del workspace, identifica l'organizzazione)_ | `<profilo-databricks>` | nome del workspace, identifica l'organizzazione |
| _(withheld: nome del profilo AWS, identifica l'organizzazione)_ | `<profilo-bedrock>` | nome del profilo AWS, identifica l'organizzazione |
| `/Users/detomasi` | `<home>` | percorso assoluto, identifica l'autore |
| _(withheld: indirizzo dell'autore)_ | `<email>` | indirizzo dell'autore |
| `lodetomasi` | `<utente>` | username della forge |
| `Lorenzo de Tomasi` | `<autore>` | nome dell'autore |
| `Lorenzo De Tomasi` | `<autore>` | nome dell'autore |
| _(withheld: identificatore numerico della forge)_ | `<id-utente>` | identificatore numerico della forge |
| _(withheld: nomina la venue e il capitolo gemello)_ | `<capitolo-precedente>` | nomina la venue e il capitolo gemello |
| _(withheld: nome dell'organizzazione, in chiaro nei commenti dell'harness)_ | `<organizzazione>` | nome dell'organizzazione, in chiaro nei commenti dell'harness |
| _(withheld: la stessa in minuscolo)_ | `<organizzazione>` | la stessa in minuscolo |
| _(withheld: sede di sottomissione di C1)_ | `<sede-anonima>` | sede di sottomissione di C1 |
| _(withheld: sede di sottomissione di C1)_ | `<sede-anonima>` | sede di sottomissione di C1 |
| _(withheld: cartella di memoria dell'assistente)_ | `<cartelle-agent>/` | cartella di memoria dell'assistente |
| _(withheld: file di istruzioni del repository)_ | `<istruzioni-di-progetto>` | file di istruzioni del repository |
| _(withheld: nome del tooling)_ | `<assistente>` | nome del tooling |
| _(withheld: nome di un agent di revisione)_ | `<revisione-avversariale-dell-apparato>` | nome di un agent di revisione |
| _(withheld: nome di un agent di revisione)_ | `<gauntlet-di-revisione>` | nome di un agent di revisione |
| _(withheld: nome di un agent di revisione)_ | `<controllo-del-registro>` | nome di un agent di revisione |
| _(withheld: lo stesso, in forma breve)_ | `<revisione-avversariale-dell-apparato>` | lo stesso, in forma breve |
| _(withheld: percorso del tooling di ricerca)_ | `<tooling>` | percorso del tooling di ricerca |
| _(withheld: nome di un repository del tooling)_ | `<altro-repository>` | nome di un repository del tooling |
| _(withheld: nome di variabile d'ambiente che nomina il tooling)_ | `C2_PRICING` | nome di variabile d'ambiente che nomina il tooling |
| _(withheld: titolo di C1, ricavato da references.bib)_ | `<titolo-capitolo-precedente>` | titolo di C1, ricavato da references.bib |
| _(withheld: le prime cinque parole dello stesso titolo)_ | `<titolo-capitolo-precedente>` | le prime cinque parole dello stesso titolo |

## Gli hash, e perche' ce ne sono due serie

Redigere un file congelato ne cambia l'hash. `HASH-CONGELATI.md` in **questo deposito**
dichiara gli hash **del deposito**, cosi' che `./verifica_hash.sh` giri pulito qui dentro.
Gli hash del repository di lavoro — quelli che il paper cita come prova che l'analisi era
congelata prima dei dati — sono nella colonna di sinistra.

Un revisore che ricalcola trova percio' due catene coerenti, e sa quale sta guardando.

| file | hash nel repository di lavoro | hash in questo deposito | redatto |
|---|---|---|---|
| `PREREGISTRAZIONE.md` | `9d6145d8f09c534a4314173e81a7b96ff27750b29b6a7c4229467477319d8317` | `2e25c38040e16f5e9352faae96e9ebd2aee65272fca927d3bb13bbc71d1fd6bd` | si |
| `analysis/analyze_c2.py` | `c478df38aa1adb748c11d45b3e22648f92e6a28503f3552d1aca1811c0babed2` | `c478df38aa1adb748c11d45b3e22648f92e6a28503f3552d1aca1811c0babed2` | no |
| `analysis/potenza.py` | `52d6d2bc7e2d39dfcc5700623960a65747a881ce5f59f950a20c6f50fdd918b7` | `fc5802f73edf1a53a854b8eda8a3f182091c181118c83f20bdc10088d322cb32` | si |
| `configs/binari_holdout.txt` | `099f811fd0b56158f39adeccf89a7fc2329c4dc12ecf9b91dcfd7dff8cf98735` | `099f811fd0b56158f39adeccf89a7fc2329c4dc12ecf9b91dcfd7dff8cf98735` | no |
| `src/raccogli_c2.py` | `a91a2a9edf1dbbcf93645e5c0d1c1b8915c3e626f274e27746802e90e810e33c` | `0da84fd40762517b7d12c240c7d7748f8ac509ddd701d757405884f32f7fc059` | si |
| `analysis/confronto_riraccolta.py` | `76cd6c126400210b7ab101f98f39b6b958087be8eabf515f5e2991acf36e4719` | `76cd6c126400210b7ab101f98f39b6b958087be8eabf515f5e2991acf36e4719` | no |

3 dei 6 file congelati sono stati redatti. Gli altri sono byte-identici.

## Cosa non c'e' in questo deposito, e non e' una dimenticanza

- **`.git`** — la storia porta nome, indirizzo e identificatori dell'autore su ogni commit.
  Non e' stata riscritta: riscrivere una storia registrata e' cio' che IR-5 vieta. E'
  semplicemente fuori dal deposito.
- **`results/workv3/`** — directory di lavoro della compilazione, sovrascritta per
  costruzione. Non e' una traccia di audit di niente, e includerla suggerirebbe che lo sia.
- **le cartelle di memoria dell'assistente** — contenevano percorsi assoluti e il
  nome della venue.

## Cosa c'e', e va letto sapendo cos'e'

- **`results/invalidati/`** — le misurazioni scartate, con il documento che dice perche'.
  Restano perche' `results/` e' append-only: chiunque puo' rifare i conti su cio' che e'
  stato escluso.
- **`results/esplorativo/`** — contiene i JSON del replay e **nessuna misurazione**. Il
  braccio esplorativo Azure e' stato invalidato insieme al lotto del nome dell'algoritmo e
  non e' stato riraccolto. Sta scritto in `results/VALIDITA-BRACCIO-AZURE-2026-08-15.md`.
  Non entrava nella famiglia dei test per costruzione, quindi non muove nessuna soglia.

## Script che la redazione rende non rieseguibili sul posto

In questi file la sostituzione ha riscritto un **percorso dentro il codice**, non
solo una stringa in un commento. Girano sulla macchina che ha i dati del capitolo
precedente, non dentro il deposito, e falliscono in modo rumoroso invece che dare un
numero sbagliato — il verso giusto, ma va detto prima che qualcuno li lanci.

- `analysis/esposizione_list_strings_c1.py`
- `analysis/potenza.py`

Tutti gli altri script del deposito riproducono i propri output dai CSV depositati.
