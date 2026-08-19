#!/usr/bin/env python3
"""R10 — quanto si sposta una graduatoria quando un endpoint rifiuta un modello.

PERCHE'. Il paper sostiene che un rifiuto e' un effetto di SELEZIONE e non un bias, sulla base di
un argomento logico: il modello assente non ha una riga da correggere. L'argomento e' giusto e non
basta, perche' non dice **quanto** cambia la conclusione di chi legge una graduatoria a cui manca
una riga. Senza quel numero la proposizione resta un'affermazione concettuale.

IL CASO E' REALE, non ipotetico. Il censimento documenta modelli serviti da un cloud e rifiutati da
un altro: `Llama-3.1-8B` deprecato su una piattaforma mentre un'altra lo serve, `Llama-4-Maverick`
bloccato per giurisdizione mentre altri della stessa famiglia girano. Chi valuta su un endpoint solo
vede una graduatoria a cui mancano righe, e non sa quali.

COSA MISURA QUESTO SCRIPT. Sui quattro modelli dei bracci pieni, per i quali esiste un punteggio su
entrambi i cloud, si costruisce la graduatoria per cloud e si simula il rifiuto di ciascun modello
(leave-one-out). Per ogni rimozione si riporta:

  - di quante posizioni si spostano i modelli rimasti;
  - come cambia il divario fra il primo e l'ultimo, che e' la quantita' che una valutazione
    riporta come «distanza fra i sistemi confrontati»;
  - se la graduatoria dei due cloud, che senza rimozioni concorda o discorda in modo misurabile,
    cambia il proprio accordo.

IL BOUND E' UN LIMITE INFERIORE, e va detto: con quattro modelli il massimo spostamento possibile e'
piccolo per costruzione. Su una graduatoria di venti modelli --- la dimensione di un leaderboard
pubblicato --- lo stesso meccanismo ha piu' spazio per muovere, non meno. Questo script misura cio'
che i nostri dati permettono di misurare, e la direzione dell'extrapolazione si dichiara invece di
essere lasciata al lettore.

    python3 analysis/missingness_bound.py
    python3 analysis/missingness_bound.py --confermativa
"""
import os
import statistics as st
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

CLOUD = ("databricks", "bedrock")


def graduatoria(punti):
    """(modello, punteggio) ordinati dal migliore, con la posizione."""
    ordinati = sorted(punti.items(), key=lambda kv: -kv[1])
    return {m: (i + 1, p) for i, (m, p) in enumerate(ordinati)}


def concordanza(a, b):
    """Coppie concordanti fra due graduatorie, su tutte le coppie di modelli comuni."""
    comuni = sorted(set(a) & set(b))
    tot = conc = 0
    for i in range(len(comuni)):
        for j in range(i + 1, len(comuni)):
            m, n = comuni[i], comuni[j]
            tot += 1
            if (a[m][0] < a[n][0]) == (b[m][0] < b[n][0]):
                conc += 1
    return conc, tot


if __name__ == "__main__":
    conf = "--confermativa" in sys.argv
    os.environ["C2_RESULTS"] = "results" if conf else "results/riraccolta"
    os.environ["C2_PATTERN"] = "c2_*.csv" if conf else "c2r_*.csv"
    import scomposizione_varianza as sv

    MODELLI = sorted({c[1] for c in sv.CONTRASTI})
    # il punteggio di un modello su un cloud: media sui binari, trasporto nativo
    punti = {}
    for cl in CLOUD:
        per_modello = {}
        for m in MODELLI:
            r = sv.runs_per_binario(m, cl, "native")
            if r:
                per_modello[m] = st.mean([st.mean(v) for v in r.values()])
        punti[cl] = per_modello

    print(f"  raccolta {'confermativa' if conf else 'primaria'}, trasporto nativo\n")
    for cl in CLOUD:
        g = graduatoria(punti[cl])
        print(f"  graduatoria su {cl}:")
        for m, (pos, p) in sorted(g.items(), key=lambda kv: kv[1][0]):
            print(f"    {pos}. {m:<22}{p:.4f}")
    conc, tot = concordanza(graduatoria(punti[CLOUD[0]]), graduatoria(punti[CLOUD[1]]))
    print(f"\n  accordo fra le due graduatorie, senza rimozioni: {conc}/{tot} coppie")

    print("\n  SIMULAZIONE DEL RIFIUTO — un modello per volta, su un cloud per volta")
    print(f"  {'rimosso da':<34}{'spostamenti':>13}{'divario 1o-ultimo':>20}{'accordo':>10}")
    massimo_spost, massimo_divario = 0, 0.0
    for cl in CLOUD:
        base = graduatoria(punti[cl])
        divario_base = max(punti[cl].values()) - min(punti[cl].values())
        for rimosso in sorted(punti[cl]):
            resto = {m: p for m, p in punti[cl].items() if m != rimosso}
            g = graduatoria(resto)
            spost = sum(1 for m in g if g[m][0] != base[m][0])
            divario = max(resto.values()) - min(resto.values())
            altro = graduatoria({m: p for m, p in punti[CLOUD[1 - CLOUD.index(cl)]].items()
                                if m != rimosso})
            c2_, t2 = concordanza(g, altro)
            massimo_spost = max(massimo_spost, spost)
            massimo_divario = max(massimo_divario, abs(divario - divario_base))
            print(f"  {rimosso + ' da ' + cl:<34}{spost:>13}"
                  f"{f'{100*divario_base:.1f} -> {100*divario:.1f}pp':>20}{f'{c2_}/{t2}':>10}")

    print("\n  IL BOUND")
    print(f"    massimo spostamento di posizione fra i modelli rimasti: {massimo_spost}")
    print(f"    massima variazione del divario primo-ultimo: {100*massimo_divario:.1f}pp")
    print(f"    per confronto, il piu' grande effetto del trasporto misurato qui e' 9,83pp")
    if 100 * massimo_divario > 9.83:
        print("    -> la rimozione di UN modello sposta il divario di piu' di quanto lo sposti")
        print("       il piu' grande effetto che questo studio misura. La selezione non e'")
        print("       piccola rispetto al segnale che una valutazione riporta.")
    else:
        print("    -> su quattro modelli la rimozione sposta il divario di meno del piu' grande")
        print("       effetto misurato. Con quattro unita' il bound e' per costruzione piccolo:")
        print("       si riporta come limite inferiore, non come misura del fenomeno.")

    print("\n  CONTROLLO a risposta nota")
    g = graduatoria(punti[CLOUD[0]])
    ok1 = len(g) == len(punti[CLOUD[0]]) and min(p for p, _ in g.values()) == 1
    print(f"    la graduatoria ha una prima posizione e tutte le voci: {'ok' if ok1 else 'FALLITO'}")
    finta = graduatoria({"a": 0.9, "b": 0.5, "c": 0.1})
    ok2 = finta["a"][0] == 1 and finta["c"][0] == 3
    print(f"    su punteggi noti (0,9 / 0,5 / 0,1) l'ordine e' 1-2-3: {'ok' if ok2 else 'FALLITO'}")
    conc_id, tot_id = concordanza(finta, finta)
    ok3 = conc_id == tot_id
    print(f"    una graduatoria concorda con se stessa su tutte le coppie: "
          f"{'ok' if ok3 else 'FALLITO'}")
    if not all([ok1, ok2, ok3]):
        raise SystemExit("  il calcolo del bound non rispetta le sue proprieta' (exit 2)")
