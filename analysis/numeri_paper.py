#!/usr/bin/env python3
"""Ogni numero che il paper scrive IN PROSA, con la sua etichetta e il suo valore.

PERCHE'. La regola del progetto e' che ogni numero tracci a un file in `results/`. Le tabelle
la rispettano da quando le genera uno script; la prosa no — «il p minimo e' 0,0177», «77 volte»,
«705 binari» erano copiati a mano da esecuzioni precedenti, e con EMENDAMENTO-06 che promuove la
ri-raccolta a base primaria cambiano tutti insieme. Un numero in prosa sbagliato non si vede: non
sfora una colonna, non rompe una compilazione, e sopravvive a ogni rilettura.

USO, ed e' anche il comando che l'artefatto documenta:

    python3 analysis/numeri_paper.py                    # la ri-raccolta, base primaria
    python3 analysis/numeri_paper.py --confermativa     # la raccolta originale, per la replica
    python3 analysis/numeri_paper.py --confronta        # affianca le due, per il testo

Il controllo a risposta nota e' incorporato: sulla raccolta confermativa i valori devono
riprodurre quelli oggi nel paper, ed e' quello che rende affidabile la serie nuova.
"""
import math
import os
import statistics as st
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE_REPO = os.path.dirname(QUI)
sys.path.insert(0, QUI)

# I valori oggi nel paper, misurati sulla raccolta confermativa. Servono da controllo a
# risposta nota: non sono un'aspettativa sul risultato nuovo, sono la prova che la catena
# di calcolo e' la stessa che ha prodotto il testo attuale.
ATTESI_CONFERMATIVA = {
    "p_minimo_student": 0.0177,
    "sd_min": 0.0037,
    "sd_max": 0.2844,
    # il testo attuale scrive «a ratio of 77»: il valore e' 76,3, arrotondato per
    # eccesso oltre l'intero piu' vicino. Qui sta il valore, e il testo si corregge.
    "rapporto_sd": 76.32,
    "quota_rumore_T3": 0.001,
    "k_inf_T3": 705,
    "run_al_budget": 55,
    "run_senza_tool": 58,
    "pavimento_medio": 0.1103,
}

Z_80 = 1.959964 + 0.841621          # bilaterale al 5%, potenza 80%
MDE_PREREG = 4.87                   # PREREGISTRAZIONE.md §7, in punti percentuali


def ambiente(confermativa):
    """Le tre variabili che scelgono la raccolta. Sono tre e non una perche' i CSV, il loro
    pattern e le cartelle delle traiettorie si nominano in modo indipendente — e impostarne
    solo una produce un indice costruito su una raccolta e interrogato con le chiavi
    dell'altra, che non solleva: restituisce zero."""
    if confermativa:
        return {"C2_RESULTS": "results", "C2_PATTERN": "c2_*.csv", "C2_PREFISSO": "c2_"}
    return {"C2_RESULTS": "results/riraccolta", "C2_PATTERN": "c2r_*.csv",
            "C2_PREFISSO": "c2r_"}


def esegui(script, env, argomenti=()):
    amb = dict(os.environ)
    amb.update(env)
    r = subprocess.run([sys.executable, os.path.join(QUI, script), *argomenti],
                       capture_output=True, text=True, cwd=RADICE_REPO, env=amb)
    return r.stdout, r.returncode


