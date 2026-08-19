"""Braccio best-of-N parallelo, diversity-matched.

Terzo braccio del confronto a 3 vie richiesto dal dialectic. Serve a distinguere due
claim diverse:
  - "l'iterazione sequenziale non aiuta"           (mono vs sequenziale)
  - "piu' calcolo non aiuta, in nessuna forma"     (mono vs sequenziale vs parallelo)

DIVERSITY-MATCHED (correzione imposta dal dialectic, attacco #2 dell'adversary): i
campioni NON usano la stessa temperatura del braccio sequenziale — sarebbero correlati e
il baseline risulterebbe debole per costruzione, misurando la scelta di temperatura
invece della strategia. Qui la temperatura varia tra i campioni.

SELEZIONE — la parte che va dichiarata, perche' cambia cosa si sta misurando:
in produzione non si sa quale candidato sia corretto. Registriamo quindi DUE quantita'
distinte, entrambe riportate, mai confuse:
  - `oracle_best`: pass-rate del candidato migliore, scelto guardando i test.
    E' un LIMITE SUPERIORE irrealizzabile in pratica = la "copertura" nel senso di
    Large Language Monkeys (arXiv:2407.21787).
  - `mean`: pass-rate media dei candidati = cosa si otterrebbe scegliendo a caso.
Il divario tra i due e' il costo della selezione, cioe' esattamente la dicotomia
selezione/copertura che S1 vuole misurare.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from monolithic import run_monolithic  # noqa: E402

# Temperature diverse per campione: garantisce diversita' reale tra i candidati.
# Ciclata se n_samples supera la lunghezza della lista.
TEMPERATURE_LADDER = [0.0, 0.3, 0.6, 0.9, 1.0, 0.2, 0.7, 0.5, 1.0, 0.4, 0.8, 0.1]


def run_best_of_n(
    binary_id: str,
    n_samples: int,
    model: str,
    provider: str,
    max_tokens: int,
    ghidra_client,
):
    """Esegue n_samples tentativi monolitici indipendenti a temperature diverse.

    Ritorna (lista di AgentResult, costo totale). La valutazione dei candidati e la
    scelta tra oracle_best e mean spetta al chiamante (run_minipilot), che ha accesso
    ai test.
    """
    results = []
    for i in range(n_samples):
        temp = TEMPERATURE_LADDER[i % len(TEMPERATURE_LADDER)]
        r = run_monolithic(
            binary_id=binary_id, model=model, provider=provider,
            max_tokens=max_tokens, temperature=temp, ghidra_client=ghidra_client,
        )
        results.append((temp, r))
    return results
