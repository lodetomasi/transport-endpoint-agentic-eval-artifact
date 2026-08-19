# Censimento dell'infrastruttura — C2

Misurato il 2026-08-13, prima che il piano esistesse. Tutto ciò che segue è stato ottenuto
interrogando gli endpoint, non leggendo documentazione.

## La claim, dal registro del programma

> La capacità agentica misurata è funzione del trasporto — function calling nativo, tool
> testuali, schemi, formato delle osservazioni, gestione degli errori, retry — e nessuna
> valutazione **agentica multi-turno su compito downstream** incrocia il trasporto con
> l'identità del cloud gestito **a parità di pesi**, né tratta la cancellazione di un modello
> come effetto di selezione di prima classe.

> **La formulazione precedente diceva «nessuna valutazione pubblicata dichiara quale usa», ed
> era falsa.** La Berkeley Function-Calling Leaderboard pubblica per ogni modello le due
> varianti — verbatim: *«FC = native support for function/tool calling. Prompt = walk-around for
> function calling»* — e GPT-4-1106-Preview fa **85,65** in Prompt contro **79,65** in FC, cioè
> il testo vince di 6,00pp, nella direzione opposta al nostro seme. Ristretta il 2026-08-15 in
> [`EMENDAMENTO-04`](../registro/EMENDAMENTO-04-claim-dopo-bfcl.md), che porta la catena delle
> fonti e le due precisazioni che la verifica ha prodotto.

**Falso se**: su ogni modello di ogni endpoint la differenza fra due trasporti sta entro ±3pp
con intervallo che contiene lo zero, **e** nessun modello viene escluso da un rifiuto di
protocollo.

## Il vicino più prossimo sulla cancellazione, e in cosa differisce

**The Leaderboard Illusion** (arXiv:2504.20879, Singh et al., 29 apr. 2025) tratta già la
rimozione differenziale di un modello come **effetto di selezione di prima classe**, non come
rumore: *«proprietary closed models are sampled at higher rates and have fewer models removed
from the arena than open-weight and open-source alternatives»*, con Google e OpenAI al 19,2% e
20,4% dei dati dell'arena contro il 29,7% di **83** modelli open-weight messi insieme.

**La differenza va scritta con precisione, perché il vicino è più vicino di quanto sembri.**
Quel paper **nomina già** il rifiuto tecnico fra le cause di rimozione — *«Chatbot Arena may be
forced to deprecate a model when a provider no longer supports it via its API»* — quindi non è
vero che opera «a un livello causale diverso» e basta. La formulazione onesta è un'altra: la sua
**evidenza quantitativa** è sull'asimmetria **curatoriale aggregata** (205 modelli deprecati in
silenzio contro 47 dichiarati; 87,8% degli open contro 80% dei proprietari), non sul meccanismo
tecnico caso per caso. Qui è l'inverso: sei meccanismi, ciascuno col messaggio verbatim
dell'endpoint, e nessun tasso.

## E il vicino che dichiara di non esserci riuscito

**FailureAtlas** (arXiv:2607.17525, Pandey e Singh, 20 luglio 2026) propone una tassonomia dei
modi in cui un'infrastruttura di serving multi-provider fallisce, su due assi — livello di
origine e rilevabilità. Il suo catalogo verificato ha **cinque voci**, nessun vendor nominato.

E una delle righe della tassonomia è vuota, **dichiaratamente**:

> *«The Model Behavior row (L4) is intentionally empty reflecting the difficulty of documenting
> this failure class to evidence grade.»*
>
> *«Despite widespread anecdotal reports of "model degradation" or "instruction-following
> drift," we were unable to find a single evidence-grade, reproducible bug report that met our
> inclusion criteria for an infrastructure-level failure in model behaviour.»*

Hanno cercato e **non hanno trovato un solo caso** che soddisfacesse i loro criteri di evidenza.
Questo censimento ne porta sei, ciascuno con il messaggio verbatim dell'endpoint che lo produce.
È il posizionamento più preciso disponibile per questa parte del lavoro, e va scritto così —
«riempie una casella che un lavoro precedente dichiara di non essere riuscito a riempire» — non
come «nessuno ha catalogato».

## Il vicino sul determinismo, che è metodologico

**Atil et al.**, *Non-Determinism of "Deterministic" LLM Settings* (arXiv:2408.04667, tredici
autori, ago. 2024 con ultima versione apr. 2025). Metodologia quasi identica alla misura di
determinismo di questo capitolo: **5 modelli, 8 task, 10 run** a temperatura nominale zero, con
*«accuracy variations up to 15% across naturally occurring runs»* e *«a gap of best possible
performance to worst possible performance up to 70%»*.