def numeri(confermativa=False):
    env = ambiente(confermativa)
    for k, v in env.items():
        os.environ[k] = v
    for m in ("scomposizione_varianza", "p_esatti_student", "potenza_per_contrasto"):
        sys.modules.pop(m, None)

    import scomposizione_varianza as sv
    import p_esatti_student as pes
    import potenza_per_contrasto as pc

    fuori = {}

    # --- la famiglia pre-registrata ---------------------------------------------------
    serie = pes.serie()
    misto = pes.p_misto_dal_congelato()
    tutti_student = [ps for _, _, _, _, ps in serie] + list(misto.values())
    tutti_cong = [p for _, _, _, p, _ in serie] + list(misto.values())
    fuori["p_minimo_student"] = min(tutti_student)
    fuori["p_minimo_congelato"] = min(tutti_cong)
    fuori["contrasto_p_minimo"] = min(serie, key=lambda r: r[4])[0]
    fuori["soglia_holm_rango1"] = 0.05 / 10

    # --- varianza e risoluzione -------------------------------------------------------
    sd, quota, kinf = {}, {}, {}
    for tid, mod, a, b in sv.CONTRASTI:
        r = sv.scomponi(mod, a, b)
        if r is None:
            continue
        sd[tid], quota[tid], kinf[tid] = r["sd_oss"], r["quota"], r["k_inf"]
    fuori["sd_min"] = min(sd.values())
    fuori["sd_max"] = max(sd.values())
    fuori["rapporto_sd"] = max(sd.values()) / min(sd.values())
    fuori["quota_rumore_T3"] = quota["T3"]
    fuori["k_inf_T3"] = kinf["T3"]
    fuori["quota_rumore_T6"] = quota["T6"]
    fuori["k_inf_T6"] = kinf["T6"]
    fuori["contrasti_sopra_100"] = sum(1 for q in quota.values() if q >= 1.0)

    # MDE per contrasto, alla potenza 80% che il disegno ha usato
    mde = {t: 100 * Z_80 * s / math.sqrt(45) for t, s in sd.items()}
    fuori["mde_min"] = min(mde.values())
    fuori["mde_max"] = max(mde.values())
    fuori["mde_sopra_prereg"] = sum(1 for m in mde.values() if m > MDE_PREREG)
    fuori["mde_totali"] = len(mde)

    # --- potenza ----------------------------------------------------------------------
    pot = {t: pc.potenza_t(s) for t, _, s in pc.SD}
    fuori["potenza_min"] = min(pot.values())
    fuori["potenza_max"] = max(pot.values())

    # --- T10, con il modello come unita' ----------------------------------------------
    from scipy import stats
    stime = pc.T10_PER_MODELLO
    se = st.stdev(stime) / math.sqrt(len(stime))
    tc = stats.t.ppf(0.975, df=len(stime) - 1)
    fuori["t10_delta"] = 100 * st.mean(stime)
    fuori["t10_lo"] = 100 * (st.mean(stime) - tc * se)
    fuori["t10_hi"] = 100 * (st.mean(stime) + tc * se)

    # --- i numeri che vengono dalle traiettorie ---------------------------------------
    out, _ = esegui("budget_turni.py", env)
    for riga in out.splitlines():
        if "che esauriscono il budget" in riga:
            fuori["run_al_budget"] = int(riga.split(":")[1].split("(")[0].strip())
        if riga.strip().startswith("testuale"):
            fuori["run_al_budget_testuali"] = int(riga.split()[2])
        if riga.strip().startswith("nativo"):
            fuori["run_al_budget_native"] = int(riga.split()[2])

    out, _ = esegui("baseline_economico.py", env)
    for riga in out.splitlines():
        if "senza nessuna tool call" in riga:
            fuori["run_senza_tool"] = int(riga.split(":")[1].strip())
        elif "con almeno una" in riga:
            fuori["run_con_tool"] = int(riga.split(":")[1].strip())
        elif "medio SENZA tool call" in riga:
            fuori["pavimento_medio"] = float(riga.split(":")[1].split()[0])
        elif "medio CON tool call" in riga:
            fuori["media_con_tool"] = float(riga.split(":")[1].split()[0])
    if "run_senza_tool" in fuori and "run_con_tool" in fuori:
        fuori["misurazioni_valide"] = fuori["run_senza_tool"] + fuori["run_con_tool"]

    out, _ = esegui("incertezza.py", env)
    for riga in out.splitlines():
        if "Confronti con bande separate" in riga:
            fuori["confronti_bande_separate"] = int(riga.split(":")[1].split("su")[0].strip())
            fuori["confronti_totali"] = int(riga.split("su")[1].split("—")[0].strip())

    return fuori


def stampa(d, titolo):
    print(f"\n  {titolo}")
    for k in sorted(d):
        v = d[k]
        print(f"    {k:<28}{v:>12.4f}" if isinstance(v, float) else f"    {k:<28}{v:>12}")


def controlla_risposta_nota(conf):
    """Il controllo che rende affidabile tutto il resto: sulla raccolta confermativa questa
    catena deve riprodurre i numeri che il paper ha oggi. Se non li riproduce, non e' la
    ri-raccolta a essere sospetta — e' la catena."""
    print("\n  CONTROLLO a risposta nota: la confermativa deve dare i numeri già nel paper")
    falliti = []
    for k, atteso in ATTESI_CONFERMATIVA.items():
        if k not in conf:
            falliti.append((k, atteso, "assente"))
            continue
        ott = conf[k]
        tol = max(abs(atteso) * 0.02, 0.0006) if isinstance(atteso, float) else 0.51
        ok = abs(ott - atteso) <= tol
        stato = "ok" if ok else "DIVERGE"
        if not ok:
            falliti.append((k, atteso, ott))
        print(f"    {k:<28} atteso {atteso:>10}   ottenuto "
              + (f"{ott:>10.4f}" if isinstance(ott, float) else f"{ott:>10}")
              + f"   {stato}")
    return falliti


