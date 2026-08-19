#!/usr/bin/env bash
# Sorveglianza della spesa di C2. FERMA la raccolta al tetto, non la commenta.
#
# Tre lezioni di C1, e la prima e' costata ore di falsa protezione:
#
# 1. NON IDENTIFICARE L'ORCHESTRATORE PER NOME. `cost_watchdog.sh` sondava la liveness
#    cercando `run_confirmatory.sh`, che non era piu' l'orchestratore: concludeva
#    "esperimento concluso" e usciva subito, ogni volta. Qui il segnale di vita e' la
#    CRESCITA dei CSV, che non invecchia con i nomi degli script.
#
# 2. PRETENDI CHE LA QUIETE DURI. Fra una cella e l'altra nessun worker e' attivo per un
#    istante: un solo campione avrebbe concluso "terminata" a meta' raccolta. Servono
#    CAMPIONI_QUIETE campioni consecutivi senza crescita E senza driver vivo.
#
# 3. UN TETTO CHE ESCE 2, NON CHE PROSEGUE. IR-6: il budget non si alza a meta' corsa.
#
# E la guardia va guardata: ogni giro scrive un battito in .sorveglianza/battito, che
# `stato.sh` confronta con l'orologio. Un guardiano che si spegne in silenzio e' peggio di
# nessun guardiano.
set -o pipefail
cd "$(dirname "$0")"

TETTO="${C2_TETTO_USD:-200}"
INTERVALLO="${C2_INTERVALLO:-60}"
CAMPIONI_QUIETE="${C2_CAMPIONI_QUIETE:-5}"
BATTITO=".sorveglianza/battito"
DIARIO=".sorveglianza/diario.log"
mkdir -p .sorveglianza

# I processi si identificano col PERCORSO ASSOLUTO, non col nome del file. Un pattern come
# "raccogli_c2.py" cerca su TUTTA la macchina: durante un collaudo in una cartella
# temporanea ha ucciso la raccolta vera di un altro albero. E' l'autocattura di `ps | grep`
# applicata al kill, e la vittima non e' il grep ma l'esperimento.
RADICE="$(pwd)"
MIO_DRIVER="$(pwd)/src/raccogli_c2.py"
MIO_WORKER="$(pwd)/src/run_minipilot.py"

spesa() {
  # UNA SOLA definizione, in analysis/spesa_totale.py, ricorsiva su tutto results/.
  # Prima erano due copie per enumerazione di cartelle, in questo file e in check_cost.sh.
  # L'enumerazione ha ceduto due volte: la prima con results/esplorativo/ (senza morso,
  # perche' era vuota), la seconda con results/ablazione/ — $22,47 spesi e invisibili al
  # tetto, mentre il diario scriveva «nessuna crescita, cella lenta o bloccata» a raccolta
  # viva. Il tetto protegge un conto, non una cartella: ogni cartella futura e' coperta per
  # costruzione. Il test nei due sensi: python3 analysis/spesa_totale.py --autotest
  python3 "$RADICE/analysis/spesa_totale.py" --radice "$RADICE/results"
}

# Byte totali dei CSV: cresce a ogni run scritta. Non dipende da come si chiama lo script
# che li scrive, che e' il punto.
impronta() {
  python3 "$RADICE/analysis/spesa_totale.py" --radice "$RADICE/results" --impronta
}

