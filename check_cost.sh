#!/usr/bin/env bash
# Spesa e run di C2, dai CSV delle celle. Conta per RIGA valida, non per file.
#
# Somma il costo anche sulle righe che non sono misurazioni: quelle si pagano lo stesso, e un
# conto che le ignora sottostima la spesa proprio nei bracci che vanno male, cioe' dove il
# tetto serve. In C1 un `awk` con la posizione di campo sbagliata riporto' 0,00 EUR su 2.101
# run gia' pagate: un numero implausibile si autodenuncia, uno plausibile no.
set -o pipefail
cd "$(dirname "$0")"
python3 - <<'PY'
import csv, glob, os, sys
sys.path.insert(0, "src")
from qualita_run import e_misurazione

TETTO = float(os.environ.get("C2_TETTO_USD", "200"))   # budget dichiarato di C2, IR-6
tot, n, non_mis = 0.0, 0, 0
per_cella = {}
# Il tetto copre tutto cio' che si paga: un budget che guarda solo il confermativo non e'
# un budget. L'elenco delle cartelle non si scrive qui — sta in analysis/spesa_totale.py,
# che e' ricorsivo, ed e' la stessa fonte che usa il sorvegliante. Due definizioni della
# stessa quantita' sono gia' divergute due volte in questo repository.
sys.path.insert(0, "analysis")
from spesa_totale import csv_di_spesa  # noqa: E402

for f in csv_di_spesa("results"):
    with open(f, errors="ignore") as fh:
        for r in csv.DictReader(fh):
            try:
                c = float(r.get("cost_usd") or 0)
            except ValueError:
                c = 0.0
            tot += c
            if e_misurazione(r):
                n += 1
            else:
                non_mis += 1
            k = (r.get("modello", ""), r.get("infra", ""), r.get("trasporto", ""))
            e = per_cella.setdefault(k, [0, 0.0])
            e[0] += 1
            e[1] += c

print(f"  {n} misurazioni + {non_mis} righe non-misurazione, ${tot:.2f} di ${TETTO:.2f}")
if per_cella:
    print()
    for k, (c, u) in sorted(per_cella.items()):
        print(f"    {'/'.join(k):48s} {c:5d} righe  ${u:7.4f}")
if tot >= TETTO:
    print(f"\n  TETTO SUPERATO. IR-6: il budget non si alza a meta' corsa.")
    sys.exit(2)
if tot >= TETTO * 0.8:
    print(f"\n  {tot / TETTO:.0%} del tetto.")
PY
