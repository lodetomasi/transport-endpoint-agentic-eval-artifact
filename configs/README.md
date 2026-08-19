# `configs/`

`pricing.json` — una voce per `provider:modello`, ciascuna con la **fonte per esteso**. La
guardia rifiuta un modello senza voce **prima** della chiamata: fino al 2026-08-13 il controllo
stava dopo, e un modello senza tariffa veniva fatturato per una chiamata e poi respinto —
misurato a 4,51 s contro 0,00 s. Le stime sono marcate `is_estimate: true` e dicono perche'.

I meter on-demand puri vanno disambiguati dalle varianti `-batch` (meta' prezzo), `-flex` e
`-priority`: prendere il numero sbagliato e' un errore di 2x che nessun controllo a valle
segnalerebbe.

`binari_holdout.txt` — i 45 binari congelati **per nome**, con lo sha256 dell'elenco. «I primi
45» non e' una specifica: e' un ordinamento, e cambia se cambia il filesystem.

## Leggere la fattura, e le due trappole che ci sono dentro

La contabilità dai CSV usa le tariffe **dichiarate**; la spesa vera è quella che fatturano i
cloud. Riconciliare non è pignoleria: è l'unico modo di sapere se una tariffa dichiarata è
quella applicata.

**Databricks** — `system.billing.usage` join `system.billing.list_prices`, con
`usage_metadata.endpoint_name` per attribuire per modello. Serve un SQL warehouse: il più
economico è un X-Small serverless con autostop breve, circa dieci centesimi per due query, e si
ferma a mano senza aspettare l'autostop.

Riconciliazione del 2026-08-14 su `gpt-oss-120b`: **$4,1272 dai CSV contro $4,1287 in
fattura, scarto 0,04%**.

**Bedrock** — due trappole, e la seconda produce un «costo zero» che sembra vero.

1. **Il ritardo.** Cost Explorer emette i dati con molte ore di ritardo: il 14 agosto alle
   15:20 UTC copriva fino alle ~04:00, mentre le run erano cominciate alle 06:59. Zero righe in
   fattura non significa zero spesa — significa che il dato non esiste ancora. Il controllo che
   distingue i due casi è confrontare il totale del giorno parziale con la media dei giorni
   pieni.

2. **I modelli Anthropic NON fatturano sotto `Amazon Bedrock`.** Hanno servizi propri:
   `Claude Sonnet 4.5 (Amazon Bedrock Edition)`, `Claude Opus 4.5 (…)`,
   `Claude Haiku 4.5 (…)`. Un filtro `SERVICE = "Amazon Bedrock"` li **manca tutti**. In questo
   studio Haiku e Sonnet sono $104 dei $125 previsti, metà dei quali su Bedrock: quel filtro
   avrebbe mostrato quasi zero.

```bash
aws ce get-cost-and-usage --time-period Start=<da> End=<a> --granularity DAILY \
  --metrics UnblendedCost --group-by Type=DIMENSION,Key=SERVICE
# poi si filtra sui nomi che contengono "edrock", non su un nome solo
```

Il profilo di raccolta non ha `ce:GetCostAndUsage`: serve il profilo amministrativo dello
stesso account, e il suo token SSO scade.
