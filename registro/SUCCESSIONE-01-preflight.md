# Successione 01 — preflight delle credenziali in `src/raccogli_c2.py`

**Data**: 2026-08-13. **Prima della raccolta**: nessun dato di C2 esisteva.

## Il file

`src/raccogli_c2.py`

| | sha256 |
|---|---|
| congelato il 2026-08-13 | `07a1e0b9…` *(il valore in `HASH-CONGELATI.md` prima di questa successione)* |
| dopo la modifica | vedi `HASH-CONGELATI.md` aggiornato |

## Cosa è cambiato

Aggiunta la funzione `preflight()` e la sua chiamata all'inizio di `main()` quando non è un
dry-run. Fa **una chiamata minima per provider** — un `Rispondi con la sola parola OK` a 16
token — prima di eseguire qualunque cella, e si ferma se una fallisce.

## Perché

Le credenziali dei due cloud sono meccanismi diversi: Bedrock legge `AWS_PROFILE`, Databricks
un profilo del CLI. Nessuno dei due si annuncia mancante finché non lo usi.

Senza il preflight, l'ordine di enumerazione del roster manda per prime le otto celle
Databricks: sarebbero girate per ore, e la nona sarebbe morta su `NoCredentialsError` col
costo già speso e il braccio a metà. È successo in piccolo durante il collaudo, ed è il motivo
per cui la modifica esiste.

## Effetto isolato sulla misura

**Nessuno.** Il preflight:

- non tocca il roster, i binari, i turni, la temperatura, il numero di run;
- non scrive in `results/` — la sua chiamata non passa da `run_minipilot.py` e non produce
  righe;
- costa **$0,000052** per esecuzione del driver (misurato: $0,000031 Databricks +
  $0,000021 Bedrock), che entra nella fattura ma non in nessun CSV e quindi non in nessun
  numero pubblicato.

Il contenuto delle celle raccolte è identico a quello che sarebbe stato raccolto senza.

## Verifica nei due sensi

| | |
|---|---|
| senza `AWS_PROFILE` | `preflight bedrock GUASTO`, exit 1, **nessuna cella eseguita** |
| con `AWS_PROFILE=<profilo-bedrock>` | entrambi OK, `guasti: 0` |

## Nota sulla guardia stessa

`verifica_hash.sh` accettava la presenza di **un** file `SUCCESSIONE-*.md` come prova che
qualunque divergenza fosse documentata. Era troppo debole: un documento scritto per un file
avrebbe coperto in silenzio la modifica di un altro. Dalla stessa data la guardia richiede che
il documento **nomini** il file divergente.
