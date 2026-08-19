#!/usr/bin/env bash
# Stato della raccolta, e SORVEGLIA IL SORVEGLIANTE.
#
# `sorveglia_costi.sh` scrive un battito a ogni giro. Qui si confronta col proprio orologio:
# un guardiano che si spegne in silenzio e' peggio di nessun guardiano, perche' per ore si
# crede di avere una protezione che non esiste.
set -o pipefail
cd "$(dirname "$0")"

TETTO="${C2_TETTO_USD:-150}"
INTERVALLO="${C2_INTERVALLO:-60}"
BATTITO=".sorveglianza/battito"

echo "=== spesa ==="
./check_cost.sh
ESITO=$?

echo
echo "=== celle ==="
python3 - <<'PY'
import sys
sys.path.insert(0, "src")
# Somma la CATENA dei suffissi, non i file: c2_x.csv e c2_x_redo.csv sono la stessa cella, e
# mostrarli separati fa leggere "0/16 chiuse" a una cella che sta a 352/360. Un pannello che
# sotto-riporta il progresso e' l'immagine speculare di uno che lo sovra-riporta, e sbaglia
# nella direzione in cui si ricomincia un lavoro gia' fatto.
from completa_celle import deficit, RUNS
from raccogli_c2 import celle
ATTESI = RUNS * 45
chiuse = iniziate = 0
for eti, infra, tr in celle():
    n, manca = deficit(eti, infra, tr)
    tot = sum(n.values())
    if tot:
        iniziate += 1
    if not manca:
        chiuse += 1
        stato = "CHIUSA"
    elif tot == 0:
        stato = "-"
    else:
        stato = f"{100 * tot // ATTESI}%  ({len(manca)} binari carenti)"
    print(f"  {eti}/{infra}/{tr:7s} {tot:4d}/{ATTESI}  {stato}")
print(f"\n  {chiuse}/16 celle chiuse, {iniziate} iniziate")
PY

echo
echo "=== processi, contati per PID ==="
# pgrep -c stampa 0 ED ESCE 1: si conta con wc, non col suo codice di uscita.
D=$(pgrep -f "$(pwd)/src/raccogli_c2.py" 2>/dev/null | wc -l | tr -d ' ')
W=$(pgrep -f "$(pwd)/src/run_minipilot.py" 2>/dev/null | wc -l | tr -d ' ')
S=$(pgrep -f "$(pwd)/sorveglia_costi.sh" 2>/dev/null | wc -l | tr -d ' ')
echo "  driver $D · worker $W · sorvegliante $S"

echo
echo "=== il sorvegliante e' VIVO o solo AVVIATO? ==="
if [ ! -f "$BATTITO" ]; then
  echo "  NESSUN BATTITO: la sorveglianza non e' mai partita."
  exit 3
fi
ORA=$(date '+%s')
ULTIMO=$(cat "$BATTITO")
ETA=$((ORA - ULTIMO))
LIMITE=$((INTERVALLO * 3))
if [ "$ETA" -le "$LIMITE" ]; then
  echo "  battito di ${ETA}s fa (limite ${LIMITE}s): VIVO"
else
  echo "  battito di ${ETA}s fa, oltre il limite di ${LIMITE}s: MORTO O BLOCCATO."
  echo "  Per ore si e' creduto di avere una protezione di budget che non esisteva."
  exit 3
fi

exit $ESITO
