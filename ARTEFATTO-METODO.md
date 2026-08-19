# Note di metodo che il paper cita e non riporta per esteso

Il paper e' stato ridotto del 25% su richiesta di revisione, e la regola applicata al taglio e' che
**nessuna affermazione si perde**: cio' che esce dal corpo entra qui, con il rimando che il paper
porta nel punto dove stava. Questo file e' parte del pacchetto di riproduzione, quindi le
affermazioni restano verificabili contro i dati e gli script.

Il criterio del taglio, dichiarato perche' un lettore possa contestarlo: **una nota metodologica
cambia come si legge un risultato, una cronaca racconta come ci siamo arrivati.** La prima resta nel
paper, la seconda viene qui. Dove il confine non era ovvio, ha vinto il paper.

---

## I perimetri delle due guardie, e cosa ciascuna copre

Il paper dichiara che l'analisi e' protetta da hash di contenuto e da una convenzione append-only
sulla directory dei risultati, e che nessuna delle due garanzie e' larga quanto il suo nome. Il
dettaglio dei perimetri:

**La catena degli hash** copre sei file: `PREREGISTRAZIONE.md`, `analysis/analyze_c2.py`,
`analysis/potenza.py`, `configs/binari_holdout.txt`, `src/raccogli_c2.py`,
`analysis/confronto_riraccolta.py`. Non copre gli altri venticinque script di analisi, che sono
sotto controllo di versione ma non congelati: una loro modifica e' visibile nella storia git e non
fa scattare nessuna guardia. La distinzione e' deliberata --- congelare uno script che genera una
tabella impedirebbe di correggere una didascalia --- ma va detta, perche' «i file congelati sono
protetti» suggerisce un perimetro piu' largo di sei file.

**Due meccanismi diversi leggono la stessa frase.** `verifica_hash.sh` confronta gli hash
dichiarati in `HASH-CONGELATI.md` con quelli effettivi e distingue una divergenza documentata da
una muta. Il hook `guard-write` di `ironrules.py` rifiuta una scrittura su `results/` e
`data/raw/`. I due coprono insiemi differenti e nessuno dei due copre l'altro: il primo non vede
una scrittura, il secondo non vede una modifica a uno script congelato fuori da `results/`.

**L'append-only e' applicato da un hook che ferma i comandi distruttivi noti, non una redirezione
di shell ordinaria.** `rm`, `mv` e `git checkout` su `results/` sono intercettati; `echo x >
results/file.csv` no. La garanzia reale per l'append-only e' quindi **la storia committata**, che
un lettore puo' controllare, non il hook. Lo diciamo perche' un hook che intercetta i casi noti
somiglia molto a un hook che intercetta tutti i casi.

## Il criterio per invalidare un lotto

Due lotti sono stati invalidati in questo programma e uno no, e la differenza e' il criterio che
riportiamo qui perche' e' riusabile da chi legge.

**Si invalida quando il canale e' sistematico E asimmetrico fra i bracci confrontati.** I due lotti
invalidati portavano un canale informativo che favoriva un braccio e non l'altro: la contaminazione
non era rumore, era un vantaggio distribuito in modo diseguale, e nessuna correzione a valle separa
la miscela.

**Non si invalida quando il canale e' non direzionale.** La directory di compilazione condivisa
(§VIII del paper) e' una precondizione che si presenta trenta volte su 5.805 misurazioni senza
asimmetria fra i bracci: scartare il lotto sarebbe stato un gesto e non una correzione. L'apparato
che la ammetteva e' stato sostituito e l'esperimento rifatto, che e' la risposta proporzionata.

**Cio' che non si fa in nessuno dei due casi: cancellare.** Le righe invalidate restano nel
deposito con la ragione allegata e il ricalcolo accanto. Una esclusione cancellata non e'
verificabile, ed e' esattamente il difetto che il predicato di validita' esiste per prevenire.

## Le cinque proposizioni, per esteso

Il paper le elenca in forma compatta. Qui stanno con l'argomento che ciascuna porta.

1. **Il trasporto e' parte della configurazione sperimentale**, non dell'infrastruttura su cui
   gira. Appartiene alla sezione di metodo accanto alla temperatura, e la ragione e' che una
   valutazione che non lo dichiara non e' riproducibile nemmeno dallo stesso gruppo sei mesi dopo:
   il default della libreria cambia, e il numero cambia con esso senza che nessuno lo scriva.

2. **Un endpoint puo' produrre unita' sperimentali mancanti.** Un modello rifiutato non e' un
   punteggio basso: e' una riga che non esiste, e nessuna analisi la recupera a valle. Il paper
   quantifica la conseguenza (§VI): rimuovere un modello da un confronto a quattro sposta il
   divario primo-ultimo fino a 47,6pp, contro i 9,83pp del piu' grande effetto d'apparato misurato.

