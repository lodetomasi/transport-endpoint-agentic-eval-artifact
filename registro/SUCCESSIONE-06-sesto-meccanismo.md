# Successione 06 — il roster esplorativo e le due celle Azure non eseguibili

**Data del documento**: 2026-08-15. **Data della modifica**: 2026-08-14, commit `35b29c0`.
**File**: `src/raccogli_c2.py`.

## Questo documento è scritto DOPO la modifica, e la regola dice prima

La regola del progetto è che il documento di successione si scrive **prima** di toccare un file
congelato. Qui non è andata così, e la ragione è precisa: la modifica era documentata in
sostanza — è l'**emendamento 02**, che descrive il braccio Azure e il rifiuto di protocollo —
ma la tabella degli hash non è stata aggiornata, e nessun documento `SUCCESSIONE-*` nominava
il file per **questa** modifica.

Il documento arriva tardi. Il fatto che nomina è verificato e non dedotto.

## Cosa è cambiato

| | sha256 |
|---|---|
| dopo la successione 04 (dichiarato fino a oggi) | `8fd465d28f554c28c5802acddf9169130c8018aa5a8413b4d55e802b784930fd` |
| dopo questa modifica | `c62936acb4ba4ddbf0737d72105fde8b0bc320a2cca8e40247d1b8ad663b6163` |

Il diff, per intero:

1. **`ROSTER_ESPLORATIVO`** aggiunto — due modelli su Azure, raggiungibili solo con
   `--esplorativo`. Non è unito a `ROSTER`: `celle()` alimenta la famiglia confermativa dei
   dieci test, e un braccio esplorativo che vi entrasse cambierebbe `m` a dati parzialmente
   visti, spostando ogni soglia di Holm.
2. **`NON_ESEGUIBILI`** popolato con due celle, entrambe `llama-3.3-70b/azure`, col messaggio
   verbatim dell'endpoint: `400 UnsupportedToolUse: This model does not support more than one
   tool call at this time`.
3. `preflight()` esteso al braccio esplorativo.

## Effetto isolato sulla misura confermativa: nessuno

Le due chiavi di `NON_ESEGUIBILI` hanno `azure` come infrastruttura, e `azure` non compare in
`ROSTER`. Le sedici celle confermative sono quindi **intatte**, e la verifica non è
argomentata: a raccolta chiusa tutte e sedici portano 45 binari e almeno 360 run valide.

Non si toccano: i 45 binari congelati, le 8 run per cella, i 12 turni, la temperatura, la
metrica primaria, la famiglia dei dieci test, `m` fisso a 10, nessuna soglia.

## Il difetto vero non è la modifica: è che la guardia non poteva vederla

`verifica_hash.sh` accettava una divergenza quando **esisteva** un documento `SUCCESSIONE-*.md`
che nominava il file. Bastava che il file avesse avuto **una** successione, in qualunque momento
del passato, perché ogni modifica successiva passasse in silenzio: la guardia rispondeva a «questo
file ha mai avuto una successione?» mentre la domanda è «questa modifica è documentata?».

È la stessa classe che la guardia esisteva per chiudere, un livello più su. La sua prima versione
accettava un documento qualunque; la correzione pretese che il documento **nominasse** il file;
e restava che il primo documento coprisse per sempre tutti i cambiamenti seguenti.

**Correzione**: il documento deve nominare il file **e dichiarare l'hash effettivo**. Un
cambiamento non documentato lascia sul disco un hash che nessun documento contiene, e la
divergenza torna muta — cioè visibile.

Hash effettivo dichiarato da questo documento:
`c62936acb4ba4ddbf0737d72105fde8b0bc320a2cca8e40247d1b8ad663b6163`.