La differenza che resta: sono **modelli diversi, ciascuno su un solo percorso di hosting**. Lo
stesso modello su due cloud nominati, con tassi di determinismo diversi fra i due, non c'è —
ed è la misura che questo capitolo aggiunge.

Tutte le fonti di questa sezione sono state **fetchate il 2026-08-15**, e nessuna è citata a
memoria.

## Perché due infrastrutture e non una

Con un endpoint solo, modello e infrastruttura sono perfettamente confusi: il −10,7pp che in
S1 separa i due trasporti per Haiku è, su un provider solo, tanto una proprietà di Haiku
quanto una proprietà dello shim OpenAI-compatibile di quel provider. Lo stesso modello su due
cloud separa le due letture in modo binario — se la differenza resta è del modello, se sparisce
è dell'infrastruttura.

## Le celle di sovrapposizione

Databricks (`<profilo-databricks>`, Azure) e Bedrock (`<profilo-bedrock>`, us-east-1, account <account>).

| modello | Databricks | Bedrock | tool nativo | nei bracci pieni |
|---|---|---|---|---|
| gpt-oss-120b | ✓ | ✓ | 1 call | **sì** |
| llama-3.3-70b | ✓ | ✓ | 1 call | **sì** |
| claude-haiku-4-5 | ✓ | ✓ | 1 call | **sì** |
| claude-sonnet-4-5 | ✓ | ✓ | 1 call | **sì** |
| claude-opus-4-5 | ✓ | ✓ | 1 call | solo censimento — $56,48 da solo |
| llama-3.1-8b | ✓ | ✓ | **prosa** | solo censimento |
| gpt-oss-20b | ✓ | ✓ | 1 call | solo censimento |

Quattro modelli nei bracci pieni, tre famiglie, pesi proprietari e aperti. I pesi aperti sono
la cella pulita: ciascun cloud li ospita davvero, quindi un risultato nullo significa che le
infrastrutture concordano e non che sono la stessa cosa con due nomi.

`llama-3.1-8b` risponde in prosa dove tutti gli altri emettono la tool call, sullo stesso
endpoint e senza cambiare nulla: è già una cella di trasporto.

## Sei meccanismi che tolgono un modello da una valutazione

> **Cinque a piano congelato, sei oggi.** `PREREGISTRAZIONE.md` §9 dice «cinque», ed è
> corretto: è congelata il 2026-08-13 e registra ciò che si sapeva allora. Una
> pre-registrazione non si aggiorna per combaciare con scoperte successive — sarebbe
> esattamente la libertà che esiste per togliere. Il sesto è del 2026-08-14 ed è
> registrato qui, con la data. Il §9 dichiarava già che l'elenco non è esaustivo, e la
> classe è aperta per costruzione.

Nessuno cercato: sono emersi provando a costruire il campione.

| meccanismo | caso | evidenza |
|---|---|---|
| rifiuto di protocollo | Gemma-3-12B su Databricks | `400: multi-turn tool calls non supportate`, 43 righe su 45 (S1) |
| deprecazione | Llama-3.1-8B su Azure | `ServiceModelDeprecated ... since 06/13/2026`, mentre Databricks lo serve |
| quota inesistente | gpt-oss-20b su Azure | catalogo dichiara `AIServices`+`GlobalStandard`, `usage list` non ha la riga, `create` rifiuta |
| disuso | Claude Sonnet 4, Opus 4.1 su Bedrock | *«marked by provider as Legacy and you have not been actively using the model in the last 30 days»* — sonda rieseguita e depositata il 2026-08-16 in `results/censimento-sonde/opus-4-1-bedrock.md`, perche' l'affermazione viveva solo in questa riga |
| giurisdizione | Llama-4-Maverick su Bedrock | *«Access to Meta Llama models is not allowed from unsupported countries, regions, or territories»* — mentre Llama 3.3 e 3.1 girano |
| **chiamate parallele** | Llama-3.3-70B su Azure | `400 UnsupportedToolUse: This model does not support more than one tool call at this time` |

**Il sesto è il più insidioso, e va letto con attenzione.** Non è il multi-turno: verificato in
tre passi il 2026-08-14 — turno 1 con un tool **passa**, turno 2 con una storia che contiene
**una** tool call **passa**, e una storia che contiene **due** tool call nello stesso messaggio
assistant viene **rifiutata**.