3. **Le componenti di varianza possono essere specifiche dell'apparato.** Una calibrazione
   ereditata da un altro apparato puo' invertire quale leva morde, non solo sbagliarne la
   dimensione. La conseguenza operativa e' che una potenza calcolata su dati altrui va ricalcolata
   sui propri appena esistono, e che la prima cella raccolta e' il momento giusto per farlo.

4. **Un preflight deve esercitare stati conversazionali realistici.** Una sonda a una chiamata per
   turno certifica configurazioni che muoiono al secondo turno, o al primo dove il modello
   raggruppa le chiamate. Due degli otto meccanismi del censimento si accendono solo in uno stato
   che una sonda ordinaria non costruisce, e il paper da' la sonda a tre passi che li raggiunge.

5. **La granularita' della metrica limita cio' che una decomposizione della varianza puo' dire.**
   Cinque unit test per compito danno a una run sei valori possibili, e una misura addensata su
   pavimento e soffitto e' da sola un meccanismo sufficiente per una grande dispersione fra
   compiti. Un disegno che poggia su una decomposizione dovrebbe dimensionare il numero di test per
   compito come dimensiona il numero di compiti --- un costo operativo, non una nota --- e riportare
   la quota di run al pavimento e al soffitto accanto alla decomposizione. Noi abbiamo fatto la
   seconda cosa e non la prima.


## Lo stesso modello, due rifiuti, secondo come lo si nomina

_Spostato dal corpo del paper nel taglio del 25%; il paper porta un rimando qui._

### The same model, two refusals, depending on how you name it

One case is worth reporting because of how we found it. A reader of a draft objected that one
of the models in the disuse row does not exist. It does, and re-probing it returned the message
the census records verbatim — but only under the regional identifier. Invoked under the plain
identifier, the same model on the same account at the same minute answers something else
entirely: **``Invocation of model ID ...\ with on-demand throughput isn't supported.
Retry your request with the ID or ARN of an inference profile''**.

Two refusals, one model, one endpoint, one minute; which one a researcher sees depends on a naming
convention. Writing the identifier the way the vendor's documentation writes it in one place rather
than another yields the conclusion that the model is unavailable for a reason that is not the
reason. This adds no mechanism — it is the same refusal by another route — but it says how a
roster gets built: **is this model available?** has no single answer even against one endpoint,
so the census records the probe and not only its verdict.


## Tre infrastrutture, tre verdetti

_Spostato dal corpo del paper nel taglio del 25%; il paper porta un rimando qui._

### Three infrastructures, three verdicts

The narrowest case in our probe is a single open-weights model that is not comparable on the
first cloud (the turn-1 output arrives on a reasoning channel), refused by the second (absent
quota), and fully functional with native tools on the third. Same weights, same request, three
infrastructures, three verdicts — and a benchmark that sampled any one of them would report a
different fact about the same model, with nothing in its tables to indicate that the other two
existed.


## Un caso che è configurazione d'account e non infrastruttura

_Spostato dal corpo del paper nel taglio del 25%; il paper porta un rimando qui._

### One case that is account configuration, not infrastructure

We report one observation at a lower level than the rest, and label it so, because it would be easy
to overclaim. On our Bedrock account a service control policy denies
**ListFoundationModels**, **ListInferenceProfiles** and **ListCustomModels**:
invocation is permitted, enumeration is not.

**This is a property of the account, not of the platform.** A service control policy is set by
whoever administers the organisation, so another team on the same platform may enumerate freely, and
nothing here supports a claim about Bedrock. It belongs in the census for one narrow reason: it
changes what **reproducibility** means for a study run under such an account. The roster cannot
be recovered from the account and must be declared by explicit enumeration in the paper — which is
what we do in (vedi il paper) — and a reader who assumes they could re-derive our sample from
an API call would be wrong. That obligation transfers to any evaluation run under a restrictive
policy, whatever the platform, and it is the transferable part. The rest is our tenant.


## Come è stato costruito il censimento

_Spostato dal corpo del paper nel taglio del 25%; il paper porta un rimando qui._

### How the census was built

The six are not a taxonomy and not a sample: they are the mechanisms we met while assembling a
roster, and the method matters more than the count.

**Who was probed.** Eleven model identities across three infrastructures, chosen by one
rule: every model we considered for the confirmatory roster, plus every model an endpoint
offered as a substitute when one was refused. The four that entered the roster are in
(vedi il paper); the other seven appear here and nowhere else, which is the point — a
census of removals can only be built from models that were candidates.

