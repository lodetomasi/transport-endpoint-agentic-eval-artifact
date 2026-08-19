#!/usr/bin/env python3
"""Il trasporto cambia COSA il modello recupera, o COME usa cio' che ha recuperato?

Il disegno confermativo misura la differenza fra i due trasporti. Non la spiega: un delta di
-10pp e' compatibile con due meccanismi opposti, e distinguerli e' la differenza fra misurare
un effetto e capirlo.

  A) INFORMAZIONE — col trasporto testuale il modello chiama meno tool, o li chiama peggio, e
     finisce con meno materiale. Il deficit e' di acquisizione.
  B) USO — i due trasporti acquisiscono lo stesso materiale, ma il formato in cui torna
     cambia quanto il modello ne cava. Il deficit e' di sfruttamento.

La decomposizione. Per ogni binario si legge cosa CIASCUN trasporto ha effettivamente
acquisito, e si rigioca quel materiale come **un solo prompt senza tool**, identico nei due
casi tranne che per il contenuto:

    replay(materiale del nativo)  -  replay(materiale del testuale)   =  componente A
    (differenza confermativa)     -  componente A                     =  componente B

Se A spiega quasi tutto, il trasporto e' un problema di recupero e si corregge dando piu'
turni. Se resta B, il formato stesso degrada l'uso, e non si corregge cosi'.

ESPLORATIVO per costruzione: prefisso `c2x_replay_`, in results/esplorativo/, fuori da ogni
famiglia congelata. Non entra nei dieci test e non muove nessuna soglia.

    python3 analysis/replay_trasporto.py --modello gpt-oss-120b --infra databricks [--limite N]
"""
import argparse
import csv
import json
import os
import statistics as st
import sys
import time
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent
sys.path[:0] = [str(RADICE / "src"), str(RADICE / "src" / "harness"), str(RADICE / "src" / "llm")]

from qualita_run import e_misurazione  # noqa: E402

# Gli id per endpoint: lo stesso modello si chiama diversamente sui due cloud, e il replay
# deve interrogare LO STESSO endpoint da cui la traiettoria e' venuta.
from raccogli_c2 import ROSTER  # noqa: E402

# Il braccio da rigiocare. Era fissato al confermativo.
PREFISSO = os.environ.get("C2_PREFISSO", "c2_")


def materiale(percorso: Path):
    """Cosa quella traiettoria ha davvero chiesto: funzioni, stringhe, turni.

    Si prende ogni `decompile_function` richiesta, non solo quelle andate a buon fine: dal
    log le due cose non si distinguono, ed e' la lettura piu' generosa verso il trasporto che
    ne ha chieste di piu'. Se il confronto appaiato regge comunque, la conclusione e' piu'
    forte.
    """
    funzioni, stringhe, turni = [], False, 0
    for riga in percorso.read_text(errors="ignore").splitlines():
        if not riga.strip():
            continue
        try:
            t = json.loads(riga)
        except json.JSONDecodeError:
            continue
        turni += 1
        for tc in t.get("tool_calls") or []:
            nome = tc.get("name") or ""
            if nome == "list_strings":
                stringhe = True
            elif nome == "decompile_function":
                arg = tc.get("arguments") or {}
                f = arg.get("name") if isinstance(arg, dict) else None
                if f and f not in funzioni:
                    funzioni.append(f)
    return funzioni, stringhe, turni


