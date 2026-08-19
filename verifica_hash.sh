#!/usr/bin/env bash
# Verifica che i file congelati non siano cambiati senza un documento di successione.
#
# Sesto controllo: gli altri verificano coerenza fra pipeline, non integrita' di un hash. Un
# hash dichiarato e mai riverificato e' documentazione, non protezione.
#
# I documenti stanno in registro/. Spostarli senza toccare questa riga renderebbe la
# guardia cieca a OGNI successione: ogni divergenza diventerebbe muta, cioe' la guardia
# si irrigidisce invece di allentarsi -- il verso meno pericoloso, ma comunque rotto.
#
# La prima versione accettava la presenza di UN qualunque SUCCESSIONE-*.md come prova che
# qualunque divergenza fosse documentata: un documento scritto per un file avrebbe coperto in
# silenzio la modifica di un altro. Ora il documento deve NOMINARE il file divergente.
set -o pipefail
cd "$(dirname "$0")"
DIVERGENZE=0
CONTROLLATI=0

while IFS='|' read -r _ f h _; do
  f=$(echo "$f" | tr -d ' `')
  h=$(echo "$h" | tr -d ' `')
  if [ -z "$f" ] || [ "$f" = "file" ]; then
    continue
  fi
  CONTROLLATI=$((CONTROLLATI + 1))
  if [ ! -f "$f" ]; then
    echo "  MANCA   $f"
    DIVERGENZE=$((DIVERGENZE + 1))
    continue
  fi
  a=$(shasum -a 256 "$f" | awk '{print $1}')
  if [ "$a" = "$h" ]; then
    echo "  ok      $f"
    continue
  fi
  echo "  DIVERGE $f"
  echo "          dichiarato $h"
  echo "          effettivo  $a"
  # Il documento deve nominare QUESTO file E dichiarare l'hash EFFETTIVO.
  #
  # Nominarlo soltanto non bastava, e il modo in cui non bastava e' quello che rassicura:
  # una successione qualunque nel passato del file copriva in silenzio ogni modifica
  # seguente, perche' la guardia rispondeva a "questo file ha mai avuto una successione?"
  # invece che a "QUESTA modifica e' documentata?". Il 2026-08-14 `src/raccogli_c2.py' e'
  # cambiato dopo la successione 04 e la guardia ha stampato zero divergenze, trovando per
  # nome la successione 01. Pretendere l'hash effettivo chiude il buco per costruzione: una
  # modifica non documentata lascia sul disco un valore che nessun documento contiene.
  SUCC=""
  for cand in $(grep -l -- "$f" registro/SUCCESSIONE-*.md 2>/dev/null); do
    if grep -q -- "$a" "$cand"; then SUCC="$cand"; break; fi
  done
  if [ -n "$SUCC" ]; then
    echo "          successione documentata in $SUCC (nomina il file e dichiara $a)"
  else
    NOMINANO=$(grep -l -- "$f" registro/SUCCESSIONE-*.md 2>/dev/null | tr '\n' ' ')
    if [ -n "$NOMINANO" ]; then
      echo "          successioni che NOMINANO $f: $NOMINANO"
      echo "          ma NESSUNA dichiara l'hash effettivo $a: e' una divergenza muta"
    else
      echo "          NESSUNA successione nomina $f: e' una divergenza muta"
    fi
    DIVERGENZE=$((DIVERGENZE + 1))
  fi
done < <(awk -F'|' '/^\| `/{print}' HASH-CONGELATI.md)

echo "  $CONTROLLATI file controllati, $DIVERGENZE divergenza/e non documentata/e"
[ "$DIVERGENZE" -eq 0 ]