**What was recorded.** For each probe: the identifier exactly as the endpoint accepts it,
the date, and the response verbatim. Where a mechanism was found by collecting rather than by
asking, we say so and give the constructed probe that reaches the same state deliberately.

**What the denominators are.** Each mechanism carries its own, and they are not
comparable: protocol refusal was met on 43 of 45 binaries of one cell; jurisdiction and disuse
are single verbatim responses; parallel-call refusal was reached in three constructed steps.
**None of these is a rate.** We report how often we met a mechanism while building one
sample, and a different roster would meet a different set — possibly a larger one.


### Benchmark che espongono più modalità

Some agentic benchmarks do expose more than one interaction mode, so the axis is not invisible
to the field. What we did not find is a benchmark that **reports the number each mode
produced**, or which models its endpoints refused to serve. We state this as the outcome of a
search rather than attaching it to a citation, because citing a work for a claim it does not
make would be worse than reporting the absence.


### Il nome del modello non identifica un sistema

That a model name does not identify a measurable system has also been argued formally: a study
of hosted open-weight APIs defines a **service object** as **``a provider-specific,
time-varying endpoint defined by model variant, protocol behavior, context capacity, listed
price, latency and throughput distribution, reliability, and task feasibility''** and studies
version persistence across a marketplace. That work is observational rather
than agentic — it measures the market, not a task — but it names the object we manipulate.


### Dashboard industriali sullo stesso modello

Industry dashboards report the same nominal model scoring differently across commercial
providers, including on one of our models, with double-digit spreads and at least one documented
cause: a serving stack that silently ignored a reasoning-effort parameter. Those figures move as
providers are re-tested, so we cite them as a live measurement rather than a fixed result. That
work predates us and is on managed clouds, so our delta is narrower than
first-of-its-kind: what we add is the multi-turn agentic setting, the transport crossed with the
endpoint as a paired factor, and determinism measured per binary rather than per benchmark score.


### La rimozione come effetto di selezione

Removal has also been analysed as a first-class selection effect: 205 models deprecated
silently against 47 announced, and 87.8% of open-weight models deprecated over time against
80% of proprietary ones. That work names technical refusal as one of
two routes out of an arena, though its quantitative evidence concerns the curatorial route. The
distinction is about evidence, not awareness: their asymmetry is aggregate and curatorial,
decided by whoever curates and in principle appealable; ours is technical refusal by the serving
infrastructure, case by case, which nobody decides as policy and nobody can appeal.


### Ricostruzione da binari spogliati

Reconstructing source from stripped binaries with language models is an active line: models
trained for the task outperform general-purpose ones and traditional decompilers on
re-executability, and specialised architectures for assembly push
that further. We take the task as given; our variable is the apparatus
around the model, not the model's ability to do this job. That field already evaluates by
**execution** — whether reconstructed code runs and passes the original tests — and our
pass-rate is the same choice, a lower bound on semantic equivalence and never
equivalence, whose floor we measure rather than assume
((vedi il paper)).


### La sotto-potenza in questa letteratura

That experiments of this kind are routinely under-powered is established for the closest
adjacent field: statistical power **``has largely been ignored''** and under-powered
experiments are **``common in the NLP literature''**; the same has been
reported for software engineering experiments. Our
contribution to that line is not another instance of the problem but a mechanism for it that
survives good practice — we computed power in advance and the calibration still failed, in a
way (vedi il paper) characterises.


### L'effetto gemello sull'asse adiacente

The same effect has a sibling on an adjacent axis and the same task family: evaluating how well
models rewrite code to resist reverse engineering, few-shot prompting takes one model from a
29% to an 81% pass rate — 52 points produced by how the model was asked rather than by which
model answered. That study manipulates the prompt and holds the
interface fixed; this one holds the prompt fixed and manipulates the interface.


### Le righe scartate restano nel deposito

Rows the predicate rejects are **kept** in the released data with the reason attached.
Deleting them would make the exclusion unauditable, which is the failure the predicate exists
to prevent.


### Cosa insegna il meccanismo della directory condivisa

**What the mechanism teaches.** The risk had been assessed and ruled observable, on the
argument that a collision would raise an infrastructure-failure flag. It would not: that flag is
read **before** compilation runs, and compilation never writes it. Having ruled a risk
observable, the design stopped looking for it. An audit of an agentic harness should ask which
shared resources are keyed on the experimental condition, and treat ``a failure here would be
visible'' as a claim to test rather than a premise.


### La sonda che i dati ammettevano, e perche' non decide

