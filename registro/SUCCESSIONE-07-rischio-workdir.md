# Successione 07 — la rete di sicurezza dichiarata nella 04 non esiste

**Data**: 2026-08-15.
**Trovato da**: il seggio metodologo del gauntlet sui risultati, confermato dall'area chair
leggendo il codice, riverificato riga per riga prima di scrivere questo documento.
**Stato**: raccolta chiusa, 16 celle su 16. Nessun dato invalidato da questa correzione.

## Che tipo di documento è

`registro/SUCCESSIONE-04-partizione.md` **non si modifica**: il registro segue lo stesso
principio append-only di `results/`. Questa successione corregge un'affermazione contenuta in
quel documento, e i due si leggono insieme.

## L'affermazione, e perché è falsa

La successione 04 ha reso concorrenti i driver per cloud. La sua sezione sul rischio residuo
diceva:

> Il rischio residuo è che i due cloud abbiano una risorsa condivisa a valle che non conosco:
> se succedesse, si vedrebbe come `infra_failure` sulle righe, che la regola di qualità esclude
> dalle misurazioni e che la ripresa per deficit ricolma.

**La risorsa condivisa esiste, e non si vedrebbe affatto come `infra_failure`.**

`src/run_minipilot.py:341` compila ogni candidato in una directory costruita **solo** su
`(prog, run_id)`:

```python
tr = compile_and_test(cand, tests, ROOT / "results" / "workv3" / f"{prog}_r{run_id}")
```

Nessun modello, nessuna infrastruttura, nessun trasporto nel percorso: le 360 directory di
`results/workv3/` sono condivise da **tutte e sedici** le celle.

E il campo `infra_failure` non può segnalarlo, per costruzione:

| riga | cosa succede |
|---|---|
| 331 | `infra = bool(getattr(res, "infra_failure", False))` — il flag è letto da `res`, cioè dall'esito della **chiamata al modello** |
| 341 | `compile_and_test(...)` viene chiamata **dopo**, e non tocca mai quel campo |

Una collisione fra due celle altererebbe `pass_rate` e `compiled` **senza alzare nessun flag**:
non sarebbe una riga scartata dalla regola di qualità, sarebbe una riga che sembra un risultato
normale. È la forma peggiore, e la 04 dichiarava chiuso il rischio proprio con l'argomento che
non regge.

## Il dettaglio che rende il difetto più netto

Lo stesso ragionamento **era già stato fatto**, e applicato alle traiettorie invece che alla
workdir. Venti righe più sopra, alla 328:

```python
# ...una cartella "N12" condivisa avrebbe fatto sovrascrivere le traiettorie
# di uno studio con quelle dell'altro, in silenzio e senza errori.
tag = Path(args.out).stem or f"N{args.turns}"
write_trajectory(res, prog, run_id, ROOT / "results" / "trajectories" / tag)
```

`write_trajectory` porta il `tag` della cella nel percorso, e il commento dice esattamente
perché: *in silenzio e senza errori*. La stessa persona che ha scritto quella riga ha lasciato
`workv3` senza tag, venti righe sotto. Il difetto non è una svista sul meccanismo — il
meccanismo era compreso e documentato. È una svista sul **secondo** posto in cui si applicava.

## Cosa è stato misurato

| | |
|---|---|
| finestra di collisione, durata della fase docker | **0,89 s** mediana |
| coppie stesso `(binario, run_id)` da celle diverse entro 2 s | **29–30**, riprodotte da due letture indipendenti |
| entro 5 s | 74 |
| entro 15 s | 130 |

Una sonda che punta contro: se una collisione fosse avvenuta, due righe vicine sullo stesso
`(binario, run_id)` avrebbero valutato lo stesso file e dovrebbero concordare **più** del caso.
Sulla coppia di celle con abbastanza casi, le vicine concordano **8,2 punti in meno** delle
lontane — il verso opposto. **Ma il seggio metodologo ha mostrato che quel segno si inverte o si
annulla controllando per l'identità del modello**, quindi la sonda non è una rassicurazione: è
l'unica sonda che i dati permettono, e non trova la firma.

## Cosa NON si fa, e perché

**Il lotto non si invalida.** A differenza del nome dell'algoritmo e del vincolo Converse, qui
non c'è un canale **sistematico e asimmetrico fra i bracci**: c'è rumore aggiuntivo non
direzionale, su una precondizione che si è verificata una trentina di volte su 5 805
misurazioni. Invalidare sarebbe sproporzionato; tacere sarebbe peggio.

**La contaminazione non è quantificabile a posteriori**: `results/workv3/` conserva solo
l'ultimo scrittore per cartella, quindi non esiste un modo di sapere, riga per riga, se una
collisione è avvenuta. Questa impossibilità è essa stessa parte di ciò che va dichiarato.

## Cosa si fa

1. **Nel paper**, la workdir condivisa va nelle minacce alla validità come minaccia **aperta**,
   con i numeri sopra e con la portata reale: poiché la chiave della cartella non contiene la
   cella, **qualunque** riga può in linea di principio collidere con qualunque altra
   dell'infrastruttura concorrente. La concentrazione osservata su una coppia di celle è un
   fatto di scheduling, non una garanzia strutturale per i contrasti di trasporto.
2. **Nel codice**, per un eventuale capitolo successivo: aggiungere modello, infrastruttura e
   trasporto al percorso di `workv3`, esattamente come `write_trajectory` fa già col suo `tag`.
   È una riga, **non retroagisce** su questi dati, e non si applica ora perché la raccolta è
   chiusa e toccare l'harness dopo i dati è ciò che questo registro esiste per impedire.

## Effetto sulla misura

**Nessuno diretto.** Non cambia un numero, non tocca un file congelato, non sposta una riga di
`results/`. Cambia un'affermazione: un rischio che il registro dichiarava presidiato non lo era,
e il documento che lo dichiarava resta agli atti con questa correzione accanto.
