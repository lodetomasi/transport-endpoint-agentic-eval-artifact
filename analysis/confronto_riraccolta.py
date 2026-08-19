#!/usr/bin/env python3
"""I quattro criteri di EMENDAMENTO-06, calcolati sulle due raccolte.

Scritto e congelato PRIMA che la ri-raccolta produca una riga. E' l'intera ragione per cui
esiste: a dati visti, «le conclusioni sono invariate» e' una frase che si puo' far dire a
quasi qualunque coppia di raccolte scegliendo cosa guardare. I quattro criteri, le due soglie
a 6 su 8, e la scelta della raccolta primaria sono dichiarati nell'emendamento e qui
implementati senza sapere che numeri usciranno.

L'ASPETTATIVA NON E' L'UGUAGLIANZA. Questo capitolo misura che a temperatura zero il punteggio
non e' stabile: due raccolte identiche DEVONO differire. Una coincidenza esatta sarebbe un
allarme sull'apparato, non un successo — ed e' il primo controllo che questo script stampa.

Riusa `analyze_c2` senza modificarlo (e' congelato): `carica()` prende una cartella, quindi le
due raccolte si leggono separatamente per costruzione e non per convenzione sui nomi.

    python3 analysis/confronto_riraccolta.py --vecchia results --nuova results/riraccolta
"""
import argparse
import math
import os
import statistics as st
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from analyze_c2 import (MODELLI, INFRA, TRASPORTI, carica, media_per_binario,  # noqa: E402
                        t_appaiato)

# Gli otto contrasti appaiati della famiglia. T9 e T10 non sono contrasti appaiati e si
# confrontano a parte, sull'esito e non sulla copertura.
OTTO = ([("T%d" % (i + 1), "trasporto", m) for i, m in enumerate(MODELLI)]
        + [("T%d" % (i + 5), "infrastruttura", m) for i, m in enumerate(MODELLI)])
SOGLIA_SEGNI = 6      # su 8, da EMENDAMENTO-06
SOGLIA_COPERTURA = 6  # su 8, da EMENDAMENTO-06


def contrasto(celle, tipo, modello):
    """Il contrasto come lo definisce la famiglia: trasporto a infrastruttura fissa
    (databricks), infrastruttura a trasporto fisso (native)."""
    if tipo == "trasporto":
        a = media_per_binario(celle, modello, "databricks", "native")
        b = media_per_binario(celle, modello, "databricks", "text")
    else:
        a = media_per_binario(celle, modello, "databricks", "native")
        b = media_per_binario(celle, modello, "bedrock", "native")
    return t_appaiato(a, b)


def segno(x):
    return 0 if (x != x or x == 0) else (1 if x > 0 else -1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--vecchia", default="results")
    ap.add_argument("--nuova", default="results/riraccolta")
    a = ap.parse_args()

    if not os.path.isdir(a.nuova):
        sys.exit(f"{a.nuova} non esiste ancora: la ri-raccolta non ha prodotto dati")

    vecchie, _ = carica(a.vecchia)
    nuove, _ = carica(a.nuova)
    if not nuove:
        sys.exit(f"nessuna misurazione in {a.nuova}/")

    righe = []
    for eti, tipo, mod in OTTO:
        nv, mv, lov, hiv, _, pv = contrasto(vecchie, tipo, mod)
        nn, mn, lon, hin, _, pn = contrasto(nuove, tipo, mod)
        righe.append((eti, tipo, mod, nv, mv, lov, hiv, pv, nn, mn, lon, hin, pn))

    assert len(righe) == 8, f"calcolati {len(righe)} contrasti, attesi 8"

    print("Confronto fra le due raccolte — i quattro criteri di EMENDAMENTO-06\n")
    print(f"  {'':<4}{'':<20}{'VECCHIA':>22}{'NUOVA':>22}")
    print(f"  {'id':<4}{'modello':<20}{'diff':>10}{'IC95':>12}{'diff':>10}{'IC95':>12}"
          f"{'dentro':>8}")
    concordi = dentro = 0
    identici = 0
    for (eti, _t, mod, nv, mv, lov, hiv, _pv, nn, mn, lon, hin, _pn) in righe:
        if nv < 2 or nn < 2:
            print(f"  {eti:<4}{mod:<20}  cella incompleta in una delle due raccolte")
            continue
        conc = segno(mv) == segno(mn)
        cop = lov <= mn <= hiv
        concordi += conc
        dentro += cop
        identici += abs(mv - mn) < 1e-9
        print(f"  {eti:<4}{mod:<20}{100*mv:>+9.1f}pp"
              f"{f'[{100*lov:+.1f},{100*hiv:+.1f}]':>12}"
              f"{100*mn:>+9.1f}pp{f'[{100*lon:+.1f},{100*hin:+.1f}]':>12}"
              f"{'si' if cop else 'NO':>8}")

    print(f"\n  CRITERIO 1 — segni concordi   : {concordi}/8  "
          f"(soglia {SOGLIA_SEGNI}) -> {'INVARIATO' if concordi >= SOGLIA_SEGNI else 'DIVERGE'}")
    print(f"  CRITERIO 3 — copertura IC95   : {dentro}/8  "
          f"(soglia {SOGLIA_COPERTURA}) -> {'INVARIATO' if dentro >= SOGLIA_COPERTURA else 'DIVERGE'}")

    # Il controllo di cui si conosce gia' la risposta, e va nel verso dell'allarme: due
    # raccolte a temperatura zero su un apparato non deterministico non possono coincidere.
    if identici:
        print(f"\n  ALLARME: {identici}/8 contrasti hanno differenza esattamente nulla fra le")
        print("  due raccolte. Su un apparato che questo capitolo misura come non")
        print("  deterministico, questo non e' conferma: e' il sospetto che le due cartelle")
        print("  contengano gli stessi file. Verificare prima di leggere qualunque criterio.")

    print("\n  CRITERIO 2 — esito della famiglia: eseguire `analyze_c2.py --results "
          f"{a.nuova}` e confrontare quali test superano Holm a m=10.")
    print("  Se nella nuova ne sopravvive uno, si riporta come DIFFERENZA fra le raccolte e")
    print("  non come risultato confermativo: la famiglia e' gia' stata spesa una volta.")
    print("\n  CRITERIO 4 — decomposizione della varianza: eseguire lo script che produce la")
    print("  quota di rumore run-to-run su entrambe e verificare l'ordine di grandezza.")

    print("\n  La raccolta PRIMARIA e' la nuova, deciso in EMENDAMENTO-06 prima di vedere")
    print("  questi numeri, sul solo criterio disponibile allora: ha l'apparato corretto.")