**Diagnostic and mitigation.** The one probe these data admit: had a collision occurred,
two nearby rows sharing a program and run index would have compiled the same file and should
agree more often than chance. Nearby rows agree 8.2 percentage points **less** than distant
ones — the opposite of the expected signature — and that sign inverts or vanishes once
model identity is controlled for, so the probe finds nothing and reassures about nothing.
Because a probe that cannot settle the question is not a mitigation, the working directory now
carries the cell and the experiment was collected again, independently, on workspaces isolated
per cell. The criteria for reading that comparison — sign agreement, family outcome,
interval coverage, and the variance decomposition, each with its threshold — were written
before the comparison could be computed, and we state their timing precisely because it is
weaker than the pre-registration's and a reader should not have to reconstruct the difference.


### Le due cautele sull'ablazione, per esteso

Two cautions, both fixed in advance, and the first is the more serious. The constrained arm does
not remove batching alone: the model is refused once and stops attempting it ((vedi il paper)),
so the arm bounds what batching is worth from above rather than estimating it. **T3
therefore remains confounded, and not fully boundable.** The ablation establishes that the loss of
batching does not account for the effect — wrong direction, wrong order of magnitude — but it
cannot partition the remainder between the protocol and the behavioural change the first refusal
induces, because the same refusal is what makes the arm possible. A reader who needs T3
decomposed needs a transport that admits several calls per turn **and** a way to constrain
their number without refusing one, which this design does not provide. And the arm covers one infrastructure and the
two models that batch at all — on the other two the rate is exactly 1.000 calls per turn, so
there is nothing to remove.


### Quanto si puo' delimitare il difetto dell'84%

We can bound this only partially and say so. The affected chapter's rows are in our artifact, and
recomputing its noise share with the crashed rows excluded is the check that would settle it; what
we can state without it is that the inversion does not depend on the 84% being right. Our own
figure is 0.5% with a bootstrap interval of $[0.0, 1.4]$, and the floor it implies — 668 binaries
against 45 collected — makes ``more runs buy nothing'' true on our data alone, whatever the
earlier number was. The reversal as a **comparison between two chapters** is weaker than it
reads; the finding that the lever which binds is a property of the apparatus rests on this
chapter's own decomposition and its interval.


### Perche' il confronto fra trasporti non ha un vincitore atteso

If native function calling were reliably better than a textual protocol, an unreported
transport would be a known bias and a reader could allow for it. It is not. A public
leaderboard runs every model it ranks in both a native and a prompted mode, and on one model
the prompted mode is **ahead** by 6pp — the
opposite direction to the seed result this study grew from. A reader who knows only that
``native is better'' is not thereby able to correct for the transport; they are able to correct
for it in the wrong direction.


### Cosa il leaderboard pubblico lascia da rivendicare

That leaderboard also settles what remains to be claimed, and we take it as a constraint rather
than as an obstacle: declaring the transport is already practised where someone thought to
practise it, so the open question is not whether anyone declares it but what it costs when
nobody does. Our claim is therefore stated at that width: no agentic multi-turn
evaluation on a downstream task crosses transport with the identity of the managed cloud at
a fixed nominal model identity, and none treats the removal of a model by its serving
infrastructure as a
selection effect of first class. Strip those clauses and what remains — that serving
infrastructure changes what an evaluation measures — is not ours: it has been shown on
self-hosted engines, measured for repeated sampling at nominal
temperature zero, and documented for public arenas as curatorial
asymmetry. The contribution is the crossing, and the census.


### I quattro risultati stabiliti su cui questo lavoro poggia

This paper stands on four results that are already established, and it is worth naming them
because they are the reason the question is worth measuring rather than arguing: transport moves
a score, the serving stack moves it, differential removal from a public arena is a selection
effect, and the harness matters more than the model it wraps. Each is a component of an apparatus shown to matter. None has been taken
apart under a paired design and crossed with the identity of the endpoint, which is what we do
— and the discipline under which we do it is part of the contribution rather than a
formality.


### Che tipo di paper e' questo

This is a measurement paper about an apparatus, and it is submitted to a software engineering
venue for that reason. Its contribution is of the kind that venue evaluates well: a
pre-registered design whose analysis script was frozen by hash **before the data existed**,
an artifact in which every number regenerates from a committed script, a census of failures
recorded with the verbatim message of the system that produced them, and a null confirmatory
result reported with the power that produced it rather than quietly reframed. Two of the four
findings below were not sought and could not have been — one of them tells us that a power
calibration does not travel between apparatuses, which is a claim about how this kind of
experiment should be sized, not about which model is better.


### Cio' che questo lavoro NON rivendica

