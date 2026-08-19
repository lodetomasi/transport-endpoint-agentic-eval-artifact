#!/usr/bin/env python3
"""Stato di un braccio a un istante dato, e quali degli otto contrasti erano calcolabili.

Esiste per una ragione sola: SPEC-06 chiede di stabilire se la soglia 6/8 possa essere stata
calibrata su un esito gia' noto. La risposta non e' un'opinione, e' un conteggio sulle righe
rilasciate a un cutoff. Il controllo negativo e' il cutoff finale: li' tutti e otto DEVONO
risultare calcolabili, altrimenti la funzione risponde di no per un difetto proprio.

    python3 revisione/stato_a_cutoff.py 2026-08-16T08:22:00
"""
import collections, csv, glob, os, sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RADICE, "src"))
from qualita_run import e_misurazione  # noqa: E402

MODELLI = ["gpt-oss-120b", "llama-3.3-70b", "claude-haiku-4-5", "claude-sonnet-4-5"]
# T1-T4: trasporto a databricks. T5-T8: infrastruttura a native.
CONTRASTI = ([("T%d" % (i + 1), [(m, "databricks", "native"), (m, "databricks", "text")])
              for i, m in enumerate(MODELLI)]
             + [("T%d" % (i + 5), [(m, "databricks", "native"), (m, "bedrock", "native")])
                for i, m in enumerate(MODELLI)])
MIN_BINARI = 45  # un contrasto appaiato su 45 binari: sotto, non e' quel contrasto


def stato(cartella, cutoff):
    binari = collections.defaultdict(set)
    n = 0
    for f in sorted(glob.glob(os.path.join(cartella, "*.csv"))):
        for r in csv.DictReader(open(f, errors="ignore")):
            if not e_misurazione(r):
                continue
            if cutoff and (r.get("timestamp") or "") >= cutoff:
                continue
            n += 1
            binari[(r["modello"], r["infra"], r["trasporto"])].add(r["binary_id"])
    calcolabili = [t for t, celle in CONTRASTI
                   if all(len(binari.get(c, ())) >= MIN_BINARI for c in celle)]
    return n, sorted(k for k in binari if binari[k]), calcolabili


if __name__ == "__main__":
    cartella = os.path.join(RADICE, "results", "riraccolta")
    for cutoff in sys.argv[1:] or [None]:
        n, celle, calc = stato(cartella, cutoff)
        print("cutoff=%s righe=%d celle=%d contrasti_calcolabili=%s"
              % (cutoff or "(nessuno)", n, len(celle), ",".join(calc) or "nessuno"))
        for c in celle:
            print("    ", c)

    # IL CONTROLLO NEGATIVO, ORA CABLATO A UN EXIT CODE. Il docstring lo prometteva e il
    # blocco si limitava a stampare: una regressione che mostrasse 7 contrasti su 8 sarebbe
    # passata con exit 0, visibile solo a un umano che leggesse l'output. Trovato da una code
    # review. Senza cutoff la raccolta e' completa e TUTTI e otto devono essere calcolabili.
    n, celle, calc = stato(cartella, None)
    print("\nCONTROLLO a risposta nota")
    print("  a raccolta completa tutti gli otto contrasti devono essere calcolabili: "
          "%d/8 -> %s" % (len(calc), "ok" if len(calc) == len(CONTRASTI) else "FALLITO"))
    sys.exit(0 if len(calc) == len(CONTRASTI) else 1)
