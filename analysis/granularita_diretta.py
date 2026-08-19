#!/usr/bin/env python3
"""La granularita' della metrica, misurata invece che confrontata.

PERCHE'. La decomposizione della varianza e' il contributo che il capitolo mette per primo, e la
sua obiezione piu' forte e' che una metrica satura --- pass-rate su cinque unit test, sei valori
possibili, il 33% delle medie binario-per-cella esattamente su 0 o 1 --- produce da sola una
grande varianza fra binari, senza nessun contributo del trasporto.

Il paper la chiudeva con DUE condizioni, e la prima era circolare: diceva che la granularita' non
puo' spiegare perche' la stessa metrica dia 0,5% qui e 84% nella raccolta da cui il disegno ha
preso il dimensionamento. Ma l'84% e' il numero che il paper stesso dichiara difettoso (righe
andate in crash mediate come zeri), quindi la difesa poggiava su un valore invalidato: si
appoggiava a un confronto per non fare una misura.

QUESTA E' LA MISURA. Si rifa' la decomposizione escludendo i binari saturi, e si guarda se la
quota di rumore regge. Se regge, l'obiezione e' chiusa da un dato dello stesso corpus, e non serve
piu' nessun confronto fra capitoli.

DUE DEFINIZIONI DI «SATURO», e si riportano entrambe perche' rispondono a domande diverse:

  - `entrambe`: il binario e' saturo in TUTTE E DUE le celle del contrasto. E' il caso di puro
    artefatto: due medie su 0 danno differenza 0, una su 0 e una su 1 danno differenza +/-1, che
    e' il singolo maggior contributo possibile alla varianza fra binari e non contiene alcuna
    informazione sul trasporto oltre al fatto che il compito e' impossibile o banale.
  - `almeno_una`: basta che UNA cella sia satura. E' la definizione severa, perche' toglie anche
    i binari in cui un braccio ha risolto e l'altro no --- che sono informativi sul trasporto.
    Toglierli sottostima l'effetto, quindi se la quota di rumore regge anche qui, regge in un
    caso in cui abbiamo giocato contro noi stessi.

    python3 analysis/granularita_diretta.py
    python3 analysis/granularita_diretta.py --confermativa
"""
import math
import os
import statistics as st
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

BANDA = 0.03
Z = (1.959964 + 0.841621) ** 2
RUNS = 8


def decomponi(a, b, binari):
    """La formula e' DUPLICATA da `scomposizione_varianza.py`, e quel file NON e' nella catena
    degli hash: `verifica_hash.sh` copre sei file e nessuno dei due e' fra quelli. Il congelato e'
    `analyze_c2.py`. Un seggio avversariale ha verificato che le due copie coincidono oggi riga per
    riga e ha nominato il rischio residuo --- nulla impedisce che divergano domani senza che una
    guardia se ne accorga. La prima versione di questo docstring diceva «la stessa formula del file
    congelato», che era falso su quale file sia congelato.

    Non si cambia lo stimatore per fare questa misura,
    altrimenti la differenza fra i due numeri non e' l'esclusione dei binari saturi."""
    diff = [st.mean(a[k]) - st.mean(b[k]) for k in binari]
    if len(diff) < 2:
        return None
    sd_oss = st.stdev(diff)
    if sd_oss <= 0:
        return None
    var_a = st.mean([st.variance(a[k]) for k in binari])
    var_b = st.mean([st.variance(b[k]) for k in binari])
    sd_rumore = math.sqrt((var_a + var_b) / RUNS)
    var_res = max(0.0, sd_oss ** 2 - sd_rumore ** 2)
    return {
        "K": len(binari),
        "sd": sd_oss,
        "quota": (sd_rumore ** 2) / (sd_oss ** 2),
        "k_inf": Z * var_res / BANDA ** 2,
        "clamp": sd_oss ** 2 - sd_rumore ** 2 < 0,
    }


def saturo(media):
    return media in (0.0, 1.0)


SEME = 20260819
B = 5000