Not that one transport is better — we measure that the choice moves the number, not which
choice is right. Not semantic equivalence: pass-rate is a lower bound with a floor we measure
rather than assume. Not that the eight mechanisms are exhaustive; they are eight met while
building a sample of eleven probed models, each an existence proof with its own denominator,
and never a rate. And not that the effect size travels: it is measured on one task family
— reconstructing C from stripped binaries — on four models and two clouds, and the
pre-registration bounds the claim to exactly that. What we do claim beyond it is narrower and
harder to escape: an evaluation that does not report its transport is not reproducible from
its method section, whatever the task.


### Il rapporto con l'argomento sull'harness

We are downstream of that argument rather than in competition with it. What those works treat as
one object — context construction, tool interaction, orchestration, verification — we take
apart along one seam: a **single** component, the transport of a tool call, manipulated as a
paired factor at a fixed nominal model identity, crossed with the identity of the endpoint.
And we add what
their framing does not reach: an endpoint can decline to serve a model at all, which is not a
harness configuration a benchmark can disclose but a row that never appears.


### Le due differenze fra i trasporti, per esteso

First, **the textual protocol admits one call per turn and the native one does not.** A
native turn in which the model emits several calls executes all of them; the textual
protocol structurally forces one. The comparison is therefore between a protocol change and
a batching change bundled together, and we report the batching rate per model as a declared
covariate rather than adjusting for it — adjusting would alter a pre-registered design
after seeing the data. Where the rate is one call per turn on both sides, the two changes
coincide and the contrast is clean; where it is not, the reader is told.


### Perche' H1 e H2 sono disgiuntive

H1 and H2 are stated disjunctively — **for at least one model** — and the asymmetry is
declared in advance rather than discovered afterwards. Rejecting ``every model lies within a
narrow band'' requires one model outside it. **Confirming** that statement requires an
equivalence test on each model, and $K=45$ does not power one at the band we pre-registered.
The falsifier band is $\pm3$pp. At $K=45$ the design's minimum detectable effect is 4.87pp
under the conservative standard deviation available before collection, and an equivalence test
at the band would require 99--119 binaries. We therefore pre-registered that a null result
would be reported as an interval excluding effects above a stated size, never as equivalence.
The observed standard deviations later made even this single figure optimistic for five of the
eight contrasts ((vedi il paper)).


### Le due serie di p, e perche' entrambe sono nel deposito

$^\ddagger$ The $p$-values are Student's $t$; the frozen analysis script computes a corrected
normal approximation instead, because **scipy** was not guaranteed in the collection
environment and an analysis that does not run where the data are collected is one somebody will
redo by hand. That approximation **understates** $p$ in all eight contrasts, by 0.0004 to
0.0053 — always in the direction that makes an effect look more significant. Reporting the
exact values costs nothing because no Holm outcome changes under either series, on either
collection, and all four series are in the artifact. We report the difference rather than
presenting the final series as though it had always been the one.


### Il secondo p di T9 e T10: due domande diverse

Two entries carry a second $p$-value that the frozen script also prints: $0.0140$ for T9 and
$0.0168$ for T10. They are not second estimates of the same quantity. The mixed model uses both
endpoints and treats the model as a random effect over four levels, which is weak by
construction against heterogeneity concentrated in one model; the exact test is a one-way
analysis on one endpoint only, treating the 45 binaries as replicates. Two different questions
over different subsets of the data. The mixed model is what enters Holm, because it is what the
pre-registration fixed, not because it is the only computable one.


### La cella a 44 binari, e l'impatto dell'escluderla

One cell contributes 44 complete binaries rather than 45. On
**gpt-oss-120b**/\allowbreak**bedrock**/\allowbreak native the endpoint rejected the
eighth run of one binary outright, for the reason set out in (vedi il paper): the serving
stack does not reconcile the chat format of the model it hosts with the validation regex of its
own API. The frozen analysis includes that binary at the seven runs it has, so $K$ remains 45
for T5; excluding it moves the contrast by $0.14$pp and its $p$ by $0.021$, neither of which
approaches the Holm threshold at that rank. We report the behaviour of the frozen script and
the size of the alternative rather than choosing between them.


### La covariata delle chiamate per turno

**Calls per turn.** The text protocol used here permits exactly one tool call per turn by
construction. Under the native transport haiku averages 1.438 calls per turn (38% of turns
carry more than one) and sonnet 1.333 (33%), while gpt-oss and llama sit at exactly 1.000. T3
and T4 therefore confound a change of protocol with the loss of call batching; T1 and T2 do
not. Sixty-eight runs exhaust the twelve-turn budget, all native and none textual, so for those
runs batching is what allowed the trajectory to finish: the confound is stronger than a budget
argument would delimit, not weaker. The original collection shows the same asymmetry at 55
runs, also entirely native.


