#!/usr/bin/env python3
"""Quante tool call per turno, per trasporto — il budget asimmetrico che H1 confonde.

`agent_loop.py` esegue TUTTE le tool call che il modello restituisce in un turno nativo. Il
protocollo testuale ne forza esattamente UNA: `_parse_text_tool_call` legge una sola riga
`TOOL_CALL:` per risposta.

A dodici turni fissi per entrambi i bracci, un modello capace di chiamate multiple estrae piu'
informazione a parita' di turni NOMINALI. E' strutturalmente lo stesso meccanismo del capitolo
precedente -- un budget negato a un braccio -- applicato al trasporto invece che al contesto.

Questo NON cambia il disegno pre-registrato. Si riporta come covariata dichiarata, e si dichiara
PRIMA di vedere se H1 si conferma: se l'effetto e' in parte spiegato da un budget di chiamate
diseguale, la lettura corretta si stringe da «il trasporto sposta il numero» a «questa
operazionalizzazione del trasporto testuale nega piu' chiamate per turno». Saperlo dopo, con un
revisore che lo trova, sarebbe la stessa frase scritta come giustificazione.

    python3 analysis/chiamate_per_turno.py
"""
import collections
import json
import statistics as st
import sys
from pathlib import Path
import os

# Le traiettorie delle due raccolte convivono nella stessa cartella, distinte dal prefisso del
# tag. Leggerle tutte somma raccolte diverse in una media che non appartiene a nessuna.
PREFISSO = os.environ.get("C2_PREFISSO", "c2_")


RADICE = Path(__file__).resolve().parent.parent


def per_cella(d: Path):
    """Chiamate per turno, su ogni traiettoria della cella."""
    per_turno, turni_con_call, turni_tot = [], 0, 0
    for f in d.glob("*.jsonl"):
        for riga in f.read_text(errors="ignore").splitlines():
            if not riga.strip():
                continue
            try:
                t = json.loads(riga)
            except json.JSONDecodeError:
                continue
            n = len(t.get("tool_calls") or [])
            turni_tot += 1
            if n:
                turni_con_call += 1
                per_turno.append(n)
    return per_turno, turni_con_call, turni_tot


def main():
    base = RADICE / "results" / "trajectories"
    if not base.is_dir():
        sys.exit("nessuna traiettoria")
    celle = collections.defaultdict(list)
    for d in sorted(base.iterdir()):
        if not d.is_dir() or not d.name.startswith(PREFISSO):
            continue
        # <prefisso><modello>_<infra>_<trasporto>[_redoN]. Lo slice era fisso a [3:], cioe'
        # alla lunghezza di «c2_»: con «c2r_» avrebbe tagliato un carattere di troppo e il
        # modello sarebbe arrivato mutilato invece che assente, che e' peggio.
        parti = d.name[len(PREFISSO):].rsplit("_", 1)
        if parti[-1].startswith("redo"):
            parti = parti[0].rsplit("_", 1)
        trasporto = parti[-1]
        resto = parti[0]
        celle[(resto, trasporto)].append(d)

    print(f"  {'cella':46s}{'turni':>8}{'con call':>10}{'call/turno':>12}{'max':>6}")
    riepilogo = collections.defaultdict(list)
    for (resto, tr), dirs in sorted(celle.items()):
        tutte, con, tot = [], 0, 0
        for d in dirs:
            a, b, c = per_cella(d)
            tutte += a; con += b; tot += c
        if not tot:
            continue
        media = st.mean(tutte) if tutte else 0.0
        riepilogo[tr] += tutte
        print(f"  {resto + '/' + tr:46s}{tot:>8}{100 * con // tot:>9}%{media:>12.3f}"
              f"{max(tutte) if tutte else 0:>6}")

    print()
    for tr in ("native", "text"):
        v = riepilogo.get(tr) or []
        if not v:
            continue
        print(f"  {tr:8s} {len(v)} turni con chiamata, media {st.mean(v):.3f} call/turno, "
              f"massimo {max(v)}, turni con >1 chiamata: {100 * sum(1 for x in v if x > 1) // len(v)}%")
    # Il pooling fra modelli NASCONDE la storia: il confondimento non e' uniforme, e la media
    # su tutti i modelli lo diluisce fino a farlo sparire. Va letto per modello.
    print("\n  Per modello, che e' dove sta la storia:")
    per_mod = collections.defaultdict(dict)
    for (resto, tr), dirs in celle.items():
        tutte = []
        for d in dirs:
            tutte += per_cella(d)[0]
        if tutte:
            per_mod[resto.rsplit("_", 1)[0]][tr] = tutte
    for m, d in sorted(per_mod.items()):
        nat = d.get("native") or []
        if not nat:
            continue
        piu_di_uno = 100 * sum(1 for x in nat if x > 1) / len(nat)
        stato = ("confondimento REALE" if piu_di_uno >= 5 else "confondimento trascurabile")
        print(f"    {m:22s} nativo {st.mean(nat):.3f} call/turno, "
              f"{piu_di_uno:.0f}% dei turni con >1 chiamata  -> {stato}")

    print("\n  Il confondimento e' STRUTTURALMENTE possibile -- agent_loop esegue tutte le call di un")
    print("  turno nativo, il testuale ne forza una -- ma i modelli devono usarlo perche' morda, e")
    print("  quasi nessuno lo usa. Dove morde, si riporta come covariata dichiarata: NON si corregge")
    print("  cambiando il disegno pre-registrato.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
