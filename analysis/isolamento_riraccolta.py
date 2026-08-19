#!/usr/bin/env python3
"""La ri-raccolta sta davvero eliminando le collisioni? Verificato durante, non dopo.

La ri-raccolta costa $138,83 e serve a una cosa sola: togliere la condizione per cui due celle
potevano compilare nella stessa directory. Se il difetto fosse ancora li', lo si scoprirebbe a
spesa conclusa — e sarebbe la seconda volta, perche' la prima raccolta e' finita prima che
qualcuno guardasse.

Tre controlli, tutti eseguibili su una raccolta parziale:

  1. Il tag della cella sta NEL PERCORSO, o non c'e'. Si legge dalla profondita', non dal
     nome: `workv3/prog16_r1` e' condivisa da tutte le celle, `workv3/<cella>/prog16_r1` no.
  2. NESSUNA cartella della ri-raccolta coincide con una directory condivisa dell'originale.
     Se coincidesse, la nuova starebbe scrivendo dove scriveva quella con cui va confrontata.
  3. La sonda temporale: due misurazioni di celle diverse, sullo STESSO binario e la STESSA
     run, entro due secondi. E' la precondizione esatta della collisione, e sulla raccolta
     originale ne trova 30 — lo stesso numero che il paper riporta, ottenuto qui per una via
     indipendente.

Il terzo e' il controllo di cui si conosce gia' la risposta in un verso: se sulla ri-raccolta
uscisse un numero simile a 30, la correzione non avrebbe morso e si fermerebbe.
"""
import csv
import glob
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, os.path.join(RADICE, "src"))
from qualita_run import e_misurazione  # noqa: E402


RUN = re.compile(r"^prog\d+_.*_r\d+$")


def condivise_e_isolate():
    """La collisione non si legge dal NOME della sottocartella: due celle diverse hanno
    legittimamente un `prog16_..._r1` ciascuna, in percorsi distinti. Si legge dalla PROFONDITA'.

    - `workv3/prog16_..._r1`            -> nessun livello di cella: TUTTE le celle la
                                          condividono. E' il difetto della prima raccolta.
    - `workv3/<cella>/prog16_..._r1`    -> il tag e' nel percorso: appartiene a una cella sola.

    La prima versione di questo controllo confrontava i nomi delle sottocartelle e segnalava
    come collisione due percorsi distinti. Falliva per la ragione sbagliata, che e' il modo in
    cui un controllo produce un allarme e nessuna informazione."""
    base = os.path.join(RADICE, "results", "workv3")
    condivise, isolate = [], defaultdict(list)
    for d in sorted(glob.glob(os.path.join(base, "*"))):
        if not os.path.isdir(d):
            continue
        n = os.path.basename(d)
        if RUN.match(n):
            condivise.append(n)          # senza cella nel percorso
        else:
            for sub in glob.glob(os.path.join(d, "*")):
                if os.path.isdir(sub) and RUN.match(os.path.basename(sub)):
                    isolate[n].append(os.path.basename(sub))
    return condivise, isolate


def istanti(pattern):
    out = []
    for f in glob.glob(os.path.join(RADICE, pattern)):
        cella = os.path.basename(f)[:-4]
        for r in csv.DictReader(open(f, errors="ignore")):
            if not e_misurazione(r):
                continue
            v = (r.get("timestamp") or "")[:26]
            for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
                try:
                    out.append((datetime.strptime(v, fmt), cella,
                                r.get("binary_id", ""), r.get("run_id", "")))
                    break
                except ValueError:
                    pass
    out.sort()
    return out