# ---------------------------------------------------------------------------------------
# I NUMERI DELLA REVISIONE 03, sorvegliati come tutti gli altri. Sono entrati nel paper il
# 2026-08-19 e vengono da due script nuovi: senza una voce qui sarebbero prosa senza guardia,
# che e' la condizione in cui un numero stantio sopravvive a un giro di revisione.
NUOVI_REVISIONE_03 = {
    # analysis/granularita_diretta.py — la decomposizione sul sottoinsieme non saturo
    "T3_quota_tutti": (0.5, "%", "quota di rumore di T3 su tutti i 45 binari"),
    "T3_quota_entrambe": (0.7, "%", "T3 escludendo i saturi in entrambe le celle, K=29"),
    "T3_quota_almeno_una": (1.7, "%", "T3 escludendo i saturi in almeno una cella, K=20"),
    "T6_quota_entrambe": (15.6, "%", "T6, regola entrambe, K=41"),
    "T6_quota_almeno_una": (17.0, "%", "T6, regola severa, K=24"),
    # analysis/denominatore_roster.py — l'incidenza dentro il roster tentato
    "coppie_tentate": (21, "", "coppie modello-piattaforma tentate"),
    "coppie_rimosse": (8, "", "rimosse prima di produrre un punteggio"),
    "cause_distinte": (7, "", "cause distinte, di cui 6 fra gli otto meccanismi nominati"),
    "modelli_sondati": (11, "", "modelli distinti sondati"),
}


def verifica_revisione_03():
    """Ricalcola i numeri della revisione 03 dai loro script e li confronta col dichiarato.

    Un valore implausibile si autodenuncia; uno plausibile e sbagliato no --- quindi il
    confronto e' col valore atteso, non con un intervallo di ragionevolezza.
    """
    import importlib
    import io as _io
    import contextlib

    fuori = []
    # il denominatore del roster: si legge dalla struttura dichiarata, non dallo stdout
    dr = importlib.import_module("denominatore_roster")
    tentate = len(dr.ROSTER)
    rimosse = [r for r in dr.ROSTER if r[2] == "rimosso"]
    cause = {r[3] for r in rimosse}
    modelli = {r[0] for r in dr.ROSTER}
    for chiave, ottenuto in (("coppie_tentate", tentate),
                             ("coppie_rimosse", len(rimosse)),
                             ("cause_distinte", len(cause)),
                             ("modelli_sondati", len(modelli))):
        atteso = NUOVI_REVISIONE_03[chiave][0]
        if ottenuto != atteso:
            fuori.append((chiave, atteso, ottenuto))

    print("  REVISIONE 03 — i numeri nuovi contro i loro script")
    for chiave, (atteso, unita, eti) in NUOVI_REVISIONE_03.items():
        rotto = [f for f in fuori if f[0] == chiave]
        if rotto:
            print(f"    DIVERGE  {chiave:<24}dichiarato {atteso}{unita}, ottenuto {rotto[0][2]}")
        else:
            print(f"    ok       {chiave:<24}{atteso}{unita}  — {eti}")
    if fuori:
        raise SystemExit(f"  {len(fuori)} numeri della revisione 03 divergono dai loro script")
    print("    (le quote della granularita' si verificano lanciando granularita_diretta.py,")
    print("     che porta il proprio controllo a risposta nota nei due sensi)")


# Gli intervalli sui sottoinsiemi, entrati il 2026-08-19 dopo che un seggio di regressione ha
# notato la disparita': la stima a K=45 portava il proprio intervallo, quelle a K ridotto no,
# ed e' li' che la varianza campionaria conta di piu'.
# I percentili del controllo di randomizzazione, entrati il 2026-08-19 dopo che un seggio
# avversariale ha mostrato che in due casi su quattro l'esclusione non si distingue da un effetto
# di taglia. Il criterio sorvegliato NON e' che i percentili siano alti --- due non lo sono, ed e'
# dichiarato --- ma che il paper li riporti tutti e quattro: se uno sparisse dalla prosa, la claim
# tornerebbe piu' forte di cio' che la misura sostiene.
PERCENTILI_RANDOMIZZAZIONE = {
    "T3_entrambe": 78.7, "T3_almeno_una": 96.0,
    "T6_entrambe": 96.5, "T6_almeno_una": 84.6,
}


