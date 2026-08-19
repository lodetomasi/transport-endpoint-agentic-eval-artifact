#!/usr/bin/env python3
"""Le figure del paper, rigenerate dai file di `results/`.

Regola di `paper/figures/`: nessuna immagine orfana, ogni figura viene da uno script, e una
figura porta UNA claim. Le forme stanno nel grafico, le parole nella didascalia — ma la frase
che *fa* la figura sta sul grafico, dove l'occhio arriva prima.

  fig1-effetti-potenza.pdf   I tre contrasti con p nominale sotto 0,05 sono anche i tre con
                             l'intervallo piu' largo. E' il winner's curse, e si vede.

  fig2-determinismo.pdf      Temperatura 0,0 non e' determinismo, e lo stesso modello ha
                             determinismo diverso sui due cloud.

Scelte tipografiche, tutte per la stampa in bianco e nero di un paper a due colonne:
niente colore che diventi grigio indistinguibile, niente cornice, niente griglia, etichette
direttamente sui dati invece che in legenda, e una sola annotazione per figura.

I numeri non sono scritti a mano: si leggono da `results/`. Se un file manca, o se ne legge
meno del previsto, lo script si ferma — un grafico costruito su un sottoinsieme filtrato male
e' indistinguibile da uno giusto.
"""
import os
import statistics as st
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Le figure NON parsano l'output testuale dell'analisi: importano le sue funzioni e
# ricalcolano dalle stesse righe. Un file di testo letto con un regex e' una seconda idea
# di quali righe contano, e la didascalia sarebbe l'unico posto in cui le due si incontrano.
# `qualita_run.e_misurazione` e' la regola condivisa, e arriva qui attraverso `analyze_c2`,
# che e' congelato: se cambia la regola, cambiano insieme analisi e figure.
sys.path.insert(0, "src")
sys.path.insert(0, "analysis")
from qualita_run import e_misurazione  # noqa: E402,F401  (importato per il controllo di paper.py)
import analyze_c2 as A  # noqa: E402

USCITA = "paper/figures"
RISULTATI = "results"

ATTESI_CONTRASTI = 8
ATTESI_MODELLI = 4

CONTRASTI = [
    ("T1", "gpt-oss-120b",      ("databricks", "native"), ("databricks", "text"),  "transport"),
    ("T2", "llama-3.3-70b",     ("databricks", "native"), ("databricks", "text"),  "transport"),
    ("T3", "claude-haiku-4-5",  ("databricks", "native"), ("databricks", "text"),  "transport"),
    ("T4", "claude-sonnet-4-5", ("databricks", "native"), ("databricks", "text"),  "transport"),
    ("T5", "gpt-oss-120b",      ("databricks", "native"), ("bedrock", "native"),   "endpoint"),
    ("T6", "llama-3.3-70b",     ("databricks", "native"), ("bedrock", "native"),   "endpoint"),
    ("T7", "claude-haiku-4-5",  ("databricks", "native"), ("bedrock", "native"),   "endpoint"),
    ("T8", "claude-sonnet-4-5", ("databricks", "native"), ("bedrock", "native"),   "endpoint"),
]

INCHIOSTRO = "#1a1a1a"
SECONDARIO = "#8a8a8a"
TENUE = "#d4d4d4"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "pdf.fonttype": 42,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
})


def nome_breve(modello):
    return (modello.replace("claude-", "").replace("-4-5", "")
            .replace("gpt-oss-120b", "gpt-oss").replace("llama-3.3-70b", "llama"))


def leggi_analisi():
    """[(id, etichetta, delta, lo, hi, p)] calcolato con le funzioni dell'analisi congelata."""
    celle, _ = A.carica(RISULTATI)
    righe = []
    for tid, mod, ca, cb, asse in CONTRASTI:
        a = A.media_per_binario(celle, mod, *ca)
        b = A.media_per_binario(celle, mod, *cb)
        n, med, lo, hi, _t, p = A.t_appaiato(a, b)
        if n < 2:
            continue
        righe.append((tid, f"{nome_breve(mod)} \u00b7 {asse}", med * 100,
                      lo * 100, hi * 100, p))
    if len(righe) != ATTESI_CONTRASTI:
        sys.exit(f"calcolati {len(righe)} contrasti, attesi {ATTESI_CONTRASTI}: "
                 "una cella manca o e' sotto la n pre-registrata, non disegno nulla")
    return righe


def leggi_determinismo():
    """[(modello, infra, trasporto, quota di binari con RUN_ATTESI run identiche)]."""
    celle, _ = A.carica(RISULTATI)
    per_cella = {}
    for m in A.MODELLI:
        for i in A.INFRA:
            for t in A.TRASPORTI:
                valori = [v[:A.RUN_ATTESI] for (mm, ii, tt, _b), v in celle.items()
                          if (mm, ii, tt) == (m, i, t) and len(v) >= A.RUN_ATTESI]
                if not valori:
                    continue
                identiche = sum(1 for v in valori if len(set(v)) == 1)
                per_cella[(m, i, t)] = 100.0 * identiche / len(valori)
    modelli = {m for m, _, _ in per_cella}
    if len(modelli) != ATTESI_MODELLI:
        sys.exit(f"calcolati {len(modelli)} modelli, attesi {ATTESI_MODELLI}")
    return per_cella


