#!/usr/bin/env python3
"""Quante run di C1 hanno DAVVERO chiamato `list_strings`, per braccio.

Esiste perche' il 2026-08-15 questo numero e' stato asserito senza uno script dietro, e
sbagliato: contato con `"list_strings" in open(f).read()`, che pesca anche `tools_offered`
— la lista degli strumenti DISPONIBILI, presente in ogni riga di turno, chiamata o no.
Quel conto restituisce il 100% per costruzione, su qualunque braccio e qualunque modello.

    {"turn": 1, "tools_offered": ["list_functions", "decompile_function", "list_strings",
     "submit_candidate"], "tool_calls": [{"name": "list_functions", ...}], ...}
                ^^^^^^^^^^^^ il grep pescava questo      ^^^^^^^^^^^ mentre il dato e' questo

E' l'errore che il progetto chiama «un numero plausibile e sbagliato non si autodenuncia»,
commesso nel controllo che doveva prevenirlo.

PERCHE' IL NUMERO SERVE. `results/STIMATORI-C1-C2-2026-08-15.txt` confronta la calibrazione
di potenza di C1 con quella osservata in C2, e i due capitoli differiscono anche per
l'apparato: in C2 i tre canali di fuga del nome dell'algoritmo sono chiusi
(`registro/EMENDAMENTO-03`), in C1 no. La domanda e' se in C1 quell'esposizione fosse
SIMMETRICA fra i due trasporti: se lo fosse, non produrrebbe la selezione differenziale che
ha invalidato il primo lotto di C2 (nativo 73% contro testuale 42%).

COME SI CONTA, e conta il come. Si usa la stessa selezione della pipeline confermativa di C1:
le prime 8 run VALIDE per binario, concatenando la catena dei suffissi di ripresa nell'ordine
in cui e' avvenuta. Contare tutti i file `.jsonl` sul disco darebbe un denominatore diverso —
546 invece di 360 sul braccio testuale — perche' includerebbe le run scartate e quelle oltre
l'ottava.
"""
import csv
import glob
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, "src")
from qualita_run import e_misurazione, SUFFISSI_RIESECUZIONE  # noqa: E402

# Il percorso dei dati di C1 e' parametrizzabile: nel deposito anonimizzato il valore di
# default viene riscritto e lo script, senza questa opzione, falliva con ZeroDivisionError
# invece di dire cosa gli mancava. Trovato dal seggio riproducibilita' del gauntlet, che ha
# preparato il deposito e ha provato a rieseguirlo.
_DEFAULT_C1 = "~/<capitolo-precedente>/research/s1-agentic-layer-cost/mini-pilot/results"
C1 = os.path.expanduser(os.environ.get("C2_S1_RESULTS", _DEFAULT_C1))
RUNS = 8
BRACCI = (("nativo", "s03_haiku45_N12"), ("testuale", "s03t_haiku45_N12"))


def prime_valide(base):
    """[(binario, percorso_traiettoria)] per le prime RUNS run valide di ogni binario."""
    per = defaultdict(list)
    for suff in SUFFISSI_RIESECUZIONE:
        csvfile = f"{C1}/{base}{suff}.csv"
        if not os.path.exists(csvfile):
            continue
        with open(csvfile, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                if not e_misurazione(r):
                    continue
                # il file e' <binario>_r<N>.jsonl mentre il CSV porta run_id nudo ("1")
                traj = f"{C1}/trajectories/{base}{suff}/{r['binary_id']}_r{r['run_id']}.jsonl"
                per[r["binary_id"]].append(traj)
    return {b: v[:RUNS] for b, v in per.items() if len(v) >= RUNS}


def chiama(traj):
    """True se una qualunque riga di turno registra una chiamata a list_strings.

    ATTENZIONE se si riusa questo script fuori da haiku-4-5: il confronto e' esatto, e nel
    corpus piu' ampio di C1 esistono nomi di tool inquinati da token di formato — per esempio
    `list_strings<|channel|>commentary` su gpt-oss. Un `==` li manca e restituisce un numero
    piu' basso del vero, in silenzio. Su haiku i nomi sono puliti (verificato: i soli presenti
    sono list_functions, decompile_function, disassemble_function, entry, list_strings,
    submit_candidate), quindi qui il confronto esatto e' corretto; altrove va normalizzato
    prima.
    """
    if not os.path.exists(traj):
        return None
    with open(traj, errors="ignore") as fh:
        for riga in fh:
            try:
                d = json.loads(riga)
            except json.JSONDecodeError:
                continue
            for c in d.get("tool_calls") or []:
                if (c or {}).get("name") == "list_strings":
                    return True
    return False


if __name__ == "__main__":
    if not os.path.isdir(C1):
        raise SystemExit(
            f"i dati di C1 non sono in {C1}.\n"
            "  Questo script legge il repository del capitolo precedente, che non fa parte di\n"
            "  questo deposito. Indica dove sta con:\n"
            "      C2_S1_RESULTS=/percorso/di/mini-pilot/results python3 "
            "analysis/esposizione_list_strings_c1.py\n"
            "  Senza quei dati il numero resta leggibile in\n"
            "  results/ESPOSIZIONE-LIST-STRINGS-C1-2026-08-15.txt, ma non rieseguibile.")
    print("C1, haiku-4-5: run che chiamano DAVVERO list_strings, per braccio")
    print("Selezione: prime 8 run valide per binario, catena dei suffissi — la stessa")
    print("della pipeline confermativa di C1.\n")
    esiti = {}
    for eti, base in BRACCI:
        celle = prime_valide(base)
        tot = si = mancanti = 0
        senza_alcuna_call = 0
        for b, trajs in celle.items():
            for t in trajs:
                v = chiama(t)
                if v is None:
                    mancanti += 1
                    continue
                tot += 1
                si += bool(v)
        esiti[eti] = (si, tot)
        pct = 100 * si / tot if tot else float("nan")
        print(f"  {eti:<9} {si:>4}/{tot:<4} run  ({pct:5.1f}%)   binari {len(celle)}"
              + (f"   traiettorie assenti: {mancanti}" if mancanti else ""))

    (sn, tn), (st, tt) = esiti["nativo"], esiti["testuale"]
    dn, dt = 100 * sn / tn, 100 * st / tt
    print(f"\n  differenza fra i bracci: {dn - dt:+.1f} punti percentuali")
    print("\n  CONFRONTO con il conto sbagliato del 2026-08-15, che usava un grep sull'intero")
    print("  file e quindi pescava tools_offered: dava 362/362 e 546/546, cioe' 100% su")
    print("  entrambi i bracci — e con denominatori che non sono quelli della pipeline.")
    if abs(dn - dt) > 1:
        print(f"\n  ESITO: l'esposizione NON e' simmetrica. Il braccio nativo incontra il canale")
        print(f"  {dn - dt:.1f}pp piu' spesso del testuale. E' meno dei 31pp che hanno invalidato il")
        print("  primo lotto di C2 (73% contro 42%), ma non e' zero: la frase «l'esposizione era")
        print("  simmetrica fra i due bracci» e' falsa e non si puo' usare per escludere che")
        print("  l'apparato contribuisca alla divergenza fra C1 e C2.")
    else:
        print("\n  ESITO: l'esposizione e' simmetrica entro un punto percentuale.")