# Conta per PID. `ps | grep <pattern>` si autocattura quando il pattern sta nella propria
# riga di comando, e `pgrep -c` stampa 0 ED ESCE 1.
# Il driver si trova per NOME e si filtra per DIRECTORY DI LAVORO, non per percorso assoluto
# nella riga di comando. La versione precedente cercava `pgrep -f "$(pwd)/src/raccogli_c2.py"`
# e non vedeva un driver lanciato come `python3 src/raccogli_c2.py` — percorso relativo, stesso
# albero, stesso processo. Il 2026-08-15 la sorveglianza ha contato zero driver per venti
# minuti mentre l'ablazione raccoglieva, ha concluso «raccolta terminata» ed e' uscita,
# lasciando la spesa senza guardia.
#
# L'invariante per cui il percorso assoluto esisteva resta intatto: un driver di un altro
# albero ha un'altra cwd e non viene contato, quindi non viene mai ucciso. Si controlla
# dove il processo LAVORA invece di come e' stato scritto il suo comando.
#
# UNA SOLA REGOLA, usata dal rilevamento E dal kill. Il 2026-08-15 la correzione ha
# insegnato a `pid_vivi` a cercare per nome + cwd, ma ha lasciato i due cicli di kill su
# `pgrep -f "$MIO_DRIVER"`, cioe' sul percorso assoluto. Misurato subito dopo: 1 driver
# rilevato, 0 uccidibili. Al tetto la guardia avrebbe ucciso il worker, il driver avrebbe
# aperto la cella successiva, e il sorvegliante era gia' uscito con exit 2 -- una guardia che
# dichiara di aver fermato la spesa e non l'ha fermata. Due definizioni della stessa cosa in
# due punti divergono, e la divergenza non fa rumore: e' lo stesso motivo per cui la regola
# di misurazione delle run e' una sola e condivisa.
pid_nostri() {
  local pid cwd
  for pid in $(pgrep -f "src/$1" 2>/dev/null); do
    cwd=$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | grep '^n' | cut -c2-)
    [ "$cwd" = "$RADICE" ] && printf '%s\n' "$pid"
  done
}

pid_vivi() {
  pid_nostri raccogli_c2.py | awk 'END{print NR+0}'
}

nota() {
  echo "$(date '+%Y-%m-%dT%H:%M:%S')  $*" | tee -a "$DIARIO"
}

nota "avvio: tetto \$$TETTO, campione ogni ${INTERVALLO}s, quiete a $CAMPIONI_QUIETE campioni"
PRECEDENTE=$(impronta)
QUIETI=0
AVVISATO_80=0

while true; do
  date '+%s' > "$BATTITO"
  S=$(spesa)
  I=$(impronta)
  V=$(pid_vivi)

  # --- il tetto, e non e' un avviso -------------------------------------------------
  if python3 -c "import sys; sys.exit(0 if float('$S') >= float('$TETTO') else 1)"; then
    nota "TETTO SUPERATO: \$$S di \$$TETTO — fermo la raccolta"
    # Stessa identificazione del rilevamento, non una seconda definizione.
    for p in $(pid_nostri raccogli_c2.py); do
      nota "  kill $p (driver)"
      kill "$p"
    done
    for p in $(pid_nostri run_minipilot.py); do
      nota "  kill $p (worker)"
      kill "$p"
    done
    # Si verifica che siano morti, invece di dichiararlo: un kill che non ha effetto e una
    # guardia che non e' scattata producono lo stesso diario.
    sleep 2
    RESTA=$(( $(pid_nostri raccogli_c2.py | awk 'END{print NR+0}') \
            + $(pid_nostri run_minipilot.py | awk 'END{print NR+0}') ))
    nota "  dopo il kill restano $RESTA processi nostri"
    nota "IR-6: il budget non si alza a meta' corsa. Fermata."
    exit 2
  fi

  if [ "$AVVISATO_80" -eq 0 ] && \
     python3 -c "import sys; sys.exit(0 if float('$S') >= 0.8*float('$TETTO') else 1)"; then
    nota "ATTENZIONE: \$$S, cioe' l'80% del tetto"
    AVVISATO_80=1
  fi

  # --- la quiete deve durare, e il driver deve essere sparito -----------------------
  if [ "$I" = "$PRECEDENTE" ] && [ "$V" -eq 0 ]; then
    QUIETI=$((QUIETI + 1))
    nota "quiete $QUIETI/$CAMPIONI_QUIETE (nessuna crescita, nessun driver) — \$$S"
    if [ "$QUIETI" -ge "$CAMPIONI_QUIETE" ]; then
      nota "raccolta terminata. Spesa finale \$$S di \$$TETTO"
      exit 0
    fi
  elif [ "$I" = "$PRECEDENTE" ] && [ "$V" -gt 0 ]; then
    # Driver vivo ma i file non crescono: non e' finita, e' ferma. Si segnala e si continua,
    # perche' una cella lenta e una cella bloccata si distinguono solo col tempo.
    QUIETI=0
    nota "driver vivo ma nessuna crescita — \$$S (cella lenta o bloccata)"
  else
    QUIETI=0
  fi

  PRECEDENTE="$I"
  sleep "$INTERVALLO"
done
