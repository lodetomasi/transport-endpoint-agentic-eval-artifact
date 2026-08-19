#!/usr/bin/env bash
# Rimette in piedi un driver che e' morto, e NON lo rimette in piedi se e' stato ucciso dal
# tetto. La differenza fra le due cose e' l'intero valore di questo file.
#
# PERCHE' ESISTE. Il driver dell'ablazione e' morto il 2026-08-15 senza lasciare traccia, e me
# ne sono accorto per caso ore dopo, con il braccio fermo al 50% e una cella mai iniziata. Le
# raccolte in corso hanno davanti circa trenta ore: la stessa cosa succedera' di nuovo.
#
# PERCHE' NON E' UN MODO DI AGGIRARE IL TETTO. `sorveglia_costi.sh` uccide i driver quando la
# spesa supera C2_TETTO_USD ed esce 2. Un rilanciatore che non lo sapesse li riavvierebbe subito
# dopo, e la protezione della spesa smetterebbe di esistere restando in piedi solo per finta.
# Quindi qui, prima di ogni riavvio:
#   - se la spesa e' oltre il tetto, NON si riavvia e si esce 2, come la sorveglianza;
#   - se la sorveglianza non e' viva, NON si riavvia: un driver senza guardia non riparte;
#   - se la cella risulta gia' completa, non c'e' niente da riavviare.
#
#   ./riprendi_se_muore.sh            # controlla ogni 5 minuti
#   ./riprendi_se_muore.sh 60         # ogni minuto, per collaudarlo
set -uo pipefail
cd "$(dirname "$0")"

INTERVALLO="${1:-300}"
TETTO="${C2_TETTO_USD:-360}"
DIARIO=".sorveglianza/riavvii.log"
nota() { printf '%s  %s\n' "$(date '+%Y-%m-%dT%H:%M:%S')" "$1" | tee -a "$DIARIO"; }

# Il pattern deve identificare LA partizione, non il braccio: con due driver
# `--riraccolta --solo-infra databricks` e `... bedrock`, cercare "raccogli_c2.py --riraccolta"
# li trova entrambi, e se ne muore uno l'altro lo copre. Il supervisore direbbe «tutto vivo»
# mentre meta' della griglia e' ferma.
vivo() { pgrep -f "raccogli_c2\.py $1\$" >/dev/null 2>&1; }

# $1 = braccio, $2 = infrastruttura (vuoto = tutte). Esce 0 se non manca nulla NELLA
# PARTIZIONE, non nel braccio: adattando questo file alle partizioni avevo corretto `vivo`
# e non questa funzione, e il supervisore ha riavviato la partizione databricks 52 volte a
# vuoto — le sue otto celle erano chiuse ma il braccio no, perche' mancava bedrock. Ogni
# riavvio pagava un preflight e sporcava il diario, che e' il modo in cui un riavvio vero
# diventa invisibile.
completa() {
  python3 - "$1" "${2:-}" <<'PY'
import sys
sys.path.insert(0, "src")
import completa_celle as cc
braccio = sys.argv[1]
infra = sys.argv[2] if len(sys.argv) > 2 else ""
celle = ([(m, i, t) for m in ("gpt-oss-120b", "llama-3.3-70b", "claude-haiku-4-5",
                              "claude-sonnet-4-5")
          for i in ("databricks", "bedrock") for t in ("native", "text")]
         if braccio == "riraccolta" else
         [(m, "databricks", "native") for m in ("claude-haiku-4-5", "claude-sonnet-4-5")])
if infra:
    celle = [c for c in celle if c[1] == infra]
manca = sum(len(cc.deficit(*c, braccio=braccio)[1]) for c in celle)
sys.exit(0 if manca == 0 else 1)
PY
}

nota "avvio: controllo ogni ${INTERVALLO}s, tetto \$$TETTO"

while true; do
  SPESA=$(python3 analysis/spesa_totale.py)

  if python3 -c "import sys; sys.exit(0 if float('$SPESA') >= float('$TETTO') else 1)"; then
    nota "spesa \$$SPESA oltre il tetto \$$TETTO: NON riavvio nulla. Il tetto non si aggira."
    exit 2
  fi

  if ! pgrep -f sorveglia_costi >/dev/null 2>&1; then
    nota "la sorveglianza non e' viva: non riavvio un driver che nessuno guarda."
    exit 3
  fi

  # Ogni voce e': <etichetta> <braccio> <argomenti esatti del driver>. Gli argomenti sono la
  # chiave con cui si cerca il processo, quindi devono coincidere con come viene lanciato.
  # <etichetta> <braccio> <infrastruttura o -> <argomenti esatti del driver>
  ATTESI=(
    "riraccolta-db  riraccolta  databricks  --riraccolta --solo-infra databricks"
    "riraccolta-bd  riraccolta  bedrock     --riraccolta --solo-infra bedrock"
    "ablazione      ablazione   -           --ablazione"
  )

  FATTE=0
  for voce in "${ATTESI[@]}"; do
    read -r ETI BR INFRA ARGS <<<"$voce"
    [ "$INFRA" = "-" ] && INFRA=""
    if completa "$BR" "$INFRA"; then
      FATTE=$((FATTE + 1))
      continue
    fi
    if ! vivo "$ARGS"; then
      nota "$ETI e' fermo e la sua raccolta non e' completa: riparto (spesa \$$SPESA)"
      # shellcheck disable=SC2086
      nohup env AWS_PROFILE=<profilo-bedrock> AWS_REGION=us-east-1 \
        python3 src/raccogli_c2.py $ARGS >> ".sorveglianza/$BR.log" 2>&1 &
      sleep 20
      if vivo "$ARGS"; then
        nota "  $ETI ripartito"
      else
        nota "  $ETI NON e' ripartito: guardare .sorveglianza/$BR.log"
      fi
    fi
  done

  if [ "$FATTE" -eq "${#ATTESI[@]}" ]; then
    nota "entrambe le raccolte sono complete. Eseguire ./chiusura.sh"
    exit 0
  fi

  sleep "$INTERVALLO"
done