def bootstrap_quota(a, b, binari):
    """L'intervallo sulla quota, ricampionando i binari DEL SOTTOINSIEME.

    Serve perche' la stima a K ridotto poggia su meno unita' di quella a K=45, ed e' esattamente
    dove la varianza campionaria conta di piu': riportare la prima senza intervallo e la seconda
    con l'intervallo e' la disparita' che un revisore nota per prima. Ricampiona i binari, che e'
    l'unita' su cui il contrasto e' appaiato, con lo stesso seme dichiarato del bootstrap
    principale.
    """
    import random
    rng = random.Random(SEME)
    quote = []
    n = len(binari)
    if n < 3:
        return None, None
    for _ in range(B):
        camp = [binari[rng.randrange(n)] for _ in range(n)]
        r = decomponi(a, b, camp)
        if r is not None:
            quote.append(r["quota"])
    if not quote:
        return None, None
    s = sorted(quote)
    def pct(q):
        i = max(0, min(len(s) - 1, int(round(q / 100 * (len(s) - 1)))))
        return s[i]
    return pct(2.5), pct(97.5)


def randomizzazione(a, b, com, K, oss, B=20000):
    """Il controllo che decide se l'esclusione dimostri qualcosa sulla SATURAZIONE.

    Escludere binari riduce K, e una quota di rumore calcolata su meno unita' ha una distribuzione
    diversa. Se togliere K binari A CASO produce una quota uguale o piu' alta con frequenza
    apprezzabile, l'aumento osservato non distingue «ho tolto i saturi» da «ho tolto dei binari», e
    la misura DELIMITA l'obiezione invece di rifiutarla.

    Restituisce il percentile in cui la quota osservata cade nella distribuzione casuale a K fisso.
    Un percentile intorno all'80 significa che una volta su cinque il caso fa altrettanto.
    """
    import random
    rng = random.Random(SEME)
    quote = []
    for _ in range(B):
        r = decomponi(a, b, rng.sample(com, K))
        if r is not None:
            quote.append(100 * r["quota"])
    if not quote:
        return None, None
    quote.sort()
    return 100 * sum(1 for q in quote if q <= oss) / len(quote), st.median(quote)


