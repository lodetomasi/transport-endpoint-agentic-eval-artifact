#!/usr/bin/env python3
"""L'unico posto dove si decide se una riga di `results/` e' una misurazione.

Questo modulo esiste per una ragione documentata nel paper (difetto (g)): il campo
`infra_failure` veniva scritto dall'harness e letto da nessuno dei tre script di analisi,
ne' dalla generazione delle figure. Quattro pipeline leggevano gli stessi CSV con quattro
regole diverse, e i numeri divergevano senza che nulla lo segnalasse.

La regola sta qui, una volta. Chi legge `results/` importa `e_misurazione`. Aggiungere un
nuovo criterio significa modificare questo file, e allora vale per tutti i consumatori
insieme -- che e' l'unico modo in cui una guardia e' davvero una guardia.

Due criteri, entrambi trovati sul campo:

1. `infra_failure=True` -- l'harness ha marcato la riga: completion troncata, eccezione
   durante la chiamata, tariffa non dichiarata.

2. `harness_error` nel campo `error` -- 62 righe in tutto lo studio, tutte
   `IndexError: list index out of range`, e **nessuna marcata**. E' un crash del nostro
   codice scritto come riga di risultato con `pass_rate=0`: la stessa forma del difetto (a),
   trovata dal lato che il flag non copriva. Un crash dell'harness non e' un fallimento del
   modello, e contarlo come tale sposta le stime verso il basso in modo non uniforme fra i
   bracci.
"""
from __future__ import annotations


def e_misurazione(riga: dict) -> bool:
    """True se la riga e' un tentativo genuino del modello, non un guasto dell'apparato."""
    if str(riga.get("infra_failure", "")).strip().lower() in ("true", "1"):
        return False
    if "harness_error" in (riga.get("error") or ""):
        return False
    return True


SUFFISSI_RIESECUZIONE = ("", "_redo", "_redo2", "_redo3")
"""Ordine di concatenazione delle ri-esecuzioni di una cella.

Esiste perche' la regola su cosa sia una misurazione e' cambiata due volte -- prima
escludendo `infra_failure`, poi i crash `harness_error` -- e ogni giro ha fatto scendere
alcune celle sotto la n pre-registrata, ricompletate in un file nuovo (`results/` e'
append-only, IR-5). Le ri-esecuzioni **completano** la cella, non la sostituiscono: si
concatenano nell'ordine in cui sono avvenute e si tengono i primi n.

Aggiungere un suffisso qui lo rende visibile a tutti i consumatori insieme. Quando questa
tupla viveva in due copie, l'analisi leggeva `_redo2` e le figure no, e la fig. 3
etichettava 0,706 dove il testo diceva 0,714 -- colto dalla guardia di coerenza, non da un
occhio umano.
"""


def celle_con_riesecuzioni(lettore, nome: str, n: int) -> dict:
    """Cella per binario, unendo le ri-esecuzioni e tenendo i primi n run validi.

    `lettore` e' una funzione nome_file -> {binary_id: [pass_rate, ...]}, cosi' questo
    modulo non impone come si legge un CSV, solo in che ordine si uniscono i file.
    """
    base: dict = {}
    for suff in SUFFISSI_RIESECUZIONE:
        for k, v in (lettore(f"{nome}{suff}.csv") or {}).items():
            base[k] = base.get(k, []) + v
    return {k: v[:n] for k, v in base.items() if len(v) >= n}


def motivo_scarto(riga: dict) -> str | None:
    """Perche' la riga e' stata scartata, per i log e per le note di validita'."""
    if str(riga.get("infra_failure", "")).strip().lower() in ("true", "1"):
        return "infra_failure marcato dall'harness"
    if "harness_error" in (riga.get("error") or ""):
        return "crash dell'harness scritto come risultato"
    return None