### Il posizionamento dell'inversione nella letteratura

That a power calibration can fail to transfer is not new in itself, and we do not claim it as
such. Designing a study on an effect size estimated from earlier data is known to miss its
target power through accuracy and follow-up bias, and multi-centre trial
design has treated between-site variance as something to be modelled rather than borrowed for
decades. What follows is that literature met on a new object, with one feature we did not find
stated elsewhere: the failure here is not a magnitude drifting: it is a reversal of which lever
binds.


### Perche' i casi non sono un tasso

**These are documented cases, not a rate.** Eleven model identities were probed across three
infrastructures — every model considered for the roster, plus every substitute an endpoint offered
when one was refused. Each case carries the endpoint's message and its own denominator, and the set
is open: we report what we met while building one sample, and a different sample would meet others.
One of the six was added a day after the pre-registration was frozen, which is why \S9 there says
five and this section says six, with the dates on both.


### La sonda a tre passi per le chiamate parallele

Parallel calls fail only in a state ordinary probing does not reach, and we established it in three
steps: a first turn offering one tool passes; a second turn whose history holds **one** tool call
passes; a history holding **two** calls in one assistant message is refused. A pre-flight sending
one call per turn therefore certifies the model as healthy, and the cell dies later, when the model
**chooses** to issue two calls at once — a choice that belongs to the model, so the failure
arrives at a time the experimenter does not pick. The useful consequence is that those three steps
are themselves a probe: hand-assemble that history and the endpoint answers before any collection is
paid for.


### Perche' l'ottavo caso e' un meccanismo e non un guasto

Two features make this a mechanism rather than a fault. It is not repairable from the measuring
side, so it does not stop happening. And it is **transport-specific**: under the textual
protocol the tool name never travels in the **toolUse** field, so the validator never sees
it. The textual transport is immune to a mechanism that kills the native one — on the axis this
study exists to measure. It appears in one cell of sixteen in both batches: the open-weights
model, on the cloud that did not train it, on the native transport only.


### Il confine e' la riparazione

The boundary is repair. Six of our eight mechanisms are explicit refusals issued by a healthy
endpoint behaving as configured — a 400, a deprecation notice with a date, a quota row that
does not exist, a geographic block. Nothing is broken, so nothing is fixed, and the refusal
holds for the whole duration of a study rather than clearing on retry. In that taxonomy's own
vocabulary they would scatter across three layers; the row nearest to them, model behaviour, is
declared **intentionally empty** for want of an evidence-grade reproducible report.


### L'asimmetria del costo di verifica

That asymmetry is why the census and the crossing carry the evidential weight here, and the
timing is worth stating precisely because it is unusually favourable: the census was
pre-registered as exploratory, and the decision to lead with it was taken in a design review
held **after** collection but **before** any confirmatory number was read. The
pre-registered family of ten tests, its thresholds and its fixed $m$ are reported in full and
unchanged. A reader can therefore check both halves independently — what was fixed in advance,
and what we chose to emphasise once the apparatus, not the results, was in view.


### La raccomandazione sul roster

**Report who is missing and why.** A roster is the output of a selection performed by the
infrastructure, and the eight mechanisms of (vedi il paper) are eight ways that selection
happens without anyone deciding it. This is the item with no counterpart in current checklists,
and it is the one we would add: a study reports the models it evaluated, and nothing obliges it
to report the models it could not. On one of our two clouds, enumeration of the catalogue is
denied by policy while invocation is permitted, so a stranger holding the account cannot even
reconstruct which models were available to be excluded — which makes the reporting obligation
fall on the authors, because it cannot fall on the reader.


### Il confondimento del batching, per esteso

The transport result was confounded with call batching on the two models that use it, and no
budget argument delimits it: sixty-eight runs exhaust the turn budget and all of them are native.
We therefore ran the ablation the confound requires — native transport forced to one call per
turn, everything else held — and it bounds the confound rather than leaving it declared
((vedi il paper)). Removing batching from the native transport does not lower the score on
either model, so the loss of batching is not a plausible account of the transport effect, in
direction or in magnitude.


### Le tre robustezze dell'inversione, per esteso

This is a reversed mechanism rather than a magnitude error, and it survives three independent
changes. It survives a change of estimator: recomputing the previous chapter with the estimator
used here gives 130.7% noise and $K=0$, so the inversion widens rather than closes. It survives
a change of apparatus and workspace isolation: the original collection here gave $0.1%$ and
$K=705$, the re-collection $0.5%$ and $K=668$ — the same conclusion at a factor of five on
the smaller quantity and 5% on the larger, which is the agreement the pre-registered criterion
asked for. And it survives on the other high-variance contrast, where T6 gives 9.3% and $K=487$
against 9.1% and $K=380$.