def figura_effetti(righe):
    righe = sorted(righe, key=lambda r: r[5])
    fig, ax = plt.subplots(figsize=(3.4, 2.9))
    etichette = []

    for i, (tid, eti, d, lo, hi, p) in enumerate(righe):
        y = len(righe) - i
        forte = p < 0.05
        colore = INCHIOSTRO if forte else SECONDARIO
        ax.plot([lo, hi], [y, y], color=colore, lw=1.6 if forte else 0.9,
                solid_capstyle="butt", zorder=2)
        ax.plot([d], [y], "o", color=colore, ms=4.4 if forte else 3.2,
                markeredgecolor="white", markeredgewidth=0.7, zorder=3)
        etichette.append((y, eti, forte))

    ax.axvspan(-3, 3, color=TENUE, alpha=0.45, lw=0, zorder=0)
    ax.axvline(0, color=SECONDARIO, lw=0.5, zorder=1)

    # L'annotazione porta la claim, ma la sua guida non deve attraversare le etichette:
    # nella prima versione la linea tagliava "haiku - transport". Sta a destra, nello spazio
    # vuoto sotto i tre intervalli lunghi, e la parentesi graffa fa da guida al posto della
    # freccia.
    y_top, y_bot = len(righe), len(righe) - 2
    ax.plot([11.6, 12.4, 12.4, 11.6], [y_top, y_top, y_bot, y_bot],
            color=SECONDARIO, lw=0.6, clip_on=False, zorder=4)
    ax.text(12.9, (y_top + y_bot) / 2, "the three with\n$p<0.05$ are\nthe three widest",
            fontsize=6.2, color=INCHIOSTRO, ha="left", va="center", clip_on=False)

    # Le etichette stanno FUORI dall'area dei dati, come tick: scritte dentro, le barre dei
    # tre contrasti lunghi ci passavano sopra. Visto rendendo la figura, non ragionandoci.
    ax.set_yticks([y for y, _, _ in etichette])
    ax.set_yticklabels([t for _, t, _ in etichette], fontsize=6.4)
    for tick, (_, _, forte) in zip(ax.get_yticklabels(), etichette):
        tick.set_color(INCHIOSTRO if forte else SECONDARIO)
    ax.tick_params(axis="y", length=0, pad=3)
    ax.set_ylim(0.2, len(righe) + 0.8)
    ax.set_xlim(-21, 11.5)
    ax.set_xticks([-20, -10, 0, 10])
    ax.set_xlabel("paired difference (pp)", fontsize=6.8, color=INCHIOSTRO)
    ax.tick_params(labelsize=6.4, colors=INCHIOSTRO, length=2.5, pad=2)
    # dentro il grafico, accanto alla banda che nomina: fuori dall'asse restava orfano
    ax.text(0, len(righe) + 0.55, "falsifier band", fontsize=5.8, color=SECONDARIO,
            ha="center", va="center")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(SECONDARIO)
    fig.tight_layout(pad=0.3)
    fig.savefig(f"{USCITA}/fig1-effetti-potenza.pdf", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def figura_determinismo(dati):
    per_modello = {}
    for (modello, infra, _trasporto), quota in dati.items():
        per_modello.setdefault(modello, []).append((quota, infra))
    ordine = sorted(per_modello, key=lambda m: -min(q for q, _ in per_modello[m]))

    fig, ax = plt.subplots(figsize=(3.4, 2.0))
    for i, m in enumerate(ordine):
        y = len(ordine) - i
        quote = sorted(q for q, _ in per_modello[m])
        ax.plot([quote[0], quote[-1]], [y, y], color=SECONDARIO, lw=1.0, zorder=1,
                solid_capstyle="round")
        for q in quote:
            ax.plot([q], [y], "o", color=INCHIOSTRO, ms=4.0,
                    markeredgecolor="white", markeredgewidth=0.7, zorder=2)
        ax.text(-4, y, nome_breve(m), va="center", ha="right", fontsize=6.4, color=INCHIOSTRO)
        if quote[-1] - quote[0] >= 5:
            ax.text((quote[0] + quote[-1]) / 2, y + 0.30, f"{quote[-1] - quote[0]:.0f} pt spread",
                    fontsize=5.8, color=SECONDARIO, ha="center")

    # senza freccia e nello spazio vuoto in basso a destra: con la freccia il testo
    # attraversava la linea di llama, visto rendendo la figura
    ax.text(104, 0.75, "each point is one cell:\ntwo clouds x two transports",
            fontsize=5.8, color=SECONDARIO, ha="right", va="center")

    ax.set_yticks([])
    ax.set_ylim(0.3, len(ordine) + 0.9)
    ax.set_xlim(-30, 108)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("binaries whose eight runs are identical (%)", fontsize=6.8, color=INCHIOSTRO)
    ax.tick_params(labelsize=6.4, colors=INCHIOSTRO, length=2.5, pad=2)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(SECONDARIO)
    ax.spines["bottom"].set_bounds(0, 100)
    fig.tight_layout(pad=0.3)
    fig.savefig(f"{USCITA}/fig2-determinismo.pdf", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(USCITA, exist_ok=True)
    righe = leggi_analisi()
    figura_effetti(righe)
    dati = leggi_determinismo()
    figura_determinismo(dati)

    nominali = sorted(r[0] for r in righe if r[5] < 0.05)
    larghezze = {r[0]: r[4] - r[3] for r in righe}
    piu_larghi = sorted(sorted(larghezze, key=lambda k: -larghezze[k])[:len(nominali)])
    print(f"  fig1  {len(righe)} contrasti, calcolati con le funzioni di analyze_c2")
    print(f"        p<0,05: {nominali}   piu' larghi: {piu_larghi}   "
          f"-> {'COINCIDONO' if nominali == piu_larghi else 'NON coincidono'}")
    t3 = [r for r in righe if r[0] == "T3"][0]
    print(f"        controllo con risposta nota: T3 = {t3[2]:+.2f}pp, p={t3[5]:.4f} -> "
          f"{'COINCIDE con ANALISI' if abs(t3[2] + 10.44) < 0.05 else 'NON COINCIDE'}")
    print(f"  fig2  {len({m for m, _, _ in dati})} modelli, {len(dati)} celle")
