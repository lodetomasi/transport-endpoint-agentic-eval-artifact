# Successione 05 — il turno finale su Bedrock, e un vincolo dell'infrastruttura sul disegno

**Data**: 2026-08-14, scritto **prima** della modifica.
**Trovato da**: la review di disegno del gauntlet (metodologo), poi verificato di persona.

## Il file

`src/llm/llm_client.py`, ramo Converse per Bedrock.

## Il fatto, verificato e non dedotto

Il disegno prevede che **al turno finale non sia offerto nessun tool**. Non è una scelta
estetica: è documentata in `agent_loop.py` da una misura del 2026-08-09 — restringere la lista
al solo `submit_candidate` non basta, perché `gpt-oss-120b` chiama comunque
`decompile_function`, un tool non offerto. Toglierli tutti è l'unica forma che garantisce un
candidato.

Su Bedrock **quel turno non è esprimibile**. Converse rifiuta una richiesta la cui storia
contiene blocchi `toolUse`/`toolResult` se manca `toolConfig`:

```
ValidationException: The toolConfig field must be defined when using toolUse
and toolResult content blocks
```

E non esiste un modo di dichiarare i tool vietandoli: `toolChoice` ammette solo
`auto`, `any`, `tool`. Provato — `none` non è un valore valido:

```
Unknown parameter in toolConfig.toolChoice: "none", must be one of: auto, any, tool
```

**Questo è un risultato, non un difetto nostro**: una delle due infrastrutture vincola cosa
l'harness può esprimere. Va nel paper accanto ai sei meccanismi di cancellazione, perché è la
stessa classe — l'infrastruttura che decide cosa è misurabile.

## Il danno sui dati già raccolti

`results/c2_gpt-oss-120b_bedrock_native*.csv`: **29 righe** con quel `ValidationException`,
distribuite su file base, `_redo` e `_redo2`.

Sono marcate `infra_failure=True`, quindi la regola di qualità le esclude e **non entrano in
nessuna media**. Il problema non è quello.

Il problema è **chi sopravvive**. Una traiettoria arriva al turno finale con `toolUse` nella
storia solo se **non** ha già sottomesso via `submit_candidate`. Quindi le run che passano sono
esattamente quelle che hanno sottomesso **prima** del turno finale, e continuare le
riesecuzioni senza correggere arricchisce il campione di quel sottoinsieme.

È un **secondo effetto di selezione**, dentro l'unico asse che questo studio esiste per
misurare pulito. Ed è la stessa classe del difetto che C1 ha pubblicato e poi ritirato:
`infra_failure` scritto dall'harness e non gestito correttamente a valle.

## La correzione, e perché non introduce asimmetrie

Quando `tools` è vuoto ma la storia convertita contiene `toolUse`/`toolResult`, il client
costruisce un `toolConfig` **dai soli nomi già presenti nella storia**, con schema vuoto e una
descrizione che dice che non sono disponibili in questo turno.

Soddisfa l'API senza offrire nulla che il modello non abbia già visto. Le alternative scartate:

| alternativa | perché no |
|---|---|
| inviare la lista completa dei tool al turno finale | offrirebbe su Bedrock quattro tool che su Databricks non ci sono: asimmetria dentro H2 |
| appiattire la storia in testo al turno finale | renderebbe il braccio nativo di Bedrock simile a quello **testuale**: contamina il contrasto che è il soggetto |
| `toolChoice: none` | non esiste |

Verificato tre volte su `gpt-oss-120b` con la storia esatta del turno finale: `tool_calls=0` e
codice C prodotto in tutte e tre.

## Effetto isolato sulla misura

**Sul braccio testuale: nessuno.** Lì la storia non contiene mai `toolUse`, quindi la
condizione non scatta e la richiesta è identica a prima.

**Sul braccio nativo di Databricks: nessuno.** L'API OpenAI-compatibile accetta una richiesta
senza `tools` anche con `tool_calls` in storia; il ramo non viene toccato.

**Sul braccio nativo di Bedrock**: le run che prima morivano ora si completano. Il turno finale
riceve un `toolConfig` che dichiara i tool già usati con schema vuoto — il modello *potrebbe*
tentare una chiamata invece di rispondere, e quando lo fa il risultato è un run senza
candidato, esattamente come su Databricks quando un modello ignora l'istruzione finale.

**Va misurato, non assunto**: quante volte il turno finale viene speso in una tool call invece
che in una risposta, per cloud. È una covariata dichiarata prima di vedere l'esito.

## Cosa si fa dei dati pre-correzione

La cella `gpt-oss-120b/bedrock/native` va **riraccolta**, non completata. Un top-up sommerebbe
run non distorte a un campione già distorto verso chi sottomette presto, e la miscela non si
separa a valle.

`results/` è append-only: i file pre-correzione **restano**, annotati in
`results/README-validita.md` con la ragione, il conteggio e la data. La riraccolta va su una
catena di suffissi distinta, e l'annotazione dice quale catena l'analisi deve leggere.

Questo è l'unico punto che richiede una decisione dell'autore, perché tocca il registro di
validità e non solo il codice.
