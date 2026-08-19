#!/usr/bin/env bash
# Quello che va fatto quando le due raccolte chiudono, in un comando solo e in ordine.
#
# Non e' una comodita': e' che fra trenta ore la sequenza giusta non sara' ovvia, e il modo in
# cui si sbaglia e' saltare un controllo perche' «tanto quello passa». Ogni passo qui sotto
# esce diverso da zero se non passa, e lo script si ferma li'.
#
# NON esegue niente che spenda. Legge, verifica, genera, compila.
set -euo pipefail

cd "$(dirname "$0")"
passo() { printf '\n=== %s\n' "$1"; }

passo "1. le raccolte sono complete?"
# Completa = OGNI cella ha RUNS run valide per OGNI binario, non un totale di righe che
# raggiunge una soglia. La prima versione di questo passo contava le righe grezze e dava
# «ablazione 150%», che e' vero e non significa niente: la cella haiku e' doppia (NOTA-02) e
# una cella vuota accanto a una doppia supererebbe comunque la soglia.
python3 - <<'PY'
import sys
sys.path.insert(0, "src")
import completa_celle as cc
MODELLI = ("gpt-oss-120b", "llama-3.3-70b", "claude-haiku-4-5", "claude-sonnet-4-5")
bracci = {
    "ri-raccolta": ("riraccolta", [(m, i, t) for m in MODELLI
                                   for i in ("databricks", "bedrock")
                                   for t in ("native", "text")]),
    "ablazione": ("ablazione", [(m, "databricks", "native")
                                for m in ("claude-haiku-4-5", "claude-sonnet-4-5")]),
}
manca = False
for eti, (braccio, celle) in bracci.items():
    carenti = {c: len(cc.deficit(*c, braccio=braccio)[1]) for c in celle}
    tot = sum(carenti.values())
    incomplete = sum(1 for v in carenti.values() if v)
    print(f"  {eti:<12} {len(celle) - incomplete}/{len(celle)} celle complete, "
          f"{tot} binari carenti")
    if tot:
        manca = True
# UNA eccezione, e solo perche' e' documentata e non recuperabile: prog39_horner su
# gpt-oss/bedrock/native resta a sette run valide su otto perche' l'endpoint rifiuta il nome
# di tool che il modello stesso produce (NOTA-03, settimo meccanismo). La catena dei suffissi
# di quella cella e' esaurita e riprovare significherebbe scegliere quante volte riprovare
# guardando il risultato. Quel binario esce dall'analisi: K=44 per quella cella, dichiarato.
ATTESA = {("gpt-oss-120b", "bedrock", "native"): {"prog39_horner"}}
resid = {}
for eti, (braccio, celle) in bracci.items():
    for c in celle:
        k = set(cc.deficit(*c, braccio=braccio)[1])
        k -= ATTESA.get(c, set()) if braccio == "riraccolta" else set()
        if k:
            resid[c] = sorted(k)
if resid:
    for c, k in resid.items():
        print(f"    {'/'.join(c)}: {len(k)} binari non documentati come eccezione")
    sys.exit("  una raccolta non e' chiusa oltre le eccezioni dichiarate. Un braccio parziale "
             "non si interpreta: i binari si processano in ordine di indice e i primi sono "
             "piu' facili.")
if manca:
    print("  (le sole carenze sono le eccezioni documentate in NOTA-03)")
PY

passo "2. l'isolamento ha tenuto per tutta la raccolta"
python3 analysis/isolamento_riraccolta.py

passo "3. i quattro criteri di EMENDAMENTO-06, dallo script congelato"
python3 analysis/confronto_riraccolta.py

passo "4. criterio 2: la famiglia sulla nuova raccolta"
python3 analysis/analyze_c2.py --results results/riraccolta | tail -20

passo "5. il mordente dell'ablazione, con la banda dichiarata prima"
python3 analysis/mordente_ablazione.py | tail -12

passo "6. la tabella del paper, generata dai dati"
mkdir -p paper/tables
python3 analysis/tabella_riraccolta.py > paper/tables/riraccolta.tex
echo "  scritta in paper/tables/riraccolta.tex — va inclusa in 08-threats.tex, dove sta il TODO"

passo "7. le guardie"
./verifica_hash.sh
python3 analysis/verifica_citazioni.py
python3 ~/onus-v5.2/plugins/onus/scripts/ironrules.py verify

passo "8. la claim sulla ri-raccolta puo' tornare al passato"
python3 analysis/guardia_claim_riraccolta.py

echo "== i numeri del paper appartengono alla base primaria"
# Aggiunto dopo che un lettore ha trovato «5,805 measured trials», il determinismo «98--100% vs
# 13--24%» e le bande «15,6% vs 62,2%» nella Conclusion: tre serie della raccolta precedente in
# una sezione che riassume il paper. Avevo verificato per SEZIONE, e verificare per sezione trova
# i residui delle sezioni che guardi.
python3 analysis/audit_paper.py

cat <<'FINE'

=== Restano tre cose che nessuno script puo' fare al posto tuo:

  a. Sostituire i due TODO(results) — in 00-front.tex e 08-threats.tex — con l'esito dei
     quattro criteri e con \input{tables/riraccolta}. Il testo pronto sta in
     registro/EMENDAMENTO-06, ed e' stato scritto prima di vedere i numeri apposta.
  a-bis. Emettere CARD-C2-v8. La v7 dice ancora, alla riga 296, che il confondimento fra
     trasporto e batching e' «non delimitato»: il braccio di ablazione lo ha delimitato il
     16/08 (+0,8pp haiku, +1,6pp sonnet, `analysis/effetto_batching.py`). La v8 si emette
     con i numeri dell'ablazione E della ri-raccolta insieme, non due volte.
  b. Decidere se i numeri principali del paper restano quelli della raccolta originale o
     passano alla nuova. EMENDAMENTO-06 dice che la PRIMARIA e' la nuova, deciso prima:
     se ora sembrasse comodo il contrario, e' il momento in cui quella decisione serve.
  c. Ricompilare e rileggere.
FINE
