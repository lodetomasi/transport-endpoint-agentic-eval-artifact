# `paper/sections/`

Una sezione per file, numerate in ordine di lettura. `main.tex` porta solo il preambolo e le
righe `\input`: un `main.tex` da duemila righe non si revisiona per sezione, produce un
conflitto a ogni modifica, e fa riportare a un errore LaTeX un numero di riga che non dice
niente.

Ogni numero traccia a un file in `results/`, altrimenti `% TODO(results)` — mai marcatori tra
parentesi quadre. I commenti sono debiti: si pagano facendo il lavoro o convertendoli in una
frase del paper, e cancellarne uno senza fare ne' l'uno ne' l'altro e' l'unico modo di sbagliare
che non lascia traccia.
