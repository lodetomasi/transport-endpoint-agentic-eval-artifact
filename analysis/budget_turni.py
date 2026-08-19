#!/usr/bin/env python3
"""Quante run esauriscono il budget di 12 turni, e in quale braccio.

La card v6 affermava: «nessuna run esaurisce il budget di 12 turni: e' opportunita' persa,
non turni bruciati». Serviva a delimitare il confondimento del batching — il nativo puo'
raggruppare piu' chiamate in un turno, il testuale ne ha una per costruzione.

L'affermazione era falsa, e la correzione INVERTE la direzione dell'argomento invece di
aggiungere un numero: se il budget si esaurisce solo nel braccio che puo' raggruppare, il
confondimento e' piu' forte, non delimitato.

Trovato dal seggio avversariale del gauntlet, 2026-08-15.

Una traiettoria ha una riga per turno. Il budget e' N=12; una traiettoria con 13 righe ha
usato tutti i turni piu' il turno finale di sottomissione forzata.
"""
import glob
import os

# Le traiettorie delle due raccolte vivono nella stessa cartella, distinte dal prefisso del tag:
# «c2_» la confermativa, «c2r_» la ri-raccolta. Il glob era «*/», che le sommava — e un conteggio
# di run che esauriscono il budget sommato fra due raccolte non e' il conteggio di nessuna delle
# due. Il prefisso si scegli, e il default resta la confermativa.
PREFISSO = os.environ.get("C2_PREFISSO", "c2_")
import re
import os
from collections import Counter, defaultdict

SOGLIA = 13


def trasporto(cella):
    """Il trasporto dal tag della cella, ANCORATO alla fine.

    Con un test di sottostringa, `c2a_..._native1` — il tag del braccio di ablazione —
    risultava "nativo", e le sue traiettorie sarebbero finite nel bucket che sostiene
    l'argomento sul confondimento del batching, gonfiandolo con dati che nativo pieno non
    sono. Trovato da `onus:harness-critic` prima che l'ablazione raccogliesse.
    """
    # Il tag e' c2_<modello>_<infra>_<trasporto>[<suffisso di ripresa>]. Il trasporto va
    # riconosciuto con un confine: `endswith` da solo perde tutte le riesecuzioni (_redo,
    # _redo2), un test di sottostringa prende per nativo anche l'ablazione (_native1).
    m = re.search(r"_(native|text)(_redo\d*)?$", cella)
    if not m:
        return "?"    # ablazione (`_native1`) e ogni altro braccio: fuori dal conteggio
    return "nativo" if m.group(1) == "native" else "testuale"


if __name__ == "__main__":
    tot = Counter()
    pieni = Counter()
    esempi = defaultdict(list)

    for t in glob.glob(os.path.join("results", "trajectories", PREFISSO + "*", "*.jsonl")):
        if "invalidati" in t:
            continue
        # Un braccio per volta: esplorativo (c2x_) e ablazione (c2a_) rispondono a domande
        # diverse e non entrano in questo numero. Il prefisso era fissato QUI OLTRE che nel
        # glob, e correggendo solo il glob lo script contava zero traiettorie stampando
        # tranquillamente «0 esauriscono il budget» — un filtro che scarta tutto travestito
        # da risultato. Due punti, un solo parametro.
        if not os.path.basename(os.path.dirname(t)).startswith(PREFISSO):
            continue
        cella = os.path.basename(os.path.dirname(t))
        tr = trasporto(cella)
        righe = sum(1 for _ in open(t, errors="ignore"))
        tot[tr] += 1
        if righe >= SOGLIA:
            pieni[tr] += 1
            esempi[tr].append((righe, cella, os.path.basename(t)))

    n_tot = sum(tot.values())
    n_pieni = sum(pieni.values())
    print(f"Budget dei turni esaurito — soglia {SOGLIA} righe (N=12 piu' il turno finale)\n")
    print(f"  traiettorie totali: {n_tot}")
    if not n_tot:
        raise SystemExit(f"  nessuna traiettoria con prefisso {PREFISSO!r}: il filtro scarta "
                         "tutto, e zero non e' una misura (exit 2)")
    print(f"  che esauriscono il budget: {n_pieni}  ({100*n_pieni/n_tot:.1f}%)\n")
    print(f"  {'braccio':<12}{'totali':>8}{'al budget':>12}{'quota':>9}")
    for tr in ("nativo", "testuale"):
        q = 100 * pieni[tr] / tot[tr] if tot[tr] else 0.0
        print(f"  {tr:<12}{tot[tr]:>8}{pieni[tr]:>12}{q:>8.1f}%")

    print("\n  Qualche caso concreto nel braccio che li esaurisce:")
    for righe, cella, f in sorted(esempi["nativo"], reverse=True)[:5]:
        print(f"    {righe} righe   {cella}/{f}")

    print("\n  LETTURA. La card v6 diceva che nessuna run esaurisce il budget, e ne concludeva")
    print("  che il batching e' opportunita' persa per il testuale invece che turni bruciati.")
    if pieni["testuale"] == 0 and pieni["nativo"] > 0:
        print("  E' vero il contrario di quel che serviva all'argomento: il budget si esaurisce")
        print("  SOLO nel braccio nativo, cioe' quello che puo' raggruppare le chiamate. Per")
        print(f"  quelle {pieni['nativo']} run il batching non e' un vantaggio inutilizzato: e' cio' che ha")
        print("  permesso di arrivare in fondo. Il confondimento di T3 e T4 e' piu' forte, non")
        print("  delimitato, e va riportato cosi'.")
    else:
        print(f"  Esauriscono il budget {pieni['nativo']} run native e {pieni['testuale']} testuali.")
