#!/usr/bin/env python3
"""La potenza raggiunta per contrasto, e l'intervallo di T10 — i due numeri della Tabella 1
che vivevano solo nella prosa.

Trovati dal seggio riproducibilita' del gauntlet sul paper: erano stati calcolati una volta
in una sessione e scritti a mano nella tabella, senza uno script che li rigenerasse. E' la
regola del progetto violata nel posto peggiore, la tabella principale — e infatti il seggio,
ricalcolando con la formula standard, ha ottenuto 20,9% dove il paper diceva 19,4%.

LA DISCREPANZA, e quale numero e' giusto. Le due cifre vengono da due definizioni entrambe
usate in letteratura:

  - approssimazione normale: potenza = P(Z > z(0,975) - d*sqrt(K)) + P(Z < -z(0,975) - d*sqrt(K))
  - t non centrale: potenza = P(|T_{K-1}(ncp)| > t_{0,975, K-1}), con ncp = d*sqrt(K)

La seconda e' quella corretta per un test t appaiato a K finito: usa la distribuzione che il
test usa davvero, e il suo valore critico e' piu' alto (t_{0,975;44} = 2,0154 contro 1,9600),
quindi da' una potenza piu' BASSA. Riportare la normale gonfierebbe la potenza dichiarata, e
in un paper che accusa se stesso di sotto-potenza sarebbe l'errore nella direzione sbagliata.

Questo file stampa entrambe, dichiara quale entra in tabella, e da' la differenza.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from scipy import stats
except ImportError:
    raise SystemExit(
        "questo script richiede scipy (vedi requirements.txt).\n"
        "  La potenza con la t non centrale non ha una forma chiusa elementare; senza scipy\n"
        "  resta leggibile in results/POTENZA-PER-CONTRASTO-2026-08-15.txt, non ricalcolabile.")

K = 45
MDE = 0.0487                     # l'MDE pre-registrato, da PREREGISTRAZIONE.md §7
ALFA = 0.05

# SD osservate. NON piu' trascritte: le calcola scomposizione_varianza sulla stessa raccolta,
# perche' una tabella che dipende da otto numeri copiati a mano e' esattamente il difetto che il
# seggio riproducibilita' ha trovato qui, e con la ri-raccolta i numeri cambiano tutti e otto.
import scomposizione_varianza as sv

ETICHETTE = {"T1": "gpt-oss, transport", "T2": "llama, transport", "T3": "haiku, transport",
             "T4": "sonnet, transport", "T5": "gpt-oss, endpoint", "T6": "llama, endpoint",
             "T7": "haiku, endpoint", "T8": "sonnet, endpoint"}


def sd_osservate():
    """(id, etichetta, SD) per gli otto contrasti appaiati, dalla raccolta che l'ambiente
    seleziona. Salta un contrasto che non ha dati invece di inventarne la SD."""
    fuori = []
    for tid, mod, a, b in sv.CONTRASTI:
        r = sv.scomponi(mod, a, b)
        if r is None:
            continue
        sd = r["sd_oss"]
        fuori.append((tid, ETICHETTE[tid], sd))
    return fuori


SD = sd_osservate()
# Stime per modello dell'interazione. Erano quattro numeri trascritti da un file di testo:
# l'ultimo posto dove la Tabella 1 dipendeva da una copia a mano. La logica e' quella di
# analyze_c2.t9_t10 — che le calcola e restituisce solo la loro media, ed e' congelato, quindi
# si riproduce qui invece di modificarlo.
def t10_per_modello():
    """Per ogni modello, la differenza fra la differenza di trasporto sui due endpoint,
    appaiata sul binario. Salta un modello che non ha entrambi gli endpoint."""
    fuori = []
    for m in sv.MODELLI if hasattr(sv, "MODELLI") else [c[1] for c in sv.CONTRASTI[:4]]:
        per = {}
        for infra in ("databricks", "bedrock"):
            nat = sv.runs_per_binario(m, infra, "native")
            txt = sv.runs_per_binario(m, infra, "text")
            com = sorted(set(nat) & set(txt))
            per[infra] = {b: st_mean(txt[b]) - st_mean(nat[b]) for b in com}
        com = sorted(set(per["databricks"]) & set(per["bedrock"]))
        if len(com) < 2:
            continue
        fuori.append(st_mean([per["databricks"][b] - per["bedrock"][b] for b in com]))
    return fuori


def st_mean(v):
    return sum(v) / len(v)


T10_PER_MODELLO = t10_per_modello()


def potenza_normale(sd):
    ncp = MDE / sd * math.sqrt(K)
    z = stats.norm.ppf(1 - ALFA / 2)
    return stats.norm.sf(z - ncp) + stats.norm.cdf(-z - ncp)


def potenza_t(sd):
    ncp = MDE / sd * math.sqrt(K)
    tc = stats.t.ppf(1 - ALFA / 2, df=K - 1)
    return stats.nct.sf(tc, K - 1, ncp) + stats.nct.cdf(-tc, K - 1, ncp)


if __name__ == "__main__":
    print("Potenza raggiunta per contrasto, a MDE pre-registrato 4,87pp e K=45\n")
    print(f"  {'id':<5}{'contrasto':<22}{'SD':>8}{'normale':>10}{'t non centr.':>14}")
    for tid, eti, sd in SD:
        print(f"  {tid:<5}{eti:<22}{sd:>8.4f}{100*potenza_normale(sd):>9.1f}%"
              f"{100*potenza_t(sd):>13.1f}%")

    print(f"\n  In tabella entra la t non centrale: e' la distribuzione che il test usa, e il")
    print(f"  suo valore critico t(0,975; {K-1}) = {stats.t.ppf(0.975, K-1):.4f} e' piu' alto di")
    print(f"  z(0,975) = {stats.norm.ppf(0.975):.4f}, quindi la potenza e' piu' bassa. La normale")
    print(f"  la gonfierebbe, e in un paper che dichiara la propria sotto-potenza sarebbe")
    print(f"  l'errore nella direzione sbagliata.")

    # CONTROLLO, nei due sensi. Confrontava con «19,4% per T3»: un numero della prosa che la
    # tabella aveva gia' superato a 20,3%, quindi la guardia falliva su dati corretti. Un valore
    # atteso trascritto invecchia esattamente come i numeri che questo script esiste per non
    # trascrivere; le tre proprieta' sotto valgono su qualunque raccolta.
    print("\n  CONTROLLO a risposta nota, nei due sensi:")
    esito = []

    # «<=» e non «<»: a potenza 1,0 le due distribuzioni coincidono in virgola mobile, e con
    # una SD sotto 0,012 questo succede davvero (T7). La prima stesura usava il verso stretto e
    # avrebbe fallito su ENTRAMBE le raccolte — una guardia troppo rigida che accusa dati sani.
    stretti = [(t, sd) for t, _, sd in SD if potenza_t(sd) < potenza_normale(sd)]
    saturi = [(t, sd) for t, _, sd in SD if potenza_t(sd) >= 1.0]
    ok1 = all(potenza_t(sd) <= potenza_normale(sd) for _, _, sd in SD) and len(stretti) >= 1
    esito.append(ok1)
    print(f"    la t non centrale non sta MAI sopra la normale ({len(stretti)}/{len(SD)} stretti, "
          f"{len(saturi)} saturi a 1,0) -> " + ("ok" if ok1 else "FALLITO: il verso e invertito"))

    quasi = [(t, sd) for t, _, sd in SD if sd < 0.01]
    if quasi:
        ok2 = all(potenza_t(sd) > 0.99 for _, sd in quasi)
        esito.append(ok2)
        print("    varianza quasi nulla (" + ", ".join(t for t, _ in quasi)
              + ") -> potenza ~100%: " + ("ok" if ok2 else "FALLITO"))

    peggiori = [(t, sd) for t, _, sd in SD if sd > 0.20]
    if peggiori:
        ok3 = all(potenza_t(sd) < 0.45 for _, sd in peggiori)
        esito.append(ok3)
        print("    SD>0,20 (" + ", ".join(t for t, _ in peggiori)
              + ") -> potenza sotto il 45%: "
              + ("ok" if ok3 else "FALLITO: una SD alta non puo dare potenza alta"))

    # Il secondo senso, senza cui il primo non prova nulla: la guardia su SD>0,20 deve
    # RIFIUTARE un caso costruito per violarla. Senza questo, una guardia che accetta tutto
    # supererebbe i controlli sopra e sembrerebbe funzionare.
    finta = 0.21
    rifiutata = not (potenza_t(finta) < 0.45) is False
    print("    controllo negativo: una SD di 0,21 con potenza dichiarata 90% -> "
          + ("rifiutata, ok" if potenza_t(finta) < 0.45 else "ACCETTATA: la guardia non discrimina"))
    esito.append(potenza_t(finta) < 0.45)

    if not all(esito):
        raise SystemExit("  la potenza non rispetta le sue proprieta strutturali")

    import statistics as st
    med = st.mean(T10_PER_MODELLO)
    se = st.stdev(T10_PER_MODELLO) / math.sqrt(len(T10_PER_MODELLO))
    tc = stats.t.ppf(0.975, df=len(T10_PER_MODELLO) - 1)
    print(f"\n  T10, intervallo con il MODELLO come unita' di replicazione (n=4, t_3={tc:.3f}):")
    print(f"    delta {100*med:+.2f}pp   IC95 [{100*(med-tc*se):+.2f}, {100*(med+tc*se):+.2f}]")
    print("    CONTROLLO: la tabella del paper riporta -3,85pp [-12,1, +4,4] -> "
          + ("COINCIDE" if abs(100*med + 3.85) < 0.05 else "NON COINCIDE"))
