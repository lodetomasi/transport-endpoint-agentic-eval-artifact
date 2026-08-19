# `registro/` — la catena delle modifiche al piano

Due tipi di documento, e la differenza non è formale:

**`SUCCESSIONE-NN-*.md`** — una modifica a un file **congelato per hash**. Si scrive **prima**
della modifica, porta l'effetto isolato sulla misura e conserva l'hash precedente.
`verifica_hash.sh` pretende che il documento **nomini** il file divergente: uno scritto per A
non copre B.

**`EMENDAMENTO-NN-*.md`** — una modifica al piano che non tocca un file congelato: il tetto di
spesa, un braccio esplorativo aggiunto.

L'ordine non è burocrazia. Scrivere il documento dopo significa deciderlo a modifica fatta, e
una giustificazione scritta a cose fatte non è la stessa cosa di una decisione presa prima.

Il paper porterà **una menzione**; questa è la catena a cui rimanda. La sintesi in ordine
cronologico sta in [`../PERCORSO.md`](../PERCORSO.md).
