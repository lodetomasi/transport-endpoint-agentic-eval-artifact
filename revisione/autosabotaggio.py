#!/usr/bin/env python3
"""Quante volte il testo si mette sotto accusa, prima e dopo la revisione.

Tre famiglie, perche' si riparano in modi diversi:
  A. AMMISSIONE     -- «non abbiamo potuto», «non e' verificabile», «era difettoso»
  B. META-VIRTU'    -- il testo commenta la propria onesta' invece di darne la misura
  C. AUTO-OBIEZIONE -- il testo formula l'obiezione del revisore prima della propria evidenza

Il conteggio e' su HEAD contro il working tree, sezione per sezione.
CONTROLLO A RISPOSTA NOTA: una frase costruita apposta deve cadere in ciascuna famiglia, e un
paragrafo neutro in nessuna.

    python3 revisione/autosabotaggio.py [--autotest]
"""
import os, re, subprocess, sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEZ = ["00-front", "01-introduction", "02-related", "03-method", "04-design", "05-results",
       "06-census", "07-discussion", "08-threats", "09-conclusion", "11-declarations", "12-appendice"]

FAMIGLIE = {
    "A ammissione": [
        r"we cannot\b", r"could not (be )?(check|verif|obtain|settle)", r"\bnot verifiable\b",
        r"\bnot checkable\b", r"had no way\b", r"\bdefective\b", r"self-inflicted",
        r"validity flag (had )?failed", r"\bwas not (reachable|possible|checkable|verifiable)\b",
        r"argued rather than certified", r"declared, not proved", r"not outcome-independent",
        r"we (do|did) not (verify|test|size|measure)\b", r"\bwe decline\b", r"we make none\b",
    ],
    "B meta": [
        r"rather than let a reader", r"which we state rather than", r"we state (it|them|each) here",
        r"never mix them", r"belongs in the open", r"and we say so", r"would find anyway",
        r"both halves of that sentence", r"we state their provenance exactly",
        r"and no different treatment", r"we compute no rate", r"claim nothing about",
    ],
    "C auto-obiezione": [
        r"What this paper does not claim", r"and it does not isolate it cleanly",
        r"decides nothing", r"\bcautions\b", r"is not decidable", r"nothing for anyone to fix",
        r"part of that null", r"was therefore not designated", r"we report this as a limit",
        r"had failed, so it could not", r"no care at design time would have caught",
    ],
}


def testo(sez, da_head):
    if da_head:
        t = subprocess.run(["git", "show", f"HEAD:paper/sections/{sez}.tex"],
                           capture_output=True, text=True, cwd=RADICE).stdout
    else:
        t = open(os.path.join(RADICE, "paper", "sections", sez + ".tex"), errors="ignore").read()
    return re.sub(r"\s+", " ", re.sub(r"(?<!\\)%.*", "", t))


def conta(t):
    return {f: sum(len(re.findall(p, t, re.I)) for p in ps) for f, ps in FAMIGLIE.items()}


def main():
    tot_p = {f: 0 for f in FAMIGLIE}
    tot_d = {f: 0 for f in FAMIGLIE}
    print("  %-18s%8s%8s%9s%8s%9s%8s" % ("sezione", "A prima", "A dopo", "B prima", "B dopo",
                                          "C prima", "C dopo"))
    for s in SEZ:
        p, d = conta(testo(s, True)), conta(testo(s, False))
        for f in FAMIGLIE:
            tot_p[f] += p[f]; tot_d[f] += d[f]
        if sum(p.values()) or sum(d.values()):
            print("  %-18s%8d%8d%9d%8d%9d%8d" % (s, p["A ammissione"], d["A ammissione"],
                  p["B meta"], d["B meta"], p["C auto-obiezione"], d["C auto-obiezione"]))
    P, D = sum(tot_p.values()), sum(tot_d.values())
    print("  " + "-" * 60)
    print("  %-18s%8d%8d%9d%8d%9d%8d" % ("TOTALE", tot_p["A ammissione"], tot_d["A ammissione"],
          tot_p["B meta"], tot_d["B meta"], tot_p["C auto-obiezione"], tot_d["C auto-obiezione"]))
    if P:
        print("\n  complessivo: %d -> %d  (%+.0f%%)" % (P, D, 100.0 * (D - P) / P))

    # ONESTA' DEL NUMERO. Parte del materiale non e' sparito: e' stato spostato in appendice,
    # dove un revisore che vuole auditarlo lo trova senza incontrarlo nella narrazione. Contarlo
    # come rimosso sarebbe la stessa sovrastima che questo capitolo studia altrove.
    app = testo("12-appendice", False)
    spostati = [(e, len(re.findall(pat, app, re.I))) for e, pat in [
        ("timestamp della provenienza", r"1\.9\\%|27\.4\\%|73\.4\\%"),
        ("dipendenza dall'esito originale", r"not independent"),
        ("precedenza non provata", r"declared rather than proved"),
        ("soglia senza derivazione", r"without a derivation"),
    ]]
    print("\n  Non rimosso, RICOLLOCATO in appendice (Appendice C):")
    for e, n in spostati:
        print("    %-34s %d occorrenze" % (e, n))
    print("    -> il corpo scende a %d; il materiale d'audit resta, fuori dalla narrazione." % D)
    return D, P


if __name__ == "__main__":
    if "--autotest" in sys.argv:
        casi = [("we cannot verify this", "A ammissione"),
                ("we state it here rather than let a reader find it", "B meta"),
                ("the arm decides nothing", "C auto-obiezione")]
        ok = True
        for frase, fam in casi:
            c = conta(frase)
            buono = c[fam] >= 1 and sum(c.values()) == c[fam]
            ok &= buono
            print(f"  «{frase}» -> {fam}: {'ok' if buono else 'FALLITO ' + str(c)}")
        neutro = conta("The median run takes six turns on one service and four on the other.")
        buono = sum(neutro.values()) == 0
        ok &= buono
        print(f"  paragrafo neutro -> nessuna famiglia: {'ok' if buono else 'FALLITO ' + str(neutro)}")
        sys.exit(0 if ok else 1)
    main()
