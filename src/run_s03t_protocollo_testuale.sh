#!/usr/bin/env bash
# Studio 03, braccio secondario dichiarato: le chiamate ai tool viaggiano nel TESTO.
# Vedi PREREGISTRATION-STUDIO-03-EMENDAMENTO-03.md. Non entra in Holm.
#
# Gira su tutti e quattro i modelli, non solo su quello che ne ha bisogno: i tre che
# supportano il protocollo nativo diventano cosi' misurati due volte, e la differenza fra
# protocolli e' un numero osservato invece di un'assunzione.
set -u
cd "$(dirname "$0")"
HELD='prog(1[6-9]|[2-5][0-9]|60)_'
run() {  # <modello> <tag> <tetto>
  echo "[$(date -u +%H:%M:%S)] $2 (tetto $3)"
  python3 -u run_minipilot.py --runs 8 --turns 12 --model "$1" --only "$HELD" \
    --decomp decomp_stripped --tool-protocol text --max-tokens "$3" \
    --out "results/s03t_${2}_N12.csv" > "/tmp/s03t_${2}.log" 2>&1
  echo "[$(date -u +%H:%M:%S)] $2 fatto"
}
case "${1:-tutti}" in
  gemma)  run databricks-gemma-3-12b                       gemma12b     8192 ;;
  altri)  run databricks-meta-llama-3-3-70b-instruct        llama3370b   8192
          run databricks-claude-haiku-4-5                   haiku45      8192 ;;
  llama)  run databricks-meta-llama-3-3-70b-instruct        llama3370b   8192 ;;
  haiku)  run databricks-claude-haiku-4-5                   haiku45      8192 ;;
  gptoss) run databricks-gpt-oss-20b                        gptoss20b   24576 ;;
esac
echo "[$(date -u +%H:%M:%S)] COMPLETO ${1:-tutti}"
