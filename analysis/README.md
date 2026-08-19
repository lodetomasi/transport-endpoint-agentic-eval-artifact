# `analysis/`

`analyze_c2.py` e' stata scritta e congelata **prima che i dati esistessero**. Si rifiuta di
calcolare su bracci parziali: i binari si processano in ordine di indice e i primi sono piu'
facili, quindi la media su un prefisso stima i binari facili. Nel capitolo precedente un braccio
a 0,936 a meta' raccolta ha chiuso a 0,832.

La famiglia e' di dieci test con **m fisso**: togliere un test a dati visti abbassa le soglie di
Holm dei sopravvissuti, quindi i non calcolabili restano dentro e non si testano.

T9 e T10 portano **due letture**: il modello misto pre-registrato, che e' il valore che entra in
Holm, e un test esatto sulle stesse quantita'. Su dati sintetici con un'interazione da 11 punti
concentrata su un modello il misto da' p = 0,14 e l'esatto p < 0,0001 — cioe' il test
pre-registrato non e' potente contro la forma di interazione piu' plausibile. Dichiarato prima
dei dati, e non corretto cambiando il test.

`potenza.py` calcola l'MDE dalla varianza del contrasto che **questo** capitolo misura, non da
quella del precedente: l'appaiamento per binario toglie la varianza fra binari, e prendere il
sigma sbagliato non fallisce — produce un K plausibile e sbagliato.
