#!/usr/bin/env python3
"""Coerenza fra cio' che il paper cita e cio' che la bibliografia definisce.

Due direzioni, e nessuna delle due e' innocua:

  - definita ma mai citata -> la voce non raggiunge il PDF, e una passata di verifica delle
    citazioni la conta come verificata mentre il lettore non la vede mai. E' successo:
    `he2025nondeterminism` e' rimasta orfana per un'intera passata perche' la sostituzione nel
    testo non aveva preso, e la bibliografia sembrava a posto.
  - citata ma non definita -> LaTeX stampa [?] e la compilazione riesce lo stesso.

Controlla inoltre che nessun campo `note` stampato contenga italiano. Non e' una questione di
stile: in una sottomissione a doppio anonimato la lingua di lavoro dell'autore e' un
identificatore, e i campi `note` finiscono nel PDF mentre i commenti `%` no.

Esce 1 se qualcosa non torna, cosi' che valga in una catena di build.
"""
import glob
import re
import sys

SEZIONI = "paper/sections/*.tex"
BIB = "paper/references.bib"

# Parole che compaiono in italiano e non in una nota bibliografica inglese. Il controllo e'
# volutamente grossolano: un falso positivo costa una rilettura, un falso negativo costa
# l'anonimato.
ITALIANO = re.compile(
    r"\b(consultat\w*|verificat\w*|modalita|variazioni|tratta|nomina|asimmetria|"
    r"riga|righe|pagina|fonda|sostiene|conferma|contro|delle|della|nella|questo|"
    r"perche|percio|senza|anche)\b", re.I)


def citate():
    out = set()
    for f in glob.glob(SEZIONI):
        for m in re.findall(r'\\cite[tp]?\{([^}]*)\}', open(f, errors="ignore").read()):
            out |= {k.strip() for k in m.split(",") if k.strip()}
    return out


def definite():
    return set(re.findall(r'^@\w+\{([^,]+),', open(BIB, errors="ignore").read(), re.M))


def note_stampate():
    """I campi note veri: quelli commentati con % non raggiungono il PDF."""
    s = "\n".join(r for r in open(BIB, errors="ignore").read().split("\n")
                  if not r.lstrip().startswith("%"))
    return [m.group(1) for m in re.finditer(r'^[ \t]*note\s*=\s*\{(.+?)\},?[ \t]*$',
                                            s, re.M | re.S)]


if __name__ == "__main__":
    c, d = citate(), definite()
    orfane, mancanti = sorted(d - c), sorted(c - d)
    sporche = [n for n in note_stampate() if ITALIANO.search(n)]

    print(f"  citate {len(c)}  definite {len(d)}")
    print(f"  definite ma mai citate : {', '.join(orfane) if orfane else 'nessuna'}")
    print(f"  citate ma non definite : {', '.join(mancanti) if mancanti else 'nessuna'}")
    print(f"  note stampate          : {len(note_stampate())}, "
          f"con testo italiano: {len(sporche)}")
    for n in sporche:
        print(f"    -> {' '.join(n.split())[:88]}")

    # Il caso di cui si conosce gia' la risposta: una chiave inventata deve risultare mancante.
    finta = "chiave_che_non_esiste_mai"
    assert finta not in d, "il controllo negativo e' diventato un nome reale: cambiarlo"

    if orfane or mancanti or sporche:
        sys.exit(1)
    print("\n  Coerente in entrambe le direzioni, e nessuna nota stampata in italiano.")