def traiettorie(modello, infra, trasporto):
    """Le traiettorie di una cella, sulla catena dei suffissi."""
    out = {}
    for suf in ("", "_redo", "_redo2", "_redo3"):
        d = (RADICE / "results" / "trajectories"
             / f"{PREFISSO}{modello}_{infra}_{trasporto}{suf}")
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.jsonl")):
            # <binario>_r<n>.jsonl
            stem = f.stem
            if "_r" not in stem:
                continue
            binario = stem.rsplit("_r", 1)[0]
            out.setdefault(binario, []).append(f)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modello", required=True)
    ap.add_argument("--infra", required=True, choices=["databricks", "bedrock"])
    ap.add_argument("--limite", type=int, default=None, help="solo i primi N binari, per provare")
    ap.add_argument("--dry-run", action="store_true",
                    help="stampa il materiale estratto e NON chiama nessun modello")
    a = ap.parse_args()

    nat = traiettorie(a.modello, a.infra, "native")
    tes = traiettorie(a.modello, a.infra, "text")
    comuni = sorted(set(nat) & set(tes))
    if not comuni:
        sys.exit(f"nessun binario con traiettorie in ENTRAMBI i trasporti per "
                 f"{a.modello}/{a.infra}. Il replay confronta cio' che i due hanno acquisito: "
                 f"senza entrambe le celle non esiste il confronto.")
    if a.limite:
        comuni = comuni[:a.limite]

    # --- quanto materiale ha acquisito ciascun trasporto -----------------------------
    print(f"  {len(comuni)} binari con entrambi i trasporti\n")
    print(f"  {'binario':34s}{'nativo':>18}{'testo':>18}")
    print(f"  {'':34s}{'fz  str  turni':>18}{'fz  str  turni':>18}")
    riepilogo = {"native": [], "text": []}
    dettaglio = []
    for b in comuni:
        riga = {"binario": b}
        for tr, fonte in (("native", nat), ("text", tes)):
            # una traiettoria per binario basta a caratterizzare il materiale della cella:
            # si prende la prima in ordine, che e' run 1, la stessa per i due trasporti
            fz, s, t = materiale(sorted(fonte[b])[0])
            riga[tr] = {"funzioni": fz, "stringhe": s, "turni": t}
            riepilogo[tr].append(len(fz))
        dettaglio.append(riga)
        print(f"  {b[:33]:34s}"
              f"{len(riga['native']['funzioni']):>4}{'  si' if riga['native']['stringhe'] else '  no'}"
              f"{riga['native']['turni']:>7}"
              f"{len(riga['text']['funzioni']):>8}{'  si' if riga['text']['stringhe'] else '  no'}"
              f"{riga['text']['turni']:>7}")

    print(f"\n  funzioni acquisite, mediana:  nativo {st.median(riepilogo['native']):.1f}   "
          f"testo {st.median(riepilogo['text']):.1f}")
    d = [len(x["text"]["funzioni"]) - len(x["native"]["funzioni"]) for x in dettaglio]
    print(f"  differenza per binario, media: {st.mean(d):+.2f} funzioni"
          + (f"  (SD {st.stdev(d):.2f})" if len(d) > 1 else ""))

    # Questa e' gia' una risposta parziale, e va letta prima di spendere: se i due trasporti
    # acquisiscono lo STESSO materiale, la componente A e' nulla per costruzione e il replay
    # non ha niente da separare -- l'intero effetto e' uso. Se differiscono molto, il replay
    # serve a dire QUANTO di quella differenza si traduce in pass-rate.
    if abs(st.mean(d)) < 0.5:
        print("\n  I due trasporti acquisiscono materiale equivalente: la componente di")
        print("  INFORMAZIONE e' gia' vicina a zero, e l'effetto misurato e' quasi tutto USO.")
    else:
        print(f"\n  I due trasporti acquisiscono materiale diverso ({st.mean(d):+.2f} funzioni).")
        print("  Il replay serve a dire quanta parte del delta di pass-rate viene da qui.")

    # IL NOME DELL'OUTPUT PORTA IL BRACCIO. Era fisso a «c2x_», mentre la LETTURA era gia'
    # parametrizzata sul prefisso: rigiocando la ri-raccolta lo script ha sovrascritto gli otto
    # file del braccio confermativo con i dati di un altro braccio, in silenzio e violando
    # l'append-only di results/. E' il difetto che questo progetto ha gia' documentato — «cartelle
    # distinte non bastano: il tag viene dal NOME» — ripetuto sull'output invece che sull'input.
    # La regola completa e' che OGNI percorso derivato dal braccio, in lettura e in scrittura,
    # deve derivarlo dallo stesso parametro.
    fuori = RADICE / "results" / "esplorativo"
    fuori.mkdir(parents=True, exist_ok=True)
    tag = "c2x" if PREFISSO == "c2_" else "c2x" + PREFISSO[2:].rstrip("_")
    p = fuori / f"{tag}_replay_materiale_{a.modello}_{a.infra}.json"
    if p.exists() and os.environ.get("C2_SOVRASCRIVI") != "1":
        raise SystemExit(
            f"  {p.name} esiste gia': results/ e' append-only (IR-5) e questo script non lo\n"
            "  sovrascrive. Se il dato va davvero rigenerato, e' una decisione da registrare:\n"
            "  C2_SOVRASCRIVI=1 la dichiara esplicitamente. Exit 2.")
    p.write_text(json.dumps(dettaglio, indent=1))
    print(f"\n  materiale estratto -> {p.relative_to(RADICE)}")

    if a.dry_run:
        print("  --dry-run: nessun modello chiamato.")
        return 0

    print("\n  La seconda meta' del replay -- rigiocare il materiale come prompt singolo --")
    print("  richiede il braccio monolitico, che questo capitolo non raccoglie. Si esegue")
    print("  quando la cella e' chiusa, con monolithic.run_monolithic sul materiale estratto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
