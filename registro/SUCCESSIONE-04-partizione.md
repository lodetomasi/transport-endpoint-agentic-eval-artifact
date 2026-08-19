# Successione 04 — partizione per infrastruttura in `src/raccogli_c2.py`

**Data**: 2026-08-14, scritto **prima** della modifica.

## Il file

`src/raccogli_c2.py`

## Cosa cambia

Un'opzione `--solo-infra {databricks,bedrock}` che restringe il driver alle celle di
un'infrastruttura. Nient'altro.

Serve a farne girare **due in parallelo**, uno per cloud.

## Perché

Il driver esegue le celle in sequenza secondo l'ordine di `ROSTER`, che alterna i due cloud.
A ogni istante quindi **un'infrastruttura lavora e l'altra è ferma**. Al ritmo misurato — 1,8
run/min su finestre di 30 e 120 minuti — le 4.395 run rimanenti sono circa 40 ore.

Partizionando, il tempo si dimezza a ~22 ore.

**Il carico per endpoint non aumenta.** Adesso Databricks riceve una cella alla volta e Bedrock
zero, poi si invertono. Dopo, ciascuno riceve una cella alla volta, sempre. Non è premere di
più su un'infrastruttura di terzi: è smettere di tenerne metà spenta.

## Effetto isolato sulla misura

**Nessuno.** La partizione non tocca:

- il roster dei quattro modelli, né gli id per endpoint;
- l'elenco congelato dei 45 binari, né il suo hash;
- run per cella (8), turni (12), temperatura (0,0), tetto di token (8.192);
- la regola di qualità, né la catena dei suffissi di ripresa.

Ogni cella riceve esattamente il comando che avrebbe ricevuto in sequenza. Cambia **chi** lo
lancia e **quando**, non **cosa**.

Una cosa che cambia e va detta: le celle non arrivano più nell'ordine di `ROSTER`. Non importa
per l'analisi, che è appaiata per binario e legge i CSV per nome, ma un log letto in ordine
cronologico non è più l'ordine del roster.

## Il rischio, e perché è delimitato

Due worker concorrenti sullo stesso endpoint non ci sono mai — è il punto della partizione. Il
rischio residuo è che i due cloud abbiano una risorsa condivisa a valle che non conosco: se
succedesse, si vedrebbe come `infra_failure` sulle righe, che la regola di qualità esclude
dalle misurazioni e che la ripresa per deficit ricolma.

## Come si ferma il driver in corso

La cella a metà **resta sul disco** — `results/` è append-only — e viene completata dalla
ripresa sui soli binari carenti, col suffisso successivo della catena. È il meccanismo della
successione 02, già provato: cella a 358/360 → 2 binari carenti → `_redo` → chiusa a 360.

Nessuna run raccolta viene persa.

## Sorveglianza

`sorveglia_costi.sh` identifica i processi col percorso assoluto e uccide **tutti** i PID che
corrispondono: due driver invece di uno non cambiano il suo comportamento al tetto.

La condizione di quiete richiede zero driver vivi per 5 campioni consecutivi, quindi con due
driver conclude «terminata» solo quando **entrambi** sono spariti — che è il comportamento
voluto.
