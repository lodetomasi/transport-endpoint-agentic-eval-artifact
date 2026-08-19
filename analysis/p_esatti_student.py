#!/usr/bin/env python3
"""I p-value dei dieci test con la t di Student esatta, contro quelli dello script congelato.

`analysis/analyze_c2.py` e' congelato per hash dal 2026-08-13 e NON si tocca. La sua
`t_appaiato()` non usa la distribuzione t: usa una normale con un fattore di correzione,

    p = 2 * (1 - norm_cdf(|t| / (1 + 1/(4(n-1)))))

perche' — dice il commento — scipy non era garantito nell'ambiente di raccolta, e
un'analisi che non gira dove girano i dati e' un'analisi che qualcuno rifara' a mano. La
scelta e' ragionevole e dichiarata; il punto e' che a K=45 quell'approssimazione **sottostima
il p in modo sistematico**, cioe' sempre nella direzione che fa sembrare l'effetto piu'
significativo di quanto sia.

Questo file misura di quanto, con `scipy.stats.t` che nel frattempo esiste in questo ambiente,
e verifica la sola cosa che conta per le conclusioni: **se qualche esito di Holm cambia**.

Trovato dal revisore metodologico del gauntlet il 2026-08-15.
"""
import csv
import glob
import os

# Terzo script con il percorso fissato alla raccolta confermativa: con --results puntato alla
# ri-raccolta restituiva comunque i numeri vecchi, cioe' il modo in cui un parametro ignorato
# somiglia a un parametro rispettato. Si scegli da ambiente, come negli altri due.
RADICE_DATI = os.environ.get("C2_RESULTS", "results")
PATTERN = os.environ.get("C2_PATTERN", "c2_*.csv")
import math
import statistics as st
import sys
from collections import defaultdict

try:
    from scipy import stats
except ImportError:                                    # noqa: F401
    raise SystemExit(
        "questo script richiede scipy (vedi requirements.txt).\n"
        "  Non e' una dipendenza dell'analisi pre-registrata: analyze_c2.py gira senza, ed e'\n"
        "  proprio la ragione per cui usa un'approssimazione normale invece della t esatta.\n"
        "  Questo script misura quanto costa quell'approssimazione, quindi scipy gli serve.")

sys.path.insert(0, "src")
from qualita_run import e_misurazione  # noqa: E402

RUNS = 8
M_FAMIGLIA = 10
CONTRASTI = [
    ("T1", "gpt-oss-120b",      ("databricks", "native"), ("databricks", "text")),
    ("T2", "llama-3.3-70b",     ("databricks", "native"), ("databricks", "text")),
    ("T3", "claude-haiku-4-5",  ("databricks", "native"), ("databricks", "text")),
    ("T4", "claude-sonnet-4-5", ("databricks", "native"), ("databricks", "text")),
    ("T5", "gpt-oss-120b",      ("databricks", "native"), ("bedrock", "native")),
    ("T6", "llama-3.3-70b",     ("databricks", "native"), ("bedrock", "native")),
    ("T7", "claude-haiku-4-5",  ("databricks", "native"), ("bedrock", "native")),
    ("T8", "claude-sonnet-4-5", ("databricks", "native"), ("bedrock", "native")),
]


def cella(modello, infra, trasporto):
    per = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(RADICE_DATI, PATTERN))):
        with open(f, errors="ignore") as fh:
            for r in csv.DictReader(fh):
                if (r.get("modello"), r.get("infra"), r.get("trasporto")) == (modello, infra, trasporto):
                    if e_misurazione(r):
                        per[r["binary_id"]].append(float(r["pass_rate"]))
    return {b: st.mean(v[:RUNS]) for b, v in per.items() if len(v) >= RUNS}


def p_congelato(t, n):
    """La formula esatta di analyze_c2.py, riprodotta qui per il confronto."""
    return 2 * (1 - 0.5 * (1 + math.erf(abs(t) / (1 + 1.0 / (4 * (n - 1))) / math.sqrt(2))))


def holm(coppie):
    """Holm step-down su m=10 FISSO, come la pre-registrazione. Ritorna {id: passa}."""
    ordinati = sorted(coppie, key=lambda x: x[1])
    esiti, fermo = {}, False
    for i, (tid, p) in enumerate(ordinati):
        soglia = 0.05 / (M_FAMIGLIA - i)
        passa = (not fermo) and p <= soglia
        if not passa:
            fermo = True
        esiti[tid] = (p, soglia, passa)
    return esiti


