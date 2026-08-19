#!/usr/bin/env bash
# Compila e pretende zero difetti tipografici. Esce non-zero se ne trova.
# Un `tectonic` che ritorna 0 dice solo che il PDF esiste: gli overfull sono warning.
set -o pipefail
cd "$(dirname "$0")/../paper" || exit 1
tectonic -X compile main.tex --keep-logs > /dev/null 2>&1 || { echo "  la compilazione fallisce"; exit 1; }
over=$(awk '/Overfull/{n++} END{print n+0}' main.log)
under=$(awk '/Underfull/{n++} END{print n+0}' main.log)
irr=$(awk '/LaTeX Warning: (Reference|Citation)/{n++} END{print n+0}' main.log)
pag=$(python3 -c "import re;print(re.findall(r'\((\d+) pages',open('main.log',errors='ignore').read())[-1])")
echo "  $pag pagine, overfull=$over underfull=$under irrisolti=$irr"
[ "$over" -eq 0 ] && [ "$under" -eq 0 ] && [ "$irr" -eq 0 ]
