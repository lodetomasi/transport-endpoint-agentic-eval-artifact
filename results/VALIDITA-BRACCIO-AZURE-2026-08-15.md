# Il braccio esplorativo Azure non ha dati validi

**Annotazione di validità del 2026-08-15.** Va letta insieme a `results/README-validita.md`,
che non ha potuto ospitarla: IR-5 rende `results/` append-only e la guardia rifiuta la modifica
in place di quel file. La regola stessa prescrive «un file nuovo più una nota», ed è questo.

## Il fatto

`results/esplorativo/c2x_gpt-oss-120b_azure_native.csv` — **238 righe** — faceva parte del lotto
invalidato per i tre canali del nome dell'algoritmo (`registro/EMENDAMENTO-03`) ed è oggi in
`results/invalidati/lotto-nome-algoritmo/`.

A differenza delle 16 celle confermative, **non è stato riraccolto**. `results/esplorativo/`
contiene oggi **zero righe di misurazione**: solo gli otto JSON del replay del materiale, che
sono derivati dalle celle confermative e non da Azure.

## Perché va scritto invece che lasciato dedurre

`registro/EMENDAMENTO-02-braccio-azure.md` istituisce un braccio esplorativo su un terzo cloud, e
`README.md` lo annuncia al lettore. **Quel braccio non ha dati validi.** Ogni frase che lo
presenta come raccolto è falsa finché non viene rifatto, e un revisore che apre
`results/esplorativo/` trova otto JSON e nessuna misurazione.

## Cosa non tocca

- **La famiglia dei dieci test**: `m` resta 10. L'esplorativo non vi entrava per costruzione, ed
  è la ragione per cui l'emendamento 02 lo teneva in una directory separata con prefisso `c2x_`
  — perché l'analisi congelata non lo vedesse.
- **Il sesto meccanismo di cancellazione** (chiamate parallele, `400 UnsupportedToolUse`). La sua
  evidenza è la **sonda in tre passi** del 2026-08-14 sull'endpoint — turno con un tool passa,
  turno con una chiamata in storia passa, storia con due chiamate nello stesso messaggio viene
  rifiutata — non le run di questa cella. Regge senza di esse.
- **Il costo**: zero righe significa zero dollari da attribuire ad Azure nel bilancio corrente.

## Una guardia che contava meno di quanto dichiarava

Trovato dal revisore di riproducibilità del gauntlet il 2026-08-15, e verificato qui.

| file | cosa somma |
|---|---|
| `check_cost.sh:20` | `results/c2_*.csv` **e** `results/esplorativo/*.csv`, col commento «il tetto copre tutto ciò che si paga, braccio esplorativo incluso» |
| `sorveglia_costi.sh:41`, la funzione che **uccide i processi** | **solo** `results/c2_*.csv` |

Il referto e l'esecutore contavano cose diverse: il tetto dichiarato valeva per il primo e non
per il secondo. **Non ha morso** — verificato oggi: l'esplorativo ha zero righe e zero dollari,
quindi il sorvegliante avrebbe ucciso alla stessa soglia. Ma «non ha morso» non è «era
protetto», e la distanza fra le due è tutta nel fatto che il braccio esplorativo sia stato
invalidato per un'altra ragione.

La correzione di `sorveglia_costi.sh` è presa in carico dalla sessione che tiene le guardie.
