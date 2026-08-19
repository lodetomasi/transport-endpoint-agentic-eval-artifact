# Deviazione 01 — ripristino di otto file di `results/esplorativo/`

**Data**: 2026-08-17.
**Regola coinvolta**: IR-5, `results/` e `data/raw/` sono append-only.
**Autorizzazione**: richiesta e concessa dall'autore prima dell'esecuzione, con la situazione
descritta sotto per intero.

## Cosa è successo

`analysis/replay_trasporto.py` derivava il percorso di **lettura** dal prefisso del braccio
(`c2_` per il confermativo, `c2r_` per la ri-raccolta) ma il nome del file di **scrittura** era
fisso a `c2x_replay_materiale_{modello}_{infra}.json`. Rigiocando la ri-raccolta per aggiornare
la covariata «materiale acquisito», lo script ha quindi sovrascritto gli otto file del braccio
confermativo con i dati di un braccio diverso, in silenzio.

È il difetto che `CLAUDE.md` documenta già — *cartelle distinte non bastano: il tag viene dal
NOME* — ripetuto sull'output invece che sull'input. La correzione precedente aveva parametrizzato
la lettura, e la lettura era l'unico posto in cui il difetto era stato cercato.

## Perché il ripristino non perde nessun dato

Due insiemi, entrambi conservati prima di toccare qualsiasi cosa:

| dato | dove sta ora |
|---|---|
| replay della ri-raccolta (il nuovo) | `results/esplorativo/c2xr_replay_materiale_*.json`, otto file depositati |
| replay del confermativo (l'originale) | committato in `git`, recuperabile a `HEAD` |

Il comando eseguito è `git checkout -- results/esplorativo/`, che riporta gli otto `c2x_` al loro
contenuto committato. La guardia `ironrules.py guard-bash` lo blocca perché il pattern
`git checkout` su `results/` **scarta il working tree**, e in generale scartare risultati è
esattamente ciò che IR-5 vieta. Qui il working tree conteneva dati già depositati altrove, quindi
l'operazione è un ripristino e non uno scarto — ma la guardia non può distinguere i due casi, e
ha ragione a non provarci: la distinzione richiede di sapere che i dati sono stati salvati sotto
un altro nome, cosa che un hook non può verificare.

## Cosa impedisce il ritorno

Non basta correggere il nome: la stessa dinamica tornerebbe al prossimo braccio. Due cambiamenti,
non uno:

1. Il nome dell'output deriva dal **medesimo parametro** della lettura, quindi non esiste più uno
   stato in cui i due divergono.
2. Lo script **rifiuta di sovrascrivere** un file di `results/` che esiste già, ed esce 2. Se il
   dato va davvero rigenerato, `C2_SOVRASCRIVI=1` lo dichiara esplicitamente — il che rende la
   sovrascrittura una decisione visibile nel comando invece di un effetto collaterale del nome.

Provata nei due sensi: rifiuta su `c2xr_` esistente e su `c2x_` esistente.

## Cosa questa deviazione NON autorizza

Non autorizza a scartare risultati. Non autorizza a usare `git checkout` su `results/` in altre
circostanze. La condizione che la rende ammissibile è verificabile e va riverificata ogni volta:
**ogni riga che il working tree sta per perdere esiste già altrove, con un nome proprio.**
Se quella condizione non è vera, la risposta corretta al blocco è depositare i dati, non chiedere
un'eccezione.