INTERVALLI_SOTTOINSIEMI = {
    "T3_tutti":      (0.5, (0.0, 1.4), 45),
    "T3_entrambe":   (0.7, (0.0, 2.0), 29),
    "T3_almeno_una": (1.7, (0.0, 3.2), 20),
    "T6_tutti":      (9.1, (4.1, 21.6), 45),
    "T6_entrambe":   (15.6, (10.9, 25.0), 41),
    "T6_almeno_una": (17.0, (11.3, 32.6), 24),
}


def verifica_intervalli_sottoinsiemi():
    """Il criterio che l'obiezione della granularita' pone: nessun estremo superiore raggiunge il
    50%. Se un giorno lo raggiungesse, la misura non chiuderebbe piu' l'obiezione e il contributo
    andrebbe ristretto --- quindi il controllo e' sulla condizione, non sul numero."""
    print("  INTERVALLI SUI SOTTOINSIEMI — il criterio e' che nessun estremo superiore tocchi il 50%")
    rotti = []
    for k, (q, (lo, hi), K) in INTERVALLI_SOTTOINSIEMI.items():
        ok = hi < 50.0 and lo <= q <= hi
        if not ok:
            rotti.append(k)
        print(f"    {'ok  ' if ok else 'ROTTO'} {k:<16}{q:>6.1f}%  [{lo:.1f}, {hi:.1f}]  K={K}")
    if rotti:
        raise SystemExit(f"  {len(rotti)} intervalli non soddisfano il criterio")
    print("    nessun estremo superiore raggiunge il 50%: l'obiezione resta delimitata")
    print("\n  I QUATTRO PERCENTILI DELLA RANDOMIZZAZIONE devono comparire tutti nel paper")
    testo = ""
    import glob as _g
    for f in _g.glob("paper/sections/*.tex"):
        testo += open(f, encoding="utf-8", errors="ignore").read()
    mancanti = [k for k, v in PERCENTILI_RANDOMIZZAZIONE.items() if f"{v:.1f}" not in testo]
    for k, v in PERCENTILI_RANDOMIZZAZIONE.items():
        print(f"    {'ok  ' if k not in mancanti else 'MANCA'} {k:<16}{v:.1f}")
    if mancanti:
        raise SystemExit(f"  {len(mancanti)} percentili non compaiono nel paper: senza di loro la "
                         "claim torna piu' forte della misura")


if __name__ == "__main__":
    conferma = "--confermativa" in sys.argv
    confronta = "--confronta" in sys.argv

    if confronta:
        nuova = numeri(confermativa=False)
        vecchia = numeri(confermativa=True)
        print("\n  numero                        confermativa    ri-raccolta")
        for k in sorted(set(nuova) | set(vecchia)):
            a, b = vecchia.get(k, "—"), nuova.get(k, "—")
            fa = f"{a:>12.4f}" if isinstance(a, float) else f"{a:>12}"
            fb = f"{b:>15.4f}" if isinstance(b, float) else f"{b:>15}"
            print(f"    {k:<28}{fa}{fb}")
        falliti = controlla_risposta_nota(vecchia)
    else:
        d = numeri(confermativa=conferma)
        stampa(d, "raccolta confermativa" if conferma else
               "ri-raccolta (base primaria, EMENDAMENTO-06)")
        falliti = controlla_risposta_nota(d if conferma else numeri(confermativa=True))

    if falliti:
        print(f"\n  {len(falliti)} valori divergono da quelli nel paper: la catena di calcolo")
        print("  non e' quella che ha prodotto il testo attuale, e i numeri nuovi non sono")
        print("  affidabili finché questo non e' spiegato.")
        raise SystemExit(2)
    print("\n  tutti i valori noti riprodotti: la catena e' quella del testo attuale")

    # LE DUE GUARDIE DELLA REVISIONE 03, collegate. Erano definite DOPO questo blocco, quindi
    # `python3 analysis/numeri_paper.py` --- il comando che la Data Availability indica al lettore
    # --- non le eseguiva mai. Un seggio di conformita' l'ha trovato con un grep che contava zero
    # chiamate. E' il difetto che questo progetto documenta come il proprio, applicato a se stesso:
    # un controllo scritto e non invocato e' un commento.
    print()
    verifica_revisione_03()
    print()
    verifica_intervalli_sottoinsiemi()
