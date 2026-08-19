# Emendamento 07 — destinazione EMSE, e cosa cambia nel materiale

**Data**: 2026-08-15.
**Decisione dell'utente**: EMSE.

**Aggiornata il 2026-08-16: numero generale, NON la special issue.** La special issue *Agentic
Software Engineering: The Rise of AI Teammates* (scadenza 28 settembre) era la scelta iniziale,
e l'ho raccomandata io. Il seggio novita' ha letto la call e ha misurato il fit: il paper tocca
**un topic su dieci** — *taxonomies of agent failures* — mentre il taglio dichiarato e' la
collaborazione uomo-agente, l'autorship di codice, i task a livello di repository. Qui non c'e'
umano nel loop e il compito e' agente-contro-oracolo. Un guest editor che legge i topic prima
dell'abstract puo' archiviarlo come fuori fuoco senza entrare nel merito, ed e' un rischio che
non riguarda la qualita' del lavoro.

Il secondo argomento e' indipendente dal primo: sei settimane devono contenere la chiusura della
ri-raccolta, il deposito dell'artefatto con un DOI e l'ultimo giro di revisione. Fattibile senza
margine — e questo paper vive dell'artefatto, che e' la parte che la fretta rovina.

Nel numero generale si perdono i revisori tematici e si guadagnano: nessuna scadenza, nessuna
lente sbagliata, e una sede dove la pre-registrazione con analisi congelata e un risultato nullo
riportato con la sua potenza sono un formato riconosciuto invece che una debolezza.

**Innesco**: il capitolo era impaginato per una conferenza a 10+2 pagine per un'assunzione mai
verificata. <sede-anonima> è la destinazione di C1, non di questo.

## Cosa la scelta risolve, e non è poco

**Il limite di pagine cade.** Il paper è a 14 pagine e cresceva per ragioni buone — censimento,
bande di incertezza, metodi completi. Il taglio pianificato non si fa. La regola «non tagliare
sul censimento» resta vera ma non deve più essere difesa contro un vincolo tipografico.

**La revisione è a cieco singolo.** Verificato sulle politiche del journal: i revisori conoscono
gli autori. Tre conseguenze materiali:

1. **L'artefatto non si reda.** Era il nodo aperto: la redazione cambia l'hash di un file che il
   paper cita, e una guardia di integrità che fallisce dentro l'artefatto costruito per
   dimostrare integrità è peggio di nessuna guardia. Il deposito parte con la catena intatta.
2. **Il capitolo precedente diventa citabile.** I due numeri presi da C1 — la calibrazione di
   potenza e l'asimmetria di esposizione ai tool — smettono di essere «il capitolo precedente»
   e diventano un riferimento con una fonte. La tracciabilità migliora invece di peggiorare.
   Se C1 è sotto revisione a cieco doppio altrove, lo si cita in terza persona come preprint:
   la citazione resta verificabile e non compromette quella sottomissione.
3. **Il controllo di de-anonimizzazione cambia di segno.** `paper.py anon` finora cercava
   identificatori da rimuovere; per questa destinazione l'assenza di autore e affiliazione è il
   difetto. Va ricontrollato nel verso giusto prima di spedire.

## Cosa la scelta non risolve

Nessuna venue dà certezza di accettazione, e questa non fa eccezione. Cio' che dà è un pubblico
dichiarato: la call elenca *Failure Patterns and Risks* e *Testing and Evaluation* fra i temi, e
il censimento è il primo mentre il disegno è il secondo. Il fit è dichiarato nella call, non
argomentato da noi.

Il soffitto già osservato dall'area chair resta: il risultato confermativo è nullo e
sotto-potenziato per costruzione, e nessun riposizionamento lo cambia. Cio' che regge il peso
è il censimento — riproducibile a costo quasi nullo da chiunque abbia un account — e
l'inversione della calibrazione di potenza.

## Formato

Non si converte al template Springer prima di sapere se la prima sottomissione lo richiede:
molti journal del gruppo accettano formato libero alla prima tornata e chiedono il template solo
in accettazione. Da verificare sulle istruzioni per autori prima di spendere lavoro di
impaginazione, che è reversibile male.

## Sull'ordine delle cose

Questo emendamento **non** autorizza a scrivere risultati che non esistono. La ri-raccolta di
`EMENDAMENTO-06` è in corso e i suoi quattro criteri sono congelati; il paper si aggiorna quando
quei quattro numeri esistono, non prima, e la scadenza del 28 settembre non è una ragione per
invertire quest'ordine.

## Il titolo, 2026-08-16

Da «Your Tool Transport Is a Free Parameter: What the Endpoint Removes Before You Can Measure
It, and How Much of the Rest the Interface Buys» a:

> **Transport and Endpoint as Free Parameters in Agentic Evaluation:
> A Pre-Registered Study of Four Models Across Two Clouds**

Ventisei parole diventano quindici, e cade la formula di serie con C1. La ragione non e' la
lunghezza: e' che i titoli di quella sede sono **descrittivi**, non slogan — «An evaluation
study of…», «Reflections on the Reproducibility of…», «Empirical benchmarking of…». Un titolo
a effetto e' da conferenza, dove compete per attenzione in un programma; in un journal deve
dire cosa e' stato fatto, perche' un editor lo classifichi al primo sguardo.

Cosa si guadagna, oltre all'adeguatezza: **«pre-registered» compare in prima pagina**, ed e' un
segnale che questa sede legge — la disciplina e' meta' del contributo e ora si vede prima
dell'abstract.

Cosa si perde: il riconoscimento a colpo d'occhio della serie. Resta visibile dal contenuto e
dalla citazione esplicita al capitolo precedente, che con il cieco singolo si puo' fare in
chiaro. E' il posto giusto: la serie si riconosce leggendo, non dal frontespizio.