Conseguenza: **il censimento lo dichiara sano.** Una sonda che prova un turno, o due turni con
una chiamata per turno, non lo trova. La cella muore più tardi, nel momento in cui il modello
*decide* di chiamare due tool insieme — cioè per una scelta del modello, non per una del
disegno. È l'unico dei sei che un preflight non può prevenire, e per questo è quello che va
scritto per primo: gli altri cinque si scoprono provando, questo si scopre raccogliendo.

Lo stesso modello a pesi aperti gira senza problemi su Databricks e Bedrock.

Il caso più stretto è **gpt-oss-20b**: non comparabile su Databricks (l'output del turno 1
arriva sul canale `reasoning`), rifiutato da Azure (quota inesistente), funzionante con tool
nativo su Bedrock. Stesso modello, tre infrastrutture, tre verdetti.

## Discovery negato, invocazione permessa

Su Bedrock l'SCP `p-5osi2ndy` nega `ListFoundationModels`, `ListInferenceProfiles` e
`ListCustomModels`. Si invoca ma non si enumera: il roster si dichiara per enumerazione
esplicita, non per regola, e uno sconosciuto non può ricostruire il campione dall'account.
È un fatto di riproducibilità dell'infrastruttura e va nel paper come tale.

## Tariffe

Tutte in `pricing.json` del progetto S1, con la fonte per esteso.

| | input | output | fonte |
|---|---|---|---|
| bedrock gpt-oss-120b | $0,15 | $0,60 | Price List API, meter `USE1-gpt-oss-120b-*-tokens` |
| bedrock gpt-oss-20b | $0,07 | $0,30 | Price List API |
| bedrock Llama 3.3 70B | $0,72 | $0,72 | Price List API |
| bedrock Llama 3.1 8B | $0,22 | $0,22 | Price List API |
| bedrock Sonnet 4.5 | $3,00 | $15,00 | AWS Marketplace, tabella prezzi |
| bedrock Opus 4.5 | $5,00 | $25,00 | Marketplace + post AWS 24 nov 2025, due fonti concordi |
| bedrock Haiku 4.5 | $1,00 | $5,00 | **stima**: parità col listino diretto Anthropic, assunta |

I meter on-demand puri vanno disambiguati dalle varianti `-batch` (metà prezzo), `-flex` e
`-priority`: prendere il numero sbagliato è un errore di 2× che nessun controllo a valle
segnalerebbe.

Il Price List API di Bedrock si ferma a Claude 3 — contiene solo 2.0, 2.1, 3 Haiku, 3 Sonnet e
Instant — quindi l'assenza dei 4.5 è una lacuna di pubblicazione e non una grafia sbagliata.
Verificato enumerando i modelli Anthropic presenti, che è il controllo positivo senza il quale
«zero risultati» si sarebbe letto come «il listino non esiste».

## Costo dei bracci pieni

Quattro celle da 360 run per modello (2 cloud × 2 trasporti × 45 binari × 8 run), sul profilo
di token misurato in S1.

| | |
|---|---|
| gpt-oss-120b | $5,21 |
| llama-3.3-70b | $12,42 |
| haiku-4-5 | $36,80 |
| sonnet-4-5 | $67,78 |
| **totale** | **$122,21 ≈ 112 €** |

## Cosa si eredita da S1

L'harness con entrambi i trasporti (`agent_loop.py`, `run_agent(tool_protocol=...)`), il replay
delle traiettorie, la regola condivisa `qualita_run.e_misurazione`, i guardiani di liveness e
di budget. Il ramo `azure` di `llm_client.py` è scritto e verificato end-to-end anche se questo
studio raccoglie su due cloud.

La guardia sui prezzi ora rifiuta **prima** della chiamata: fino al 2026-08-13 il controllo
stava dopo, e un modello senza tariffa veniva fatturato per una chiamata prima di essere
respinto — misurato a 4,51 s contro 0,00 s.

## Cosa manca prima di raccogliere

- La pre-registrazione, con lo script di analisi congelato per hash **prima** che i dati
  esistano.
- Il calcolo di potenza su σ noto da S1 (0,211 come media delle SD entro-binario, 0,274 per
  pooling di varianza): decide K e le run per cella, cioè se 360 è il numero giusto.
- Il budget dichiarato per questo studio. Quello di S1 è chiuso a ~178 € su 200 e non si
  trasferisce.
