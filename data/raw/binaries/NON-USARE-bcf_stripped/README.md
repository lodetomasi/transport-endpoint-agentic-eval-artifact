# NON USARE — corpus bogus-control-flow, trasformazione inefficace

60 binari costruiti il 2026-08-10 con `clang -O1 -s -mllvm -enable-bcfobf` (bogus control
flow **senza** flattening), come tentativo di una terza famiglia di trasformazione per
rispondere al rilievo «una sola trasformazione».

**Scartati prima di eseguire un solo run.** Il rapporto di salti contro il codice in chiaro
è **1,00 di mediana** (range 0,97-1,44): la trasformazione non trasforma. Sonda sui flag
della stessa build di Hikari, su `prog04_expr_parser`:

| flag | rapporto salti |
|---|---|
| `cffobf` | **×2,45** |
| `bcfobf` | ×1,00 |
| `bcfobf -bcf_prob=100` | ×1,01 |
| `bcfobf -bcf_prob=100 -bcf_loop=3` | ×1,01 |
| `subobf` | ×1,03 |
| `splitobf` | ×1,00 |
| `indibran` | ×0,81 |
| `strcry` | ×0,99 |

In questa build **solo il control-flow flattening produce una trasformazione misurabile
sul conteggio dei salti**. Alcuni di questi pass (cifratura di stringhe, sostituzione di
istruzioni) non modificherebbero comunque il conteggio dei salti, quindi la sonda non li
esclude del tutto; `bcfobf` invece dovrebbe aggiungere rami falsi, e non lo fa.

**Perché non li usiamo lo stesso.** Una condizione presentata come «terza famiglia di
trasformazione» che lascia il binario sostanzialmente non offuscato è un appiglio che un
revisore trova in dieci minuti ricompilando. Meglio dichiarare una famiglia a due intensità
molto distanti (2,88× contro 18,29× di rapporto salti) che fingerne tre.

Verificare con `probe_flags.sh` e `check_intensity.sh` dentro il container OLLVM.
