#!/usr/bin/env bash
# Le tre guardie della revisione, in un comando. Esce non-zero alla prima che fallisce.
# Compila con tectonic e pretende ZERO overfull, ZERO underfull, ZERO riferimenti irrisolti:
# un PDF che compila non e' un PDF corretto, e la differenza si vede solo contando.
set -o pipefail
cd "$(dirname "$0")/.."
esito=0
for c in "revisione/compila.sh" \
         "python3 revisione/controlla_latex.py --autotest" \
         "python3 revisione/controlla_latex.py" \
         "python3 analysis/audit_paper.py" \
         "python3 revisione/modifiche_dichiarate.py" \
         "python3 revisione/autosabotaggio.py --autotest" \
         "python3 revisione/conta_soglie.py" \
         "python3 revisione/verifica_numerica.py --tsv revisione/numeric_verification.tsv" \
         "python3 analysis/saturazione_turni.py --braccio riraccolta" \
         "python3 analysis/runtime_t6.py" \
         "python3 analysis/contesto_t6.py" \
         "python3 analysis/conteggio_m8.py" \
         "python3 analysis/saturazione_turni.py --braccio ablazione" \
         "python3 revisione/stato_a_cutoff.py"; do
    if $c > /dev/null 2>&1; then
        printf '  ok       %s\n' "$c"
    else
        printf '  FALLITO  %s\n' "$c"
        esito=1
    fi
done
exit $esito