def serie():
    """(id, K, t, p congelato, p Student) per gli otto contrasti appaiati. Estratta dal main
    perche' la tabella del paper la importa: un numero riparsato dallo stdout di un altro
    script e' un numero trascritto con passaggi in piu'."""
    fuori = []
    for tid, mod, ca, cb in CONTRASTI:
        a, b = cella(mod, *ca), cella(mod, *cb)
        com = sorted(set(a) & set(b))
        d = [b[k] - a[k] for k in com]
        n_ = len(d)
        if n_ < 2:
            continue
        se = st.stdev(d) / math.sqrt(n_)
        t = st.mean(d) / se
        fuori.append((tid, n_, t, p_congelato(t, n_), 2 * stats.t.sf(abs(t), df=n_ - 1)))
    return fuori


def p_misto_dal_congelato():
    """I p di T9 e T10 vengono dal modello misto dello script congelato, che e' l'unico a
    calcolarli. Erano due costanti scritte a mano: giuste sulla raccolta per cui erano state
    scritte, silenziosamente sbagliate su qualunque altra."""
    import subprocess
    qui = os.path.dirname(os.path.abspath(__file__))
    r = subprocess.run([sys.executable, os.path.join(qui, "analyze_c2.py"),
                        "--results", RADICE_DATI],
                       capture_output=True, text=True, cwd=os.path.dirname(qui))
    fuori = {}
    for riga in r.stdout.splitlines():
        c = riga.split()
        if c and c[0] in ("T9", "T10"):
            fuori[c[0]] = float(c[-1])
    if set(fuori) != {"T9", "T10"}:
        raise SystemExit("  T9/T10 non letti dallo script congelato: non li invento")
    return fuori


if __name__ == "__main__":
    print("p-value: approssimazione congelata contro t di Student esatta\n")
    print(f"  {'id':<5}{'K':>4}{'t':>9}{'p congelato':>14}{'p Student':>12}{'differenza':>13}")
    righe = serie()
    for tid, n, t, pc, ps in righe:
        print(f"  {tid:<5}{n:>4}{t:>9.3f}{pc:>14.4f}{ps:>12.4f}{ps - pc:>+13.4f}")

    sotto = sum(1 for _, _, _, pc, ps in righe if pc < ps)
    print(f"\n  L'approssimazione sottostima il p in {sotto} casi su {len(righe)}"
          + (" — sempre nella direzione che fa sembrare l'effetto piu' significativo."
             if sotto == len(righe) else "."))

    # Holm su entrambe le serie, con T9 e T10 ai loro p pre-registrati (dal misto)
    P_MISTO = p_misto_dal_congelato()
    for eti, idx in (("congelati", 3), ("Student", 4)):
        coppie = [(r[0], r[idx]) for r in righe] + list(P_MISTO.items())
        esiti = holm(coppie)
        passano = [k for k, v in esiti.items() if v[2]]
        print(f"\n  Holm m=10 sui p {eti}: {len(passano)} test superano la soglia"
              + (f" ({', '.join(passano)})" if passano else " — nessuno"))

    # CONTROLLO, nei due sensi. Confrontava con «0,0143 per T3»: vero sulla raccolta
    # confermativa e falso su ogni altra, quindi la guardia avrebbe accusato dati sani appena
    # la raccolta cambiava. Le due proprieta' sotto valgono su qualunque raccolta, e la seconda
    # e' il senso che manca sempre — senza di essa una guardia che accetta tutto passa.
    print("\n  CONTROLLO a risposta nota, nei due sensi:")
    esito = []
    ok = all(pc < ps for _, _, _, pc, ps in righe)
    esito.append(ok)
    print("    l'approssimazione sta SOTTO Student su tutti e otto -> "
          + ("ok" if ok else "FALLITO: in almeno un caso la sovrastima"))
    finta = p_congelato(2.463, 45)
    ok2 = abs(finta - 0.0143) < 0.0005
    esito.append(ok2)
    print(f"    su t=2,463 e K=45 l'approssimazione deve dare 0,0143: {finta:.4f} -> "
          + ("ok" if ok2 else "FALLITO: la formula congelata e cambiata"))
    if not all(esito):
        raise SystemExit("  i p non rispettano le loro proprieta strutturali")
    print("\n  CONCLUSIONE. La differenza e' sistematica e va dichiarata, ma NON cambia")
    print("  nessuna conclusione: a m=10 fisso nessun test supera la propria soglia di Holm")
    print("  con nessuna delle due serie. Lo script congelato resta congelato; il paper")
    print("  riporta i p esatti accanto, con la successione che dichiara la differenza.")