### Il disegno del braccio di ablazione, per esteso

The pre-registered contrast between transports moves two things at once on the models that
batch: the format of the call, and the number of calls a turn admits. Native allows several,
the textual protocol allows one, and haiku issues 1.438 calls per turn against sonnet's 1.333.
A declared confound is not a bounded one, so we collected the arm that separates them: native
transport forced to **one call per turn**, everything else — model, endpoint, corpus,
runs, turns, temperature — held fixed. The arm is exploratory, does not enter the family of
ten, and its stopping criterion was fixed before it ran.


### La raccomandazione sul trasporto

**Declare the transport** as you declare the model and the temperature. This sharpens an
existing requirement rather than adding one: the harness must already be described once it goes
beyond bare API calls, and the encoding of a tool call sits inside them. It is invisible in
current method sections and it is worth points — in either direction, as the leaderboard that
publishes both modes shows.


### Il predicato di validita', per esteso

A single predicate decides whether a row is a measurement, and the same predicate is used by
the collector and by the analysis. Two definitions of validity, one in each half of a
pipeline, diverge silently: in the preceding chapter of this programme a flag written by the
harness and read by none of the analysis scripts caused rows that were crashes to be averaged
as zeroes, and a cross-model boundary derived from them was published and withdrawn.


### Il meccanismo della directory condivisa, per esteso

**Threat.** Candidates were compiled in a directory keyed on the program and run index and
on nothing else — not the model, not the infrastructure, not the transport — so sixteen
cells shared 360 directories under concurrent collection. Two cells can write the same file
while a third process reads it, and a run that compiles another cell's candidate is scored
normally: no flag is raised and the row is indistinguishable from a clean one. Because the key
omits the cell, no contrast is structurally exempt.


### La provenienza del corpus

The binaries are the held-out split of the preceding chapter's
corpus, frozen by name and by
hash before collection. Reusing them rather than building a new corpus keeps the comparison
across chapters direct instead of argued, and leaves the transport as the only variable that
moves.


### Le due conseguenze del determinismo

Two consequences follow. First, the very narrow interval on T7 ($[-0.1,+0.6]$) is not high power
but absence of noise, and the distinction matters when reading Table~\ref{tab:tests}.


### L'argomento sull'harness nel suo complesso

For agents, that argument has already been made about the harness as a whole: **``the agent
execution harness \ldots\ is often a stronger determinant of agent performance than the model it
wraps''**, and current protocols **``systematically misattribute harness-level gains to model
improvements''**. A companion benchmark measures harness effects across
106 tasks and 5{,}194 trajectories and concludes that **``agent capability should be reported
at the model-harness configuration level rather than attributed to the base
model''**.

### La finestra fra scrittura e lettura, e la sonda che i dati ammettevano

Citato da §VIII, «Internal validity». La finestra fra la scrittura del candidato e la sua lettura è
**0,89 s**, e 74 coppie di righe da celle diverse condividono programma e indice di run entro cinque
secondi (30 entro due). La sonda che questi dati ammettono: righe vicine che condividono programma e
indice concordano **8,2 punti percentuali in MENO** di quelle distanti — il verso opposto alla firma
di una collisione — e quel segno svanisce quando si controlla per l'identità del modello. Non decide
nulla in nessuno dei due sensi, ed è per questo che non è una mitigazione: la mitigazione è la
directory che ora porta la cella, e la ri-raccolta su workspace isolati.

### Perché la designazione della base primaria è argomentata e non certificata

Citato da §VIII. I due numeri che delimitano la differenza: all'mtime dello script dei criteri
esistevano 112 delle eventuali 5.880 righe (**1,9%**), tutte da una **singola** cella su sedici; i
file entrano in version control il giorno dopo, quando esisteva il **73,4%** delle righe. Nessuno dei
quattro criteri è calcolabile da un modello solo — confrontano otto contrasti appaiati fra le due
raccolte — quindi il loro contenuto non può essere stato informato dal loro esito, e questo è
verificabile nelle righe rilasciate. Ciò che non è verificabile è la precedenza temporale in sé: un
mtime si può riscrivere. La pre-registrazione propria non condivide questa debolezza — committata 22
ore prima della prima riga della raccolta originale, e quella precedenza si verifica.

### La tassonomia dei guasti, livello per livello

