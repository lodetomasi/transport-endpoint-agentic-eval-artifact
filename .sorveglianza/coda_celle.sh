#!/usr/bin/env bash
# Le 12 celle quasi chiuse di UN cloud, in sequenza. Sta in un FILE e non in un `bash -c`
# inline perche' la cmdline di un bash -c contiene il percorso del driver e si auto-cattura
# nel pgrep del sorvegliante: il guardiano conterebbe vivo un wrapper che driver non e'.
set -o pipefail
RADICE="$(cd "$(dirname "$0")/.." && pwd)"
INFRA="$1"
for m in gpt-oss-120b llama-3.3-70b claude-haiku-4-5; do
  for t in native text; do
    python3 "$RADICE/src/raccogli_c2.py" --cella "$m/$INFRA/$t"
  done
done
