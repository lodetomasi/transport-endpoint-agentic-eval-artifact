# `results/` — append-only

Un file non si riscrive e non si cancella. Le riesecuzioni vanno sulla catena dei suffissi
`("", "_redo", "_redo2", "_redo3")`, e si leggono concatenandola; il quinto suffisso non
esiste, perche' nessuna analisi lo leggerebbe.

```
c2_<modello>_<infra>_<trasporto>[_redoN].csv   una riga per run
trajectories/<infra>_<trasporto>/<binario>_r<n>.jsonl   il log per-turno di ogni run
```

Le traiettorie non sono scarto: sono l'evidenza grezza, ed e' grazie a loro che nel capitolo
precedente una limitazione dichiarata sui log per-turno ha potuto essere ritirata.

Cosa e' stato invalidato, e perche', sta in `README-validita.md`. Un'annotazione porta tre
cose, e la terza manca sempre: **quale lotto**, **la causa con l'evidenza**, e **il ricalcolo**
— il numero prima e dopo.
