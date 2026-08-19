#!/usr/bin/env python3
"""L'esposizione alla workdir condivisa, e la sonda che ne cerca la firma.

`run_minipilot.py` compila ogni candidato in `results/workv3/<prog>_r<run_id>` -- una chiave
che NON contiene modello, infrastruttura ne' trasporto. Le sedici celle condividono quindi 360
directory, e la raccolta e' girata con collettori concorrenti.

Questo script produce i numeri che il paper cita nelle minacce alla validita':

  1. la FINESTRA: quanto dura la fase docker, cioe' l'intervallo fra la scrittura di
     candidate.c e la sua lettura dentro il container. Si misura eseguendola, con un
     percorso ASSOLUTO -- con un percorso relativo docker rifiuta il bind mount e la
     funzione torna in 0,03 s con compiled=False, che a occhio sembra "docker e' velocissimo".
  2. le ESPOSIZIONI: coppie di righe da CELLE DIVERSE sullo stesso (binario, run_id) vicine
     nel tempo.
  3. la SONDA: se una collisione fosse avvenuta, due righe vicine avrebbero valutato lo stesso
     file e dovrebbero CONCORDARE PIU' del caso. Si confronta la concordanza fra righe vicine
     e lontane A PARITA' DI COPPIA DI CELLE, perche' senza quel controllo si misurerebbe
     quanto due celle si somigliano invece della firma della collisione.

La sonda non e' una prova di assenza, e il suo limite si stampa insieme al numero.
"""
import csv
import glob
import os
import re
import statistics
import sys
import tempfile
import time
from collections import Counter, defaultdict
from datetime import datetime as dt, timedelta

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VICINO_S = 5.0


def righe():
    out = []
    for f in sorted(glob.glob(os.path.join(RADICE, "results", "c2_*.csv"))):
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                t = (r.get("timestamp") or "").replace("Z", "+00:00")
                try:
                    t = dt.fromisoformat(t)
                    pr = float(r["pass_rate"])
                except (ValueError, KeyError):
                    continue
                out.append((r["binary_id"], r["run_id"], t,
                            (r["modello"], r["infra"], r["trasporto"]), pr))
    return out


def finestra_docker():
    """Misura la fase docker. Percorso ASSOLUTO: e' la condizione della raccolta."""
    sys.path.insert(0, os.path.join(RADICE, "src"))
    try:
        from run_minipilot import compile_and_test
    except ImportError as e:
        return None, f"harness non importabile: {e}"
    cand = '#include <stdio.h>\nint main(void){printf("ok\\n");return 0;}\n'
    tests = [{"args": [], "stdin": "", "expected_stdout": "ok\n"}] * 5
    base = os.path.join(RADICE, "local", "misura_collisione")
    tempi, esiti = [], []
    for i in range(4):
        t0 = time.time()
        r = compile_and_test(cand, tests, __import__("pathlib").Path(base) / f"a{i}")
        tempi.append(time.time() - t0)
        esiti.append(bool(r.get("compiled")))
    # Un tempo bassissimo CON compiled=False non e' "docker e' veloce": e' docker che non ha
    # girato. Si dichiara invece di stampare un numero rassicurante e falso.
    if not all(esiti):
        return None, ("la compilazione non e' riuscita: il numero misurato sarebbe il "
                      "percorso d'errore, non la fase docker")
    return statistics.median(tempi), None


def main():
    rs = righe()
    per = defaultdict(list)
    for b, rid, t, cella, pr in rs:
        per[(b, rid)].append((t, cella, pr))

    print("Workdir condivisa: esposizione e sonda")
    print(f"  righe con timestamp: {len(rs)}")
    # Si contano SOLO le cartelle nello schema piatto <prog>_r<run>, che e' quello con cui
    # la raccolta confermativa e' avvenuta e a cui il numero del paper si riferisce. Dopo la
    # successione 08 lo stesso albero ospita anche cartelle-tag per cella, e sommarle darebbe
    # un'esposizione inflazionata che sembra una misura nuova: 362 invece di 360 gia' oggi,
    # con due soli smoke. Trovato da `onus:harness-critic` prima della raccolta.
    radice_work = os.path.join(RADICE, "results", "workv3")
    voci = os.listdir(radice_work) if os.path.isdir(radice_work) else []
    piatte = [v for v in voci if re.match(r"^prog\d+.*_r\d+$", v)]
    per_cella = [v for v in voci if v not in piatte]
    print(f"  directory nello schema piatto (quello della raccolta confermativa): "
          f"{len(piatte)} per 16 celle")
    if per_cella:
        print(f"  cartelle per cella, schema nuovo, ESCLUSE dal conteggio: {len(per_cella)}\n")
    else:
        print()

    med, errore = finestra_docker()
    if errore:
        print(f"  FINESTRA: non misurata -- {errore}")
    else:
        print(f"  FINESTRA (mediana della fase docker, 4 esecuzioni): {med:.2f} s")

    print("\n  ESPOSIZIONI: coppie stesso (binario, run_id) da CELLE DIVERSE")
    for f in (2, 5, 15, 30, 60):
        n = 0
        for v in per.values():
            v.sort()
            for i in range(len(v)):
                for j in range(i + 1, len(v)):
                    if v[j][1] == v[i][1]:
                        continue
                    if (v[j][0] - v[i][0]).total_seconds() > f:
                        break
                    n += 1
        print(f"    entro {f:>3} s: {n:>4}")

    vic, lon = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
    for v in per.values():
        for i in range(len(v)):
            for j in range(i + 1, len(v)):
                if v[i][1] == v[j][1]:
                    continue
                k = tuple(sorted(["/".join(v[i][1]), "/".join(v[j][1])]))
                d = abs((v[j][0] - v[i][0]).total_seconds())
                uguali = 1 if abs(v[i][2] - v[j][2]) < 1e-9 else 0
                tgt = vic if d <= VICINO_S else lon
                tgt[k][0] += uguali
                tgt[k][1] += 1

    print(f"\n  SONDA: concordanza di pass_rate, righe vicine (<={VICINO_S:.0f}s) contro lontane,")
    print("         A PARITA' DI COPPIA DI CELLE. Una collisione alzerebbe le vicine.")
    tv, tl = [0, 0], [0, 0]
    coppie = 0
    for k in sorted(vic):
        if vic[k][1] < 5 or k not in lon:
            continue
        coppie += 1
        v, l = vic[k], lon[k]
        tv[0] += v[0]; tv[1] += v[1]; tl[0] += l[0]; tl[1] += l[1]
        print(f"    {k[0]} vs {k[1]}")
        print(f"      vicine {v[0]}/{v[1]} = {100*v[0]/v[1]:5.1f}%   "
              f"lontane {l[0]}/{l[1]} = {100*l[0]/l[1]:5.1f}%")
    if tv[1] and tl[1]:
        d = 100 * tv[0] / tv[1] - 100 * tl[0] / tl[1]
        print(f"\n    differenza: {d:+.1f} punti  (una collisione la darebbe POSITIVA)")
    print(f"\n  LIMITE DELLA SONDA, che si stampa col numero: {coppie} coppia/e di celle ha")
    print("  abbastanza casi. Una sola coppia non regge un confronto appaiato generale, e il")
    print("  segno si attenua o si inverte controllando per l'identita' del modello. La sonda")
    print("  NON prova assenza: dice che la firma attesa non c'e' dove i dati permettono di")
    print("  cercarla. E la questione resta indecidibile per costruzione, perche' workv3/")
    print("  conserva solo l'ultimo scrittore per directory.")


if __name__ == "__main__":
    main()