if __name__ == "__main__":
    conf = "--confermativa" in sys.argv
    os.environ["C2_RESULTS"] = "results" if conf else "results/riraccolta"
    os.environ["C2_PATTERN"] = "c2_*.csv" if conf else "c2r_*.csv"
    os.environ.setdefault("C2_PREFISSO", "c2_" if conf else "c2r_")
    import scomposizione_varianza as sv

    print(f"  raccolta {'confermativa' if conf else 'primaria'}: la decomposizione con e senza i "
          f"binari saturi\n")
    print(f"  {'':5}{'regola':<14}{'K':>4}{'quota rumore':>14}{'IC95':>18}"
          f"{'K_inf':>8}{'esclusi':>9}")

    esiti = {}
    for tid, mod, ca, cb in sv.CONTRASTI:
        a = sv.runs_per_binario(mod, *ca)
        b = sv.runs_per_binario(mod, *cb)
        com = sorted(set(a) & set(b))
        if len(com) < 2:
            continue
        ma = {k: st.mean(a[k]) for k in com}
        mb = {k: st.mean(b[k]) for k in com}
        insiemi = {
            "tutti": com,
            "entrambe": [k for k in com if not (saturo(ma[k]) and saturo(mb[k]))],
            "almeno_una": [k for k in com if not (saturo(ma[k]) or saturo(mb[k]))],
        }
        esiti[tid] = {}
        for eti, ins in insiemi.items():
            r = decomponi(a, b, ins)
            esiti[tid][eti] = r
            if r is None:
                print(f"  {tid if eti=='tutti' else '':<5}{eti:<14}{len(ins):>4}"
                      f"{'non calcolabile':>14}")
                continue
            marca = "*" if r["clamp"] else ""
            # L'intervallo si calcola sui due contrasti che il paper cita per esteso. Sugli altri
            # sei sarebbe lavoro senza lettore: le loro quote non entrano in prosa, e su T7/T8 la
            # varianza residua e' troncata, quindi un intervallo li' non descrive una stima.
            lo, hi = bootstrap_quota(a, b, ins) if tid in ("T3", "T6") else (None, None)
            ic = f"[{100*lo:.1f}, {100*hi:.1f}]" if lo is not None else "—"
            r["ic"] = (lo, hi)
            print(f"  {tid if eti=='tutti' else '':<5}{eti:<14}{r['K']:>4}"
                  f"{100*r['quota']:>13.1f}%{marca}{ic:>18}{r['k_inf']:>8.0f}"
                  f"{len(com)-len(ins):>9}")
        print()

    # --- la domanda che l'obiezione pone ------------------------------------------------
    print("  LA RISPOSTA ALL'OBIEZIONE DELLA GRANULARITA'")
    t3 = esiti.get("T3")
    if not t3 or not t3["tutti"]:
        raise SystemExit("  T3 non calcolabile: la misura non si puo' fare")
    q0 = 100 * t3["tutti"]["quota"]
    for eti, testo in (("entrambe", "togliendo i binari saturi in ENTRAMBE le celle"),
                       ("almeno_una", "togliendo quelli saturi in ALMENO UNA cella")):
        r = t3[eti]
        if r is None:
            print(f"    {testo}: non calcolabile")
            continue
        q = 100 * r["quota"]
        print(f"    su T3, {testo}: la quota di rumore va da {q0:.1f}% a {q:.1f}% "
              f"(K da {t3['tutti']['K']} a {r['K']})")
    r_str = t3["almeno_una"]
    if r_str and 100 * r_str["quota"] < 50:
        print("    -> la quota resta sotto la meta' anche nel caso severo, quindi la saturazione")
        print("       della metrica non produce da sola la varianza fra binari che il capitolo")
        print("       attribuisce all'eterogeneita' vera. L'obiezione si chiude con un dato di")
        print("       QUESTO corpus, senza appoggiarsi a un confronto con un numero difettoso.")
    else:
        print("    -> la quota sale al di sopra della meta' quando i binari saturi escono: la")
        print("       saturazione porta una parte sostanziale di cio' che il capitolo attribuisce")
        print("       all'eterogeneita'. Il contributo va ristretto di conseguenza.")

    # --- IL CONTROLLO CHE DECIDE COSA LA MISURA DIMOSTRA --------------------------------
    print("\n  RANDOMIZZAZIONE: la quota osservata contro sottoinsiemi CASUALI della stessa taglia")
    print(f"    {'caso':<22}{'K':>4}{'osservata':>11}{'mediana casuale':>17}{'perc.':>8}")
    for tid in ("T3", "T6"):
        cc = [x for x in sv.CONTRASTI if x[0] == tid]
        if not cc or tid not in esiti:
            continue
        _, mod, ca, cb = cc[0]
        a = sv.runs_per_binario(mod, *ca); b = sv.runs_per_binario(mod, *cb)
        com = sorted(set(a) & set(b))
        for regola in ("entrambe", "almeno_una"):
            r = esiti[tid].get(regola)
            if not r:
                continue
            pct, med = randomizzazione(a, b, com, r["K"], 100 * r["quota"])
            if pct is None:
                continue
            print(f"    {tid + ' ' + regola:<22}{r['K']:>4}{100*r['quota']:>10.1f}%"
                  f"{med:>16.1f}%{pct:>7.1f}")
    print("    Un percentile intorno all'80 significa che togliere binari a caso produce una quota")
    print("    uguale o piu' alta una volta su cinque: in quei casi l'esclusione non si distingue")
    print("    da un effetto di taglia, e la misura delimita l'obiezione invece di rifiutarla.")

    # --- il controllo a risposta nota, nei due sensi -------------------------------------
    print("\n  CONTROLLO a risposta nota, nei due sensi")
    ok = []
    for tid, e in esiti.items():
        if e["tutti"] and e["almeno_una"]:
            ok.append(e["almeno_una"]["K"] <= e["tutti"]["K"])
    print(f"    escludendo binari il K non cresce mai: {'ok' if all(ok) else 'FALLITO'}")
    finto_a = {f"b{i}": [0.0] * RUNS for i in range(10)}
    finto_b = {f"b{i}": [1.0] * RUNS for i in range(10)}
    ins = [k for k in finto_a if not (saturo(0.0) and saturo(1.0))]
    ok.append(len(ins) == 0)
    print(f"    dieci binari tutti saturi in entrambe le celle si escludono tutti: "
          f"{'ok' if len(ins) == 0 else 'FALLITO'}")
    misto = {"x": [0.0, 1.0] * (RUNS // 2)}
    ok.append(not saturo(st.mean(misto["x"])))
    print(f"    un binario a media 0,5 non e' saturo: "
          f"{'ok' if not saturo(st.mean(misto['x'])) else 'FALLITO'}")
    if not all(ok):
        raise SystemExit("  la misura non rispetta le sue proprieta'")
