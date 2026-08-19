#!/usr/bin/env python3
"""I quattro controlli di SUCCESSIONE-09, scritti PRIMA della modifica che verificano.

Il progetto ha una regola su questo, nata da otto guardie scritte in un giorno e tutte provate
dopo: una guardia si prova prima, e nei due sensi. Il senso che manca piu' spesso e' il
secondo — senza di esso, una funzione che dichiara *tutto* incompleto passerebbe il primo
controllo e sembrerebbe corretta.

Cosa proteggono: `onus:harness-critic` ha verificato che la ri-raccolta scritta di getto
avrebbe (a) risposto «CHIUSA gia'» su tutte e sedici le celle spendendo zero con exit 0,
oppure (b) sovrascritto le 5.760 traiettorie della raccolta originale, perche' il tag della
workdir si deriva dallo STEM del file e non dal percorso.

UN TEST NON DEVE DIPENDERE DALLO STATO DELLA RACCOLTA. La prima versione asseriva che il
braccio `riraccolta` avesse 45 binari carenti «perche' la cartella e' vuota»: vero il giorno in
cui l'ho scritto, falso il giorno dopo, e il test e' diventato rosso mentre il codice era
giusto. Un test che scade e' peggio di nessun test, perche' insegna a ignorare il rosso. Ora la
proprieta' verificata e' quella stabile — `deficit` conta i file DEL BRACCIO CHE GLI SI CHIEDE —
e si verifica confrontandolo con i file che esistono davvero, qualunque essi siano.

    python3 test/test_bracci.py     oppure     python3 -m pytest test/
"""
import glob
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, os.path.join(RADICE, "src"))

import completa_celle as cc  # noqa: E402

CELLA = ("claude-haiku-4-5", "databricks", "native")
BRACCI = ("confermativo", "ablazione", "riraccolta", "esplorativo")


def test_deficit_guarda_il_braccio_giusto():
    """La proprieta' stabile: `deficit` conta nei file del braccio richiesto. Si verifica
    contro i file che esistono, non contro un numero che invecchia."""
    for braccio in ("confermativo", "riraccolta"):
        percorso = cc.percorso_cella(*CELLA, "", braccio=braccio)
        cartella = os.path.dirname(percorso)
        prefisso = os.path.basename(percorso).split("_")[0]
        esistono = bool(glob.glob(os.path.join(cartella, prefisso + "_*.csv")))
        _, manca = cc.deficit(*CELLA, braccio=braccio)
        if esistono:
            assert len(manca) < 45, (
                f"{braccio}: esistono file ma risultano carenti tutti i 45 binari — "
                "deficit sta guardando la cartella sbagliata")
        else:
            assert len(manca) == 45, (
                f"{braccio}: nessun file, ma risultano carenti solo {len(manca)} binari — "
                "deficit sta contando i file di un altro braccio")


def test_confermativo_resta_chiuso():
    """Il secondo senso, senza cui il primo non prova nulla: il braccio confermativo E'
    completo e deve continuare a risultarlo. Questo non invecchia — il confermativo e'
    append-only e chiuso da prima che esistesse questo test."""
    _, manca = cc.deficit(*CELLA, braccio="confermativo")
    assert not manca, f"il confermativo risulta carente su {len(manca)} binari: e' una regressione"


def test_percorsi_e_stem_distinti():
    """Distinti come PERCORSI non basta: il tag di workdir e traiettorie si deriva dallo
    STEM. Due bracci con lo stesso stem si sovrascrivono le traiettorie a vicenda."""
    perc = {b: cc.percorso_cella(*CELLA, "", braccio=b) for b in BRACCI}
    assert len(set(perc.values())) == len(BRACCI), f"percorsi non distinti: {perc}"
    stem = {b: os.path.splitext(os.path.basename(p))[0] for b, p in perc.items()}
    assert len(set(stem.values())) == len(BRACCI), \
        f"STEM non distinti — le traiettorie collidono: {stem}"


def test_braccio_ignoto_solleva():
    """Un valore sconosciuto non deve ricadere sul confermativo: e' il modo in cui un refuso
    manda una raccolta a sovrascrivere il braccio sbagliato."""
    try:
        cc.percorso_cella(*CELLA, "", braccio="confermativoo")
    except (ValueError, KeyError):
        return
    raise AssertionError("un braccio inesistente non ha sollevato: ricade su un default")


if __name__ == "__main__":
    print("SUCCESSIONE-09 — i quattro controlli, nei due sensi\n")
    falliti = []
    for nome, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_")):
        try:
            fn()
            print(f"  ok      {nome}")
        except AssertionError as e:
            falliti.append(nome)
            print(f"  FALLITO {nome}\n            {e}")
        except Exception as e:
            falliti.append(nome)
            print(f"  ERRORE  {nome}\n            {type(e).__name__}: {e}")
    print(f"\n  {4 - len(falliti)}/4 passati")
    sys.exit(1 if falliti else 0)