Citato da §VI, «Why this is the part that is new». La tassonomia più vicina classifica i guasti del
serving multi-provider per **livello d'origine e rilevabilità**: rete e trasporto, streaming e
protocollo, stato e sessione, comportamento del modello, governance e costo. Due dei cinque livelli
raggiungono già fallimenti che precedono la generazione — «TCP timeouts, TLS handshake failures, DNS
resolution issues» sotto rete e trasporto, «rate-limit counters that leak and never recover» sotto
governance — quindi il confine che tracciamo non è il momento della generazione. È la **riparazione**:
ogni voce di quella tassonomia è qualcosa che smette di succedere quando viene riparata, mentre un
endpoint che rifiuta un'identità di modello per giurisdizione o per deprecazione non è un guasto da
riparare. Ed è già stato mostrato, altrove, sia che l'infrastruttura di serving cambia ciò che una
valutazione misura (su motori self-hosted e task a turno singolo) sia che la rimozione differenziale
da un'arena pubblica è un effetto di selezione con conseguenze misurabili — quel lavoro nomina il
rifiuto tecnico come una delle due vie d'uscita, e la sua evidenza quantitativa riguarda l'altra.

### La distribuzione del pavimento della metrica

Citato da §V, «What the metric buys, measured». Le 53 run che non hanno chiamato **nessuno** strumento
— il modello risponde al primo turno senza mai leggere la decompilazione — hanno media 0,1132, mediana
0,00, massimo 0,40, e il massimo cade su un singolo binario. Le 5.756 run che hanno chiamato almeno uno
strumento hanno media 0,6378. Cinque unit test per binario premiano una firma plausibile: il pavimento
esiste, è misurato invece che assunto, e non domina.

### I sei default ereditati, ciascuno col difetto a cui risponde

Citato da §IV. Ogni vincolo nasce da un difetto che nel capitolo precedente ha prodotto un numero
pulito e falso.

- **Il sorgente candidato non si avvolge mai in markup.** Un candidato avvolto misura la
  formattazione, non la ricostruzione.
- **Le funzioni si presentano in ordine nativo, mai ordinate per dimensione.** Nel capitolo
  precedente l'ordinamento era un vantaggio non dichiarato a un braccio.
- **Le tabelle dei simboli si spogliano da ogni binario.** Con i simboli presenti il binario nomina
  il proprio algoritmo e il baseline sale di conseguenza.
- **Un turno di solo ragionamento non si registra come punteggio zero.**
- **La guardia dei prezzi rifiuta PRIMA della chiamata al provider, non dopo**: un modello senza
  tariffa dichiarata non deve essere fatturato per una richiesta che viene poi rifiutata.
- **Il parametro del limite di token si invia col nome che l'endpoint accetta**, senza fallback
  prova-uno-poi-l'altro — un fallback fa dipendere la richiesta effettivamente inviata da un ramo
  d'errore.

### Quanto vale, in aritmetica, tenere m=10 invece di m=8

Citato da §V. Otto dei dieci test sono contrasti appaiati; T9 e T10 sono un modello misto e
un'interazione sulle stesse righe, quindi la famiglia di dieci contiene due test non indipendenti
dagli otto e che rispondono a domande diverse. Holm a m=10 divide la soglia più piccola per dieci
invece che per otto: **0,0050 invece di 0,0063**. Il p di T6, 0,0191, manca entrambe, quindi qui
nessuna conclusione dipende dalla scelta — ma su uno studio il cui p più piccolo cadesse fra le due
soglie dipenderebbe, e chi legge deve sapere quale delle due è stata usata e perché. Teniamo m=10
perché è ciò che la pre-registrazione ha fissato e perché è la direzione conservativa, non perché sia
l'unico conteggio difendibile.

### Il meccanismo per cui un flag di validità gonfia la quota di rumore

Citato da §V, RQ6. Nel capitolo precedente un flag scritto dall'harness e letto da nessuno script di
analisi faceva mediare come zeri le righe andate in crash, e un confine fra modelli derivato da quelle
righe è stato pubblicato e ritirato. La quota di rumore che eredita questo capitolo è calcolata sulla
stessa raccolta. Mediare i crash come zeri gonfia la varianza **entro** binario — un crash cade a
zero mentre le run vere del modello cadono altrove, quindi le run di uno stesso binario discordano
più di quanto il modello le abbia fatte discordare — e la quota di rumore è esattamente la componente
entro-binario sul totale. Da qui la direzione è nota anche dove la magnitudine non lo è: il difetto
spinge la cifra ereditata **in alto**, cioè nella direzione che fa sembrare il nostro 0,5% un
capovolgimento più grande di quanto sia.
