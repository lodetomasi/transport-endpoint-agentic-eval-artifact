# Emendamento 01 — il tetto di spesa da $150 a $200

**Data**: 2026-08-14. **Deciso da**: l'autore. **Stato della raccolta al momento della
decisione**: 2 celle su 16 chiuse, **$12,12 spesi**.

## Cosa cambia

`C2_TETTO_USD` passa da **150** a **200**. È il valore su cui `sorveglia_costi.sh` uccide la
raccolta ed esce 2, e su cui `check_cost.sh` esce 2.

Nient'altro.

## Perché questo non è la cosa che IR-6 vieta

IR-6 dice che il budget non si alza a metà corsa, e la ragione è che un tetto spostato **nel
momento in cui lo si sta per toccare** non è un tetto: è una formalità che cede quando serve.

Qui il tetto non è vicino.

| | |
|---|---|
| speso alla decisione | **$12,12** |
| proiezione a chiusura, sui costi per-run misurati | **$124,88** |
| tetto precedente | $150 — margine 20% |
| tetto nuovo | $200 — margine 60% |

Non si sta facendo spazio a uno sforamento che è già avvenuto o imminente: si allarga un
margine mentre la proiezione resta **sotto entrambi i valori**. Se la decisione fosse arrivata
a $148 spesi sarebbe stata l'altra cosa, e andrebbe rifiutata.

La distinzione è il punto, e va scritta perché fra sei mesi le due situazioni si assomigliano
nel registro e non nei fatti.

## Cosa NON cambia

- Il disegno: 4 modelli × 2 infrastrutture × 2 trasporti, 45 binari × 8 run.
- La pre-registrazione, le ipotesi, la famiglia dei dieci test, `m` fisso.
- Le tariffe dichiarate e la guardia che rifiuta un modello senza voce prima della chiamata.
- Nessuna soglia statistica.

Il tetto è una protezione operativa contro un ciclo che va in fuga, non un parametro del
disegno. Alzarlo non rende nessun braccio più grande né nessun test più permissivo.

## Contesto: il vincolo che conta è quello complessivo

Il tetto per studio non è il vincolo vero. Quello dichiarato dall'autore è **500 € per C1 e C2
insieme**, e alla data di questo emendamento la situazione è:

| | |
|---|---|
| C1, raccolta (25.382 run) | 178 € |
| C1, gauntlet di review | 21 € |
| C2, finora | 11 € |
| **già speso** | **210 €** |
| C2, restante previsto | 104 € |
| C2, gauntlet previsto | 21 € |
| **totale a chiusura** | **~335 €** |

Margine sul vincolo complessivo: **165 €**. Alzare il tetto di studio da $150 a $200 consuma al
massimo 46 € di quel margine, e solo se la raccolta arrivasse davvero al nuovo tetto — cosa che
la proiezione esclude.

## Verifica

```bash
C2_TETTO_USD=200 ./check_cost.sh     # e la sorveglianza riavviata con lo stesso valore
```

La sorveglianza va **riavviata** perché legge la variabile all'avvio: una che continua a girare
col vecchio valore è precisamente il caso di un guardiano che sembra attivo e sorveglia altro.
