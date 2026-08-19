#!/usr/bin/env python3
"""L'MDE per contrasto con la SD osservata, contro il bound unico dichiarato.

La card conclude «nessun contrasto colloca l'effetto fuori da una banda di circa +/-4,9pp».
Quel 4,9 viene dalla SD conservativa PRE-REGISTRATA (0,1167), calibrata sui dati di C1 su
due modelli e sul solo asse del trasporto. Le SD osservate in C2 vanno da 0,0037 a 0,2844,
quindi un bound unico non descrive nessuno degli otto contrasti: ne sovrastima due e ne
sottostima sei.

Trovato dal seggio metodologo del gauntlet sui risultati, 2026-08-15.

    MDE = (z(0,975) + z(0,80)) * SD / sqrt(K),  K = 45
"""
import math

Z = 1.959964 + 0.841621
K = 45
BOUND_DICHIARATO = 4.87            # da SD conservativa 0,1167, PREREGISTRAZIONE §7
SD_OSSERVATE = [                   # da results/SCOMPOSIZIONE-VARIANZA-2026-08-15.txt
    ("T1", "gpt-oss / trasporto",   0.1950),
    ("T2", "llama / trasporto",     0.1374),
    ("T3", "haiku / trasporto",     0.2844),
    ("T4", "sonnet / trasporto",    0.1232),
    ("T5", "gpt-oss / infrastr.",   0.1339),
    ("T6", "llama / infrastr.",     0.2481),
    ("T7", "haiku / infrastr.",     0.0037),
    ("T8", "sonnet / infrastr.",    0.0630),
]

if __name__ == "__main__":
    print("MDE per contrasto, con la SD osservata — contro il bound unico della card\n")
    print(f"  {'id':<5}{'contrasto':<24}{'SD oss':>9}{'MDE reale':>12}")
    sopra = []
    for tid, eti, sd in SD_OSSERVATE:
        mde = Z * sd / math.sqrt(K) * 100
        nota = "   sopra il bound" if mde > BOUND_DICHIARATO else ""
        if mde > BOUND_DICHIARATO:
            sopra.append(tid)
        print(f"  {tid:<5}{eti:<24}{sd:>9.4f}{mde:>11.2f}pp{nota}")
    lo = min(Z * sd / math.sqrt(K) * 100 for _, _, sd in SD_OSSERVATE)
    hi = max(Z * sd / math.sqrt(K) * 100 for _, _, sd in SD_OSSERVATE)
    print(f"\n  bound unico dichiarato nella card: {BOUND_DICHIARATO}pp")
    print(f"  contrasti il cui MDE reale lo supera: {len(sopra)} su 8 ({', '.join(sopra)})")
    print(f"  intervallo reale degli MDE: da {lo:.2f}pp a {hi:.2f}pp")
    print("\n  CONSEGUENZA. La frase «una banda di circa +/-4,9pp» non descrive questi dati:")
    print("  descrive il disegno pre-registrato. La formulazione che i dati sostengono e'")
    print("  per contrasto — «fuori dalla banda che la varianza di quel contrasto consente,")
    print("  e quella banda va da 0,15pp a 11,9pp» — che e' piu' debole e piu' vera.")
