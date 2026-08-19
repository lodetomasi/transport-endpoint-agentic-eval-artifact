# Emendamento 04 — la claim di apertura era falsa, e la citazione che la falsifica va attribuita bene

**Data**: 2026-08-15, scritto **prima** di toccare i file.
**Trovato da**: il revisore di novità del gauntlet del 2026-08-14
(`reviews/proposal-2026-08-14.md`), verificato per fetch il 2026-08-15.
**Stato della raccolta**: 14 celle su 16 chiuse. Nessun dato da rifare.

## Cosa cambia

La claim di apertura. Non il disegno, non le ipotesi, non le soglie.

**Prima** — `PREREGISTRAZIONE.md` §2, `README.md`, `research/CENSIMENTO.md`:

> Nessuna valutazione agentica pubblicata dichiara quale trasporto usa.

**Dopo**:

> Nessuna valutazione **agentica multi-turno su compito downstream** incrocia il trasporto con
> l'identità del cloud gestito **a parità di pesi**, né tratta la cancellazione di un modello
> come effetto di selezione di prima classe.

## Perché: la prima è falsificabile con una citazione

La **Berkeley Function-Calling Leaderboard** pubblica per ogni modello due varianti, e le
definisce così — verbatim dalla pagina, letta il 2026-08-15:

> FC = native support for function/tool calling. Prompt = walk-around for function calling.

E il divario esiste, nella **direzione opposta** al nostro seme: **GPT-4-1106-Preview** ottiene
**85,65** in modalità Prompt contro **79,65** in modalità FC. Il testo vince di **6,00pp**, dove
Haiku in C1 perdeva 10,7pp passando al testo.

Una claim che dice «nessuno lo dichiara» cade davanti a una leaderboard che lo pubblica in
colonna. Va ristretta a ciò che regge, ed è comunque il contributo: BFCL confronta i trasporti
**a infrastruttura fissa**, su chiamate valutate in sé, e non incrocia mai il trasporto con
l'infrastruttura che lo implementa — che è l'unica cella in cui modello e infrastruttura si
separano.

## L'attribuzione, che la verifica IR-1 ha corretto

Scrivere «BFCL (Patil et al., ICML 2025) pubblica FC contro Prompting» attribuirebbe al **paper**
una cosa che sta nella **leaderboard**. I tre pezzi vanno citati separatamente:

| fatto | fonte, verificata per fetch il 2026-08-15 |
|---|---|
| la leaderboard distingue FC e Prompt, con la definizione verbatim sopra | `gorilla.cs.berkeley.edu/leaderboard.html`, versione **V4** |
| 85,65 (Prompt) contro 79,65 (FC) su GPT-4-1106-Preview | `github.com/ShishirPatil/gorilla` discussione **#606**, risposta del maintainer Shishir Patil |
| il benchmark come lavoro pubblicato | Patil, Mao, Yan, Ji, Suresh, Stoica, Gonzalez. *The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models*. ICML 2025, PMLR **267**:48371–48392 |

Due precisazioni che il fetch ha prodotto e che il paper deve portare:

1. **L'abstract del paper non menziona** il confronto fra modalità. Il numero non viene da lì.
2. **GPT-4-1106-Preview non compare più** nella leaderboard V4 corrente. Il confronto è
   verificabile nella discussione #606, che è datata — si cita quella, non «la leaderboard oggi».

## Effetto isolato sulla misura

**Nessuno.** Non si tocca: il roster, i 45 binari congelati, le 8 run per cella, i 12 turni, la
temperatura, la metrica primaria, la famiglia dei dieci test, `m` fisso a 10, nessuna soglia, il
calcolo di potenza.

È una riformulazione di **come si dice cosa è nuovo**, e i dati non ne sanno niente.

## Dove si applica, e dove NON si applica

| file | azione |
|---|---|
| `README.md` | riformulare — non è congelato |
| `research/CENSIMENTO.md` | riformulare — non è congelato |
| `DIREZIONI.md` §C2, in `<altro-repository>` | riformulare — altro repository |
| `PREREGISTRAZIONE.md` §2 | **non si tocca** |

`PERCORSO.md` §8 voce 1 diceva di applicarla anche alla pre-registrazione. **Non si fa**: la
pre-registrazione è immutabile (IR-4) ed è ora locked per hash
(`9d6145d8f09c…`, `.graph/locks.json`); la guardia rifiuta la scrittura, provata nei due sensi
il 2026-08-15. Riscrivere una claim congelata perché una revisione l'ha falsificata è
esattamente la libertà che la pre-registrazione esiste per togliere.

Quindi: **il file congelato resta con la claim del 13 agosto, e questo emendamento è la sua
correzione datata.** Il paper cita la claim ristretta e rimanda qui per la genealogia — la
stessa forma usata per i cinque-contro-sei meccanismi di cancellazione.