if __name__ == "__main__":
    problemi = []

    # --- 1. il tag della cella e' nel percorso, o non c'e'
    condivise, isolate = condivise_e_isolate()
    nuove_isolate = sum(len(v) for k, v in isolate.items() if k.startswith("c2r_"))
    print(f"  directory SENZA cella nel percorso (condivise da tutte): {len(condivise)}")
    print(f"  directory della ri-raccolta, isolate per cella         : {nuove_isolate}")
    if nuove_isolate == 0:
        problemi.append("la ri-raccolta non ha ancora scritto directory isolate: verificare")
    for k in sorted(isolate):
        if k.startswith("c2r_"):
            print(f"    {k}: {len(isolate[k])} run")

    # --- 2. nessuna sovrapposizione con la raccolta originale
    base = os.path.join(RADICE, "results", "workv3")
    nuove = {os.path.basename(d) for d in glob.glob(os.path.join(base, "c2r_*"))}
    sovrapposte = nuove & set(condivise)
    print(f"\n  cartelle di cella nuove: {len(nuove)}; coincidenti con una directory "
          f"condivisa dell'originale: {len(sovrapposte)}")
    if sovrapposte:
        problemi.append(f"la ri-raccolta scrive dove scriveva l'originale: {sorted(sovrapposte)[:3]}")

    # --- 3. la sonda temporale. DUE quantita', e la loro differenza e' il punto.
    #
    # La vicinanza temporale su (binario, run) era diagnostica quando le workdir erano
    # CONDIVISE: due celle a un secondo di distanza compilavano lo stesso file. Con la workdir
    # che porta il tag della cella quella implicazione cade — la vicinanza resta, la collisione
    # no. Contare solo la vicinanza applica all'apparato nuovo il criterio del vecchio, ed e'
    # lo stesso errore gia' corretto in esposizione_concorrenza.py: qui era rimasto, e
    # segnalava «la condizione persiste» su una coppia le cui directory sono diverse.
    #
    # Quello che conta e' la CONGIUNZIONE: vicini nel tempo E sullo stesso percorso.
    def workdir(cella, binario, run):
        return f"workv3/{cella}/{binario}_r{run}"

    for eti, pat, atteso in (("originale ", "results/c2_*.csv", "30 condivisi, il difetto"),
                             ("ri-raccolta", "results/riraccolta/c2r_*.csv", "atteso: nessuno")):
        ev = istanti(pat)
        # l'originale non aveva il tag: la workdir era workv3/<binario>_r<run> per tutti
        con_tag = eti.startswith("ri-rac")
        vicini = condivisi = 0
        for i, (t, c, b, r) in enumerate(ev):
            for j in range(i - 1, -1, -1):
                if (t - ev[j][0]).total_seconds() > 2:
                    break
                if ev[j][1] != c and (ev[j][2], ev[j][3]) == (b, r):
                    vicini += 1
                    if not con_tag or workdir(c, b, r) == workdir(ev[j][1], ev[j][2], ev[j][3]):
                        condivisi += 1
                    break
        print(f"\n  {eti}: {len(ev)} misurazioni, {vicini} vicine entro 2 s sullo stesso "
              f"(binario, run), di cui {condivisi} SULLO STESSO PERCORSO  [{atteso}]")
        if eti.startswith("orig") and condivisi < 25:
            problemi.append(f"la sonda trova solo {condivisi} percorsi condivisi "
                            "nell'originale, dove il difetto ne aveva 30: il criterio non "
                            "rileva piu' il caso noto e non prova nulla sulla ri-raccolta")
        if eti.startswith("ri-rac") and condivisi:
            problemi.append(f"{condivisi} coppie CONDIVIDONO IL PERCORSO nella ri-raccolta: "
                            "l'isolamento non tiene")

    print()
    if problemi:
        for p in problemi:
            print(f"  PROBLEMA: {p}")
        print("\n  Fermare la ri-raccolta: sta comprando lo stesso difetto una seconda volta.")
        sys.exit(1)
    print("  L'isolamento tiene: ogni directory appartiene a una cella sola, nessuna")
    print("  sovrapposizione con l'originale, e la precondizione della collisione non si")
    print("  ripresenta sui dati raccolti finora.")
