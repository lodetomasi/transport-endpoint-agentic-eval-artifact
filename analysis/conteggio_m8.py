#!/usr/bin/env python3
"""M8 — quante traiettorie l'endpoint ha rifiutato per il nome di tool che il suo stesso modello emette.

PERCHE' ESISTE. Il numero (11 traiettorie) compariva nel paper senza uno script che lo producesse,
mentre le Declarations affermano che ogni quantita' viene da uno script committato. Un seggio di
riproducibilita' l'ha riprodotto a mano con un grep e ha segnalato la contraddizione.

L'unita' e' la TRAIETTORIA, non l'occorrenza della stringa: le occorrenze sono 21 contando il lotto
invalidato, e i due numeri rispondono a due domande diverse. Qui si contano le run che l'endpoint ha
rifiutato nei due lotti conservati.

    python3 analysis/conteggio_m8.py
"""
import glob, os, sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOME = "decompile_function<|channel|>commentary"
ATTESI = {"originale": 4, "riraccolta": 7}   # controllo a risposta nota, dal paper


def per_braccio():
    fuori = {"originale": [], "riraccolta": [], "invalidato": []}
    for p in sorted(glob.glob(os.path.join(RADICE, "results", "**", "*.jsonl"), recursive=True)):
        if NOME not in open(p, errors="ignore").read():
            continue
        rel = os.path.relpath(p, RADICE)
        braccio = ("invalidato" if "/invalidati/" in rel else
                   "riraccolta" if "/c2r_" in rel else "originale")
        fuori[braccio].append(rel)
    return fuori


def main():
    b = per_braccio()
    print("  M8 — traiettorie in cui il nome generato dal modello raggiunge la validazione dell'API\n")
    for braccio in ("originale", "riraccolta", "invalidato"):
        print("  %-12s %d traiettorie" % (braccio, len(b[braccio])))
        for f in b[braccio]:
            print("      ", f)
    conservate = len(b["originale"]) + len(b["riraccolta"])
    print("\n  nei due lotti conservati: %d traiettorie" % conservate)

    print("\n  CONTROLLO a risposta nota, nei due sensi")
    ok = True
    for braccio, atteso in ATTESI.items():
        buono = len(b[braccio]) == atteso
        ok &= buono
        print("    %-12s atteso %d, ottenuto %d: %s"
              % (braccio, atteso, len(b[braccio]), "ok" if buono else "FALLITO"))
    # controllo NEGATIVO: un nome che nessun endpoint ha mai restituito deve dare zero.
    finto = "decompile_function<|channel|>QUESTO_NON_ESISTE"
    trovate = sum(1 for p in glob.glob(os.path.join(RADICE, "results", "**", "*.jsonl"), recursive=True)
                  if finto in open(p, errors="ignore").read())
    ok &= trovate == 0
    print("    un nome inesistente deve dare 0: %d -> %s" % (trovate, "ok" if trovate == 0 else "FALLITO"))
    return 0 if ok and conservate == 11 else 1


if __name__ == "__main__":
    sys.exit(main())
