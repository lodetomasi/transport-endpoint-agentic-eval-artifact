# `src/` — l'harness e i driver

`harness/` e' ereditato dal capitolo precedente e regge **entrambi i trasporti**:
`run_agent(..., tool_protocol="native"|"text")`. Il protocollo testuale e' la costante
`TEXT_TOOL_PROTOCOL` in `agent_loop.py` — il modello chiude la risposta con una sola riga
`TOOL_CALL: {...}`, il campo `tools` della richiesta **non viene inviato**, e l'output del tool
torna come messaggio `user`.

`qualita_run.py` e' **la** regola su cosa conta come misurazione. Una sola, condivisa fra
raccolta e analisi: due definizioni divergono, e la divergenza non fa rumore. Nel capitolo
precedente un campo scritto dall'harness e letto da nessuno dei tre script di analisi produsse
204 righe mediate come pass_rate = 0, e il risultato che ne usci' fu pubblicato e poi ritirato.

`raccogli_c2.py` enumera le 16 celle, fa il preflight, e riprende quelle parziali.
`completa_celle.py` calcola il deficit per binario sulla catena dei suffissi.
`run_minipilot.py` esegue una cella: `ROOT` sono i dati, `SRC` e' il codice — due costanti,
perche' unirle rompe l'una o l'altra e l'errore arriva a meta' raccolta.
