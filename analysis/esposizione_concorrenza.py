#!/usr/bin/env python3
"""Le due misure di esposizione alla concorrenza, che non sono la stessa cosa.

Il paper riporta due numeri sulla directory di lavoro condivisa, e finora nessuno script li
produceva entrambi: il seggio di riproducibilita' ha tracciato «843 di 5.805» e ha trovato uno
script che, per la stessa domanda, rispondeva 30. Aveva ragione a segnalarlo, e la ragione e'
che le domande erano due:

  A. CONCORRENZA — quante misurazioni hanno una riga di un'ALTRA CELLA entro due secondi,
     su qualunque binario. Misura quanto la raccolta fosse affollata. NON e' la precondizione
     di una collisione: due celle che lavorano su binari diversi non condividono la directory.

  B. PRECONDIZIONE — quante avrebbero compilato nella STESSA DIRECTORY. Non e' «stesso
     binario e stessa run»: e' «stesso PERCORSO di workdir», e i due criteri coincidono solo
     prima della correzione, quando il percorso era `workv3/<prog>_r<run>` e non conteneva la
     cella. Dopo la correzione il percorso e' `workv3/<cella>/<prog>_r<run>` e due celle
     diverse non collidono mai, per costruzione.

     Ci sono ricascato: la prima versione di questo script applicava alla ri-raccolta il
     criterio della raccolta vecchia e segnalava una collisione fra due celle che scrivevano
     in due directory distinte. E' lo stesso errore, in forma diversa, che avevo gia' fatto
     nel controllo di isolamento — guardare la chiave logica invece del percorso reale.

A e' un ordine di grandezza sopra B, e riportare solo A sovrastima la minaccia mentre riportare
solo B nasconde quanto la raccolta fosse concorrente. Il paper li tiene entrambi; questo script
li produce entrambi, con la definizione accanto, cosi' che un lettore sappia quale sta leggendo.

ATTENZIONE AL MODO DI CONTARE. Per B si cerca all'indietro nella finestra dei due secondi e ci
si ferma alla prima riga che soddisfa la condizione. Fermarsi invece alla prima riga di
un'altra cella QUALUNQUE — che e' l'errore che ho commesso calcolandolo a mano — restituisce
22 invece di 30, perche' una riga vicina di un'altra cella su un binario diverso interrompe la
ricerca prima di trovare quella che conta.
"""
import csv
import glob
import os
import sys
from datetime import datetime

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, os.path.join(RADICE, "src"))
from qualita_run import e_misurazione  # noqa: E402

FINESTRA = 2.0   # secondi


def eventi(pattern):
    ev = []
    for f in glob.glob(os.path.join(RADICE, pattern)):
        cella = os.path.basename(f)[:-4]
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                if not e_misurazione(r):
                    continue
                v = (r.get("timestamp") or "")[:26]
                for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
                    try:
                        ev.append((datetime.strptime(v, fmt), cella,
                                   r.get("binary_id", ""), r.get("run_id", "")))
                        break
                    except ValueError:
                        pass
    ev.sort()
    return ev


def workdir(cella, binario, run, con_tag):
    """Il percorso in cui la run compila. `con_tag=False` riproduce l'apparato originale,
    dove la cella NON entrava nel percorso ed era la causa del problema."""
    return (f"workv3/{cella}/{binario}_r{run}" if con_tag
            else f"workv3/{binario}_r{run}")


def conta(ev, con_tag):
    """(A concorrenza, B precondizione). A guarda le celle, B guarda i PERCORSI."""
    a = b = 0
    for i, (t, c, bi, ru) in enumerate(ev):
        mio = workdir(c, bi, ru, con_tag)
        for j in range(i - 1, -1, -1):
            if (t - ev[j][0]).total_seconds() > FINESTRA:
                break
            if ev[j][1] != c:
                a += 1
                break
        for j in range(i - 1, -1, -1):
            if (t - ev[j][0]).total_seconds() > FINESTRA:
                break
            if ev[j][1] != c and workdir(ev[j][1], ev[j][2], ev[j][3], con_tag) == mio:
                b += 1
                break
    return a, b


if __name__ == "__main__":
    for eti, pat, con_tag in (("raccolta originale (workdir senza cella)", "results/c2_*.csv", False),
                              ("ri-raccolta (workdir con cella)", "results/riraccolta/c2r_*.csv", True)):
        ev = eventi(pat)
        if not ev:
            print(f"  {eti}: nessuna misurazione")
            continue
        a, b = conta(ev, con_tag)
        n = len(ev)
        print(f"\n  {eti}: {n} misurazioni")
        print(f"    A. con un'altra cella entro {FINESTRA:.0f}s (qualunque binario) : "
              f"{a} ({100*a/n:.1f}%)   <- affollamento")
        print(f"    B. ... che avrebbero compilato nello STESSO PERCORSO        : "
              f"{b} ({100*b/n:.2f}%)   <- precondizione della collisione")

    print("\n  Il numero che il paper usa per delimitare la minaccia e' B, non A: due celle")
    print("  che lavorano nello stesso secondo su binari diversi non condividono la directory.")
    print("  A dice quanto la raccolta fosse concorrente, ed e' riportato per questo.")

    # Il controllo di cui si conosce gia' la risposta: sulla ri-raccolta, dove il percorso
    # porta il tag della cella, B deve essere zero anche se A resta alto.
    ev = eventi("results/riraccolta/c2r_*.csv")
    if ev:
        a, b = conta(ev, True)
        if b:
            sys.exit(f"\n  ATTESO ZERO, TROVATO {b}: la ri-raccolta ha coppie sulla stessa "
                     "workdir. La correzione non tiene, fermare.")
        print(f"\n  Controllo: sulla ri-raccolta B={b} con A={a} — le celle si sovrappongono")
        print("  nel tempo ma non nello spazio, che e' esattamente cio' che la correzione fa.")
