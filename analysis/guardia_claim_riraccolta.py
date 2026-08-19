#!/usr/bin/env python3
"""Il paper non deve dichiarare la ri-raccolta completata finche' non lo e'.

PERCHE' ESISTE. L'abstract ha contenuto per alcune ore la frase «we isolated the workspaces and
re-collected all sixteen cells independently» mentre la raccolta era all'1,6%. Un'affermazione
al passato per un'azione in corso: nessuno l'aveva scritta in malafede, era il testo definitivo
messo in anticipo perche' «tanto poi sara' vero». E' il difetto che questo capitolo esiste per
non commettere, e un revisore che chiedesse i numeri non troverebbe niente.

La regola del progetto e' sostituire un'affermazione con un controllo che la esegue. Questo e'
il controllo: confronta cio' che il paper DICE della ri-raccolta con cio' che i file
DIMOSTRANO, ed esce 1 se il testo promette piu' dei dati.

    python3 analysis/guardia_claim_riraccolta.py
    python3 analysis/guardia_claim_riraccolta.py --autotest
"""
import argparse
import csv
import glob
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, os.path.join(RADICE, "src"))
from qualita_run import e_misurazione  # noqa: E402

ATTESE = 5760          # 16 celle x 45 binari x 8 run
CELLE_ATTESE = 16

# Frasi che affermano un'azione COMPIUTA. Il presente progressivo («is being collected») e il
# futuro non compaiono qui: dichiarano un'intenzione, che e' vera anche a raccolta aperta.
COMPIUTE = [
    r"re-collected all sixteen cells",
    r"the sixteen cells were collected again",
    r"were re-collected",
    r"has been re-collected",
    r"we re-collected",
    r"reported beside an independent re-collection",
    r"the re-collection (?:confirms|shows|reproduces|found|establishes)",
    # Aggiunti dopo aver scritto l'esito: la guardia contava zero frasi mentre il paper ne
    # conteneva quattro, perche' cercava formulazioni che nessuno aveva usato. Una guardia che
    # non intercetta la frase che il testo scrive davvero non protegge nulla.
    r"was collected again",
    r"the four frozen criteria.{0,40}outcome",
    r"all four are met",
    r"in the re-collection",
]


def stato_riraccolta(radice=None):
    """(misurazioni valide, celle con almeno una riga). La sottocartella smoke/ non conta:
    e' collaudo, e sta apposta dove il glob non ricorsivo non la vede."""
    base = radice or os.path.join(RADICE, "results", "riraccolta")
    n, celle = 0, set()
    for f in sorted(glob.glob(os.path.join(base, "*.csv"))):
        righe = sum(1 for r in csv.DictReader(open(f, errors="ignore")) if e_misurazione(r))
        if righe:
            # UNA CELLA, NON UN FILE. Contava i file e dichiarava «31/16 celle»: la catena dei
            # suffissi (''/_redo/_redo2/_redo3) da' fino a quattro file per cella, quindi
            # sedici file possono essere otto celle. Il verdetto «COMPLETA» sarebbe passato su
            # meta' del disegno. E' lo stesso difetto gia' corretto in stato.sh, ricomparso qui
            # perche' corretto in un posto invece che nella definizione.
            base_nome = os.path.basename(f)[:-4]
            for suf in ("_redo3", "_redo2", "_redo"):
                if base_nome.endswith(suf):
                    base_nome = base_nome[: -len(suf)]
                    break
            celle.add(base_nome)
        n += righe
    return n, len(celle)


def frasi_compiute(cartella=None):
    """Le occorrenze di un'affermazione al passato, fuori dai commenti LaTeX."""
    base = cartella or os.path.join(RADICE, "paper", "sections")
    trovate = []
    for f in sorted(glob.glob(os.path.join(base, "*.tex"))):
        for i, riga in enumerate(open(f, errors="ignore"), 1):
            if riga.lstrip().startswith("%"):
                continue
            testo = re.sub(r"(?<!\\)%.*$", "", riga)      # commento a fine riga
            for pat in COMPIUTE:
                if re.search(pat, testo, re.I):
                    trovate.append((os.path.basename(f), i, " ".join(testo.split())[:96]))
    return trovate


def verdetto(n, celle, trovate):
    completa = n >= ATTESE and celle >= CELLE_ATTESE
    return completa, (bool(trovate) and not completa)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--autotest", action="store_true")
    a = ap.parse_args()

    if a.autotest:
        # I due sensi. Senza il secondo, una guardia che vieta SEMPRE la frase passerebbe il
        # primo e bloccherebbe il paper anche a raccolta finita.
        assert verdetto(100, 1, [("x", 1, "we re-collected")])[1] is True, \
            "non blocca una frase compiuta a raccolta incompleta"
        assert verdetto(ATTESE, CELLE_ATTESE, [("x", 1, "we re-collected")])[1] is False, \
            "blocca la frase anche a raccolta completa"
        assert verdetto(100, 1, [])[1] is False, "blocca in assenza di frasi"
        # e il presente progressivo non deve mai essere intercettato
        assert not any(re.search(p, "the experiment is being collected again", re.I)
                       for p in COMPIUTE), "intercetta un'intenzione invece di un'azione"
        # Il caso che il conteggio per file sbagliava: sedici file che sono otto celle.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            intestazione = "modello,infra,trasporto,binary_id,run_id,pass_rate,esito\n"
            riga = "m,databricks,native,prog01,r1,1.0,ok\n"
            for i in range(8):
                for suf in ("", "_redo"):
                    with open(os.path.join(d, f"c2r_m{i}_databricks_native{suf}.csv"), "w") as fh:
                        fh.write(intestazione + riga)
            _, celle_viste = stato_riraccolta(d)
            assert celle_viste == 8, \
                f"sedici file di otto celle contati come {celle_viste}: la catena dei suffissi"
        print("  autotest: 5 controlli, tutti passati")
        sys.exit(0)

    n, celle = stato_riraccolta()
    trovate = frasi_compiute()
    completa, viola = verdetto(n, celle, trovate)

    print(f"  ri-raccolta: {n}/{ATTESE} misurazioni in {celle}/{CELLE_ATTESE} celle "
          f"-> {'COMPLETA' if completa else 'IN CORSO'}")
    print(f"  frasi che la dichiarano compiuta: {len(trovate)}")
    for f, i, t in trovate:
        print(f"    {f}:{i}  {t}")

    if viola:
        print("\n  Il paper dichiara compiuta una raccolta che non lo e'. Le frasi sopra vanno")
        print("  riportate al presente, oppure si aspetta che la raccolta chiuda. Il testo")
        print("  definitivo, con i quattro criteri, sta in registro/EMENDAMENTO-06.")
        sys.exit(1)

    if completa and not trovate:
        print("\n  La raccolta e' chiusa e il paper non la usa ancora: manca l'esito dei quattro")
        print("  criteri e la tabella originale/ri-raccolta.")
    elif completa:
        print(f"\n  Coerente: {len(trovate)} affermazioni compiute su una raccolta chiusa a "
              f"{n} misurazioni in {celle} celle.")
    else:
        print("\n  Coerente: il paper non promette piu' di quanto i file dimostrino.")
