# Emendamento 06 — ri-raccolta completa con directory isolate, e come si legge il confronto

**Data**: 2026-08-15, scritto **prima** di spendere il primo centesimo.
**Innesco**: la minaccia dichiarata in `SUCCESSIONE-07` — la directory di compilazione era
chiavata su programma e indice di run, senza la cella, con driver concorrenti.
**Costo**: $138,83 misurati (non stimati: somma di `cost_usd` sulle 5.805 misurazioni esistenti).

## Perché non è un rerun mirato

L'ipotesi di lavoro era rifare solo le celle esposte alla concorrenza. Misurato: **843
misurazioni su 5.805 (14,5%) hanno un'altra cella entro 2 secondi, e le celle toccate sono
16 su 16**. Il sottoinsieme esposto coincide con l'esperimento. Il compromesso non esiste, e la
ragione è un numero, non un'opinione.

## Cosa si rifà, e cosa no

Si rifanno le **sedici celle confermative**: stesso roster, stessi 45 binari, 8 run, 12 turni,
temperatura 0, stessi due trasporti, stessi due cloud. Cambia **una** cosa nell'apparato: la
directory di compilazione porta il tag della cella, correzione già entrata con `SUCCESSIONE-08`
e già esercitata dal braccio di ablazione.

**Non** si rifà il censimento (non ha directory di lavoro), **non** si rifà l'ablazione (nasce
già isolata), **non** cambia la famiglia dei dieci test né `m = 10`.

## Il tetto

`sorveglia_costi.sh` porta `C2_TETTO_USD` a 200. Il tetto è un **tripwire operativo**, non il
budget pre-registrato: nessuna ipotesi, nessun contrasto, nessuna soglia cambia. Si alza per
autorizzazione esplicita dell'utente in data odierna, ed è documentato qui perché un tripwire
alzato in silenzio non protegge più niente.

**Il valore, calcolato invece che scelto.** La prima stesura di questo documento diceva $320,
ed era sbagliata in un modo che si sarebbe visto solo a raccolta avviata:

| voce | |
|---|---|
| speso alla data | $165,60 |
| ablazione residua (già autorizzata da `SUCCESSIONE-08`, $28 stimati, $5,55 spesi) | $22,45 |
| ri-raccolta | $138,83 |
| **atteso alla fine** | **$326,88** |

A $320 il tripwire avrebbe fermato la raccolta **prima della fine**, ed è il fallimento
peggiore fra quelli disponibili: un esperimento ucciso a poche celle dal termine, con la spesa
già sostenuta e nessun risultato utilizzabile. Il tetto si porta a **$360**, che lascia un
margine del 10% — non del 4%, perché in questo progetto le stime di costo hanno già sbagliato.

Va detto con precisione cosa è cambiato rispetto a quanto autorizzato: il totale annunciato era
$302,98, quello atteso è $326,88. La differenza sono i $22,45 dell'ablazione **già in corso e
già autorizzata**, che non erano stati sommati. Non è spesa nuova; è spesa vecchia mancante da
un totale.

**Secondo aggiustamento, 16/08 08:30: da $360 a $400.** A ri-raccolta al 26,5% il conto
aggiornato dice:

| voce | |
|---|---|
| speso | $214,26 |
| residuo, stimato cella per cella ai costi che ebbero nell'originale | $126,88 |
| **atteso alla fine** | **$341,14** |

Con il tetto a $360 il margine era di **$18,86, il 5%** — e le mie stime di costo in questo
progetto hanno gia' sbagliato due volte. La differenza rispetto ai $326,88 previsti sopra viene
dallo spreco documentato in `NOTA-02`: la cella haiku dell'ablazione raccolta due volte, circa
$8,70, piu' un'ablazione un po' piu' cara della stima.

Va detto cosa alzare il tetto **non** fa: non spende. Sposta la soglia a cui il guardiano
interviene, e la spesa reale resta quella che le celle costano. Va detto anche cosa si evita, e
non e' una catastrofe: al tetto la sorveglianza uccide driver e worker, ma i CSV restano e la
catena dei suffissi riprende dai soli binari carenti — verificato. Si evita un'interruzione a
poche celle dalla fine e la ripresa manuale, non una perdita di dati.

Autorizzato dall'utente il 16/08. Il tripwire resta un tripwire: non autorizza altre
iterazioni, altri bracci, altri modelli. Solo questa ri-raccolta, che è la stessa misura con
l'apparato corretto.

## Come si legge il confronto — dichiarato ora, non a dati visti

Questo è il punto per cui il documento esiste. A dati visti, «le conclusioni sono invariate» è
una frase che si può far dire a quasi qualunque coppia di raccolte scegliendo cosa guardare.

**L'aspettativa non è l'uguaglianza.** Questo stesso capitolo misura che a temperatura zero il
punteggio non è stabile: due raccolte identiche *devono* differire, e una coincidenza esatta
sarebbe un allarme, non un successo.

Quindi si dichiarano quattro criteri, e si riportano tutti e quattro qualunque cosa dicano:

1. **Segno degli otto contrasti.** Quanti degli otto conservano il segno. Pre-dichiarato:
   invariato se **almeno 6 su 8** concordano.
2. **Esito della famiglia.** La conclusione attuale è che **nessuno** dei dieci test sopravvive
   a Holm. Invariata se anche nella nuova raccolta nessuno sopravvive; se ne sopravvive uno,
   si riporta come differenza fra le due raccolte e **non** come risultato confermativo, perché
   la famiglia è stata già spesa una volta.
3. **Copertura.** Per ciascuno degli otto, se la nuova stima puntuale cade nell'IC95 della
   vecchia. Pre-dichiarato: invariato se **almeno 6 su 8** cadono dentro.
4. **La decomposizione della varianza.** Lo 0,1% di rumore run-to-run che ha invertito la
   calibrazione di potenza si riproduce entro un ordine di grandezza, oppure no.

**Quale raccolta è la primaria, deciso adesso**: la **nuova**. Non perché darà numeri migliori
— non si sa — ma perché ha l'apparato corretto, ed è l'unico criterio disponibile prima di
vedere i risultati. La vecchia si riporta integralmente accanto, resta in `results/`
(append-only), e non viene annotata come invalidata: non c'è evidenza che lo sia, e
`README-validita.md` registra invalidazioni misurate, non sospetti.

**Se i quattro criteri divergono fra loro** — per esempio i segni tengono e la copertura no —
si riportano divergenti. Non c'è una regola di sintesi, e inventarla adesso significherebbe
sceglierla sapendo già cosa vorrei che dicesse.

## Il rischio che questo emendamento introduce

Una seconda raccolta è una seconda occasione di guardare. Il rischio è che, davanti a due
insiemi, il paper racconti quello che gli conviene. I quattro criteri sopra e la scelta
anticipata della raccolta primaria sono la contromisura; funzionano solo perché sono scritti
prima, e questo file esiste per essere confrontato con quel che il paper dirà poi.

## Cosa si scrive nel paper, e cosa non si scrive

Si scrive che un audit ha identificato un percorso di concorrenza, che i workspace sono stati
isolati e l'esperimento ri-raccolto in modo indipendente, e **quali dei quattro criteri**
risultano soddisfatti — con i numeri.

Non si scrive «le conclusioni sostanziali sono invariate» come formula, se non lo sono su tutti
e quattro. E non si scrive prima di aver visto i quattro numeri.
