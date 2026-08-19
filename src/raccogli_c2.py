#!/usr/bin/env python3
"""Driver delle 16 celle di C2: 4 modelli x 2 infrastrutture x 2 trasporti.

Lo stesso modello ha id diversi sui due cloud, e la cella appaiata li deve riconoscere come
lo stesso: per questo ogni riga porta `--etichetta`, che e' il nome indipendente
dall'endpoint. Dedurlo dall'id a valle funzionerebbe finche' un id non cambia.

    python3 src/raccogli_c2.py --dry-run          # stampa i comandi, non esegue
    python3 src/raccogli_c2.py --cella gpt-oss-120b/bedrock/text
    python3 src/raccogli_c2.py                     # tutte le celle, in sequenza

Un rifiuto di piattaforma non e' un fallimento di capacita': il primo si completa
riprovando, il secondo no. Le celle non eseguibili si dichiarano in NON_ESEGUIBILI con il
messaggio verbatim, e in questo studio sono un RISULTATO.
"""
import argparse
import os
import subprocess
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
sys.path.insert(0, QUI)
# In testa e non dentro main(): dalla successione 09 anche `comando()` chiede a questo modulo
# dove va il file di una cella, e `comando()` e' definita molto prima del punto in cui
# l'import stava. Un import locale in una funzione non e' visibile in un'altra.
import completa_celle as cc  # noqa: E402

# etichetta -> {infrastruttura: (provider, id del modello su quell'endpoint)}
ROSTER = {
    "gpt-oss-120b": {
        "databricks": ("databricks", "databricks-gpt-oss-120b"),
        "bedrock": ("bedrock", "openai.gpt-oss-120b-1:0"),
    },
    "llama-3.3-70b": {
        "databricks": ("databricks", "databricks-meta-llama-3-3-70b-instruct"),
        "bedrock": ("bedrock", "us.meta.llama3-3-70b-instruct-v1:0"),
    },
    "claude-haiku-4-5": {
        "databricks": ("databricks", "databricks-claude-haiku-4-5"),
        "bedrock": ("bedrock", "us.anthropic.claude-haiku-4-5-20251001-v1:0"),
    },
    "claude-sonnet-4-5": {
        "databricks": ("databricks", "databricks-claude-sonnet-4-5"),
        "bedrock": ("bedrock", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"),
    },
}
TRASPORTI = ["native", "text"]

# --- braccio ESPLORATIVO, emendamento 02 -------------------------------------------
# Separato dal ROSTER, non unito: celle() alimenta la famiglia confermativa dei dieci test,
# e un esplorativo che vi entrasse cambierebbe m a dati parzialmente visti, spostando ogni
# soglia di Holm. Si raggiunge solo con --esplorativo, mai per default.
ROSTER_ESPLORATIVO = {
    "gpt-oss-120b":  {"azure": ("azure", "gpt-oss-120b")},
    "llama-3.3-70b": {"azure": ("azure", "llama-3.3-70b-instruct")},
}

# Celle che un endpoint rifiuta per protocollo, non per capacita'. Si compila DOPO aver
# incontrato il rifiuto, col messaggio verbatim, e la cella non si ritenta.
NON_ESEGUIBILI: dict[tuple[str, str, str], str] = {
    # Emendamento 02. Azure serve Llama 3.3 70B, e il censimento lo dichiara sano: turno 1 con
    # un tool passa, turno 2 con una storia a una chiamata passa. Rifiuta pero' una storia che
    # contiene DUE tool call nello stesso messaggio assistant, che un ciclo agentico produce
    # appena il modello decide di chiamarne due insieme. Non e' un fallimento di capacita': si
    # ripresenterebbe identico a ogni tentativo.
    ("llama-3.3-70b", "azure", "native"):
        "400 UnsupportedToolUse: This model does not support more than one tool call at this time",
    ("llama-3.3-70b", "azure", "text"):
        "400 UnsupportedToolUse (stesso rifiuto: il trasporto testuale non cambia il vincolo "
        "sulla storia inviata al modello)",
}

RUNS = 8
TURNS = 12
MAX_TOKENS = 8192
ELENCO = os.path.join(RADICE, "configs", "binari_holdout.txt")


def preflight(esplorativo=False):
    """Una chiamata minima per provider, PRIMA di qualunque cella.

    Le credenziali di Bedrock stanno in AWS_PROFILE e quelle di Databricks in un profilo
    del CLI: sono due meccanismi diversi, e nessuno dei due si annuncia mancante finche'
    non lo usi. Senza questo controllo le otto celle Databricks girerebbero per ore e la
    nona morirebbe su NoCredentialsError -- il costo e' gia' speso e il braccio e' a meta'.
    """
    sys.path[:0] = [os.path.join(QUI, "llm")]
    from llm_client import chat  # noqa: E402
    sonde = ({"azure": "gpt-oss-120b"} if esplorativo else
             {"databricks": "databricks-gpt-oss-120b", "bedrock": "openai.gpt-oss-120b-1:0"})
    guasti = []
    for provider, modello in sonde.items():
        try:
            r = chat([{"role": "user", "content": "Rispondi con la sola parola OK."}],
                     model=modello, provider=provider, max_tokens=16, temperature=0.0)
            print(f"  preflight {provider:11s} OK  (${r.cost_usd:.6f})")
        except Exception as e:
            guasti.append((provider, f"{type(e).__name__}: {e}"[:160]))
            print(f"  preflight {provider:11s} GUASTO  {type(e).__name__}: {str(e)[:90]}")
    if guasti:
        print("\n  Credenziali: Databricks usa un profilo del CLI (default <profilo-databricks>), Bedrock\n"
              "  usa AWS_PROFILE. Esporta quello giusto ed esegui di nuovo:\n"
              "    export AWS_PROFILE=<profilo-bedrock> AWS_REGION=us-east-1")
    return guasti


def celle(esplorativo=False):
    """Le celle CONFERMATIVE. `esplorativo` restituisce invece il braccio dell'emendamento 02,
    che non entra nella famiglia dei dieci test e non muove nessuna soglia."""
    r = ROSTER_ESPLORATIVO if esplorativo else ROSTER
    for eti in r:
        for infra in r[eti]:
            for trasporto in TRASPORTI:
                yield eti, infra, trasporto


def comando(eti, infra, trasporto, elenco, runs, suffisso, braccio="confermativo"):
    """`suffisso` isola le riesecuzioni: results/ e' append-only e un file non si riscrive.
    `elenco` e `runs` restringono la ripresa ai soli binari carenti.

    IL PERCORSO NON SI COSTRUISCE QUI. Fino alla successione 09 questa funzione ripeteva la
    regola dei percorsi che vive in `completa_celle.percorso_cella`, e la duplicazione ha gia'
    morso due volte: il driver dell'ablazione che chiedeva la completezza al braccio
    confermativo, e il primo CSV dell'ablazione nato `_redo2` nella catena di un altro braccio.
    Una regola, un posto.

    Ogni braccio va in una SOTTOCARTELLA e con un PREFISSO proprio. La sottocartella serve
    perche' analyze_c2.py e' congelato e fa glob non ricorsivo su results/*.csv: un file li'
    dentro finirebbe in `lungo()` e contaminerebbe T9 e T10. Il prefisso serve perche'
    run_minipilot deriva il tag di workdir e traiettorie dallo STEM del file, non dal percorso:
    stesso nome in cartelle diverse ⇒ stesso tag ⇒ traiettorie sovrascritte."""
    r = ROSTER_ESPLORATIVO if braccio == "esplorativo" else ROSTER
    provider, model_id = r[eti][infra]
    out = os.path.relpath(cc.percorso_cella(eti, infra, trasporto, suffisso, braccio), RADICE)
    cmd = [sys.executable, os.path.join(QUI, "run_minipilot.py"),
           "--model", model_id, "--provider", provider, "--etichetta", eti,
           "--tool-protocol", trasporto, "--runs", str(runs), "--turns", str(TURNS),
           "--max-tokens", str(MAX_TOKENS), "--temperature", "0.0",
           "--binari-file", elenco, "--out", out]
    if braccio == "ablazione":
        cmd += ["--max-calls-per-turn", "1"]
    return cmd, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cella", default=None, help="etichetta/infra/trasporto")
    ap.add_argument("--esplorativo", action="store_true",
                    help="il braccio Azure dell'emendamento 02. NON entra nella famiglia dei "
                         "dieci test: m resta 10 e nessuna soglia si muove.")
    ap.add_argument("--ablazione", action="store_true",
                    help="il braccio della successione 08: nativo forzato a UNA chiamata per "
                         "turno, per separare il cambio di protocollo dalla perdita del "
                         "raggruppamento. Esplorativo, in results/ablazione/, e NON entra "
                         "nella famiglia dei dieci test.")
    ap.add_argument("--riraccolta", action="store_true",
                    help="il braccio della successione 09: le stesse sedici celle "
                         "confermative, raccolte da capo con la workdir isolata per cella "
                         "(EMENDAMENTO-06). Va in results/riraccolta/ con prefisso c2r_, "
                         "quindi e' invisibile all'analisi congelata e non sovrascrive le "
                         "traiettorie dell'originale. NON entra nella famiglia dei dieci "
                         "test: la famiglia e' gia' stata spesa una volta.")
    ap.add_argument("--solo-infra", default=None, choices=["databricks", "bedrock", "azure"],
                    help="restringe a un'infrastruttura, per farne girare due in parallelo. "
                         "Il carico per endpoint NON aumenta: in sequenza uno lavora e l'altro "
                         "e' fermo, partizionati ne lavora uno per ciascuno.")
    a = ap.parse_args()

    # I bracci si escludono. Due flag booleani veri insieme sceglierebbero in silenzio, ed e'
    # la ragione per cui la successione 09 li ha uniti in un parametro solo.
    attivi = [k for k, v in (("esplorativo", a.esplorativo), ("ablazione", a.ablazione),
                             ("riraccolta", a.riraccolta)) if v]
    if len(attivi) > 1:
        sys.exit(f"bracci incompatibili: {', '.join(attivi)}. Se ne sceglie uno.")
    braccio = attivi[0] if attivi else "confermativo"

    scelte = list(celle(a.esplorativo))
    if a.riraccolta:
        print(f"  ri-raccolta: {len(scelte)} celle confermative, workdir isolata per cella, "
              f"in results/riraccolta/ — i quattro criteri di lettura sono congelati in "
              f"analysis/confronto_riraccolta.py")
    if a.ablazione:
        # Il braccio di ablazione NON e' il roster intero: e' definito nella successione 08
        # come i soli modelli che raggruppano davvero le chiamate (haiku 1,437 per turno,
        # sonnet 1,332; gli altri due sono a 1,000 esatto e l'ablazione non toglierebbe
        # nulla), sul solo trasporto nativo — sul testuale il vincolo c'e' gia' per
        # costruzione, e ripeterlo raccoglierebbe un duplicato pagandolo.
        #
        # Il filtro sta qui e non nella riga di comando perche' un `--ablazione` nudo
        # genererebbe sedici celle per circa $140, sforando il tetto: e' una guardia contro
        # un errore che costa, non una comodita'.
        RAGGRUPPANO = {"claude-haiku-4-5", "claude-sonnet-4-5"}
        scelte = [c for c in scelte if c[0] in RAGGRUPPANO and c[2] == "native"
                  and c[1] == "databricks"]
        print(f"  ablazione: {len(scelte)} celle (i due modelli che raggruppano, "
              f"nativo, una sola infrastruttura — la stima di costo della "
              f"successione 08 e' su queste)")
    if a.solo_infra:
        scelte = [c for c in scelte if c[1] == a.solo_infra]
        print(f"  partizione: {len(scelte)} celle su {a.solo_infra}")
    if a.cella:
        parti = tuple(a.cella.split("/"))
        if parti not in scelte:
            sys.exit(f"cella {a.cella!r} non nel roster. Disponibili:\n  " +
                     "\n  ".join("/".join(c) for c in scelte))
        scelte = [parti]

    if not a.dry_run:
        guasti = preflight(a.esplorativo)
        if guasti:
            sys.exit(f"\n  {len(guasti)} provider non raggiungibile/i: non parto. "
                     f"Un braccio a meta' costa piu' di un braccio non iniziato.")

    fatte, saltate, fallite = 0, 0, 0
    for eti, infra, trasporto in scelte:
        chiave = (eti, infra, trasporto)
        if chiave in NON_ESEGUIBILI:
            print(f"  SALTO {eti}/{infra}/{trasporto} — NON ESEGUIBILE: "
                  f"{NON_ESEGUIBILI[chiave]}")
            saltate += 1
            continue
        # Una cella e' completa quando ogni binario ha RUNS run VALIDE, non quando il file
        # esiste. Un CSV interrotto a meta' esiste, e saltarlo lo lascerebbe corto per
        # sempre -- e un braccio parziale e' peggio di un braccio assente, perche' la media
        # su un prefisso stima i binari facili.
        #
        # Il controllo vale ANCHE in dry-run. Prima della successione 09 il dry-run usciva
        # qui sopra e stampava un comando per ogni cella, comprese quelle che la raccolta
        # vera avrebbe saltato: mostrava sedici comandi dove ne sarebbero partiti zero. Un
        # dry-run che non prevede il salto e' inutile esattamente nel momento in cui serve,
        # cioe' prima di spendere.
        _, manca = cc.deficit(eti, infra, trasporto, braccio)
        if not manca:
            print(f"  CHIUSA gia' {eti}/{infra}/{trasporto}")
            saltate += 1
            continue
        if a.dry_run:
            suffisso = cc.prossimo_suffisso(eti, infra, trasporto, braccio)
            cmd, out = comando(eti, infra, trasporto, ELENCO, max(manca.values()),
                               suffisso, braccio)
            print(f"  [{len(manca)} binari carenti] {' '.join(cmd)}")
            fatte += 1
            continue
        suffisso = cc.prossimo_suffisso(eti, infra, trasporto, braccio)
        if suffisso:
            elenco = os.path.join(RADICE, ".sorveglianza", f"manca_{eti}_{infra}_{trasporto}.txt")
            os.makedirs(os.path.dirname(elenco), exist_ok=True)
            with open(elenco, "w") as f:
                f.write("\n".join(sorted(manca)) + "\n")
            deficit_max = max(manca.values())
            print(f"  RIPRESA {eti}/{infra}/{trasporto}: {len(manca)} binari carenti, "
                  f"{deficit_max} run each -> suffisso {suffisso!r}")
        else:
            elenco, deficit_max = ELENCO, RUNS
        cmd, out = comando(eti, infra, trasporto, elenco, deficit_max, suffisso, braccio)
        print(f"\n=== {eti} / {infra} / {trasporto} -> {out} ===")
        t0 = time.time()
        r = subprocess.run(cmd, cwd=RADICE)
        # L'exit code NON si maschera: un braccio fallito che prosegue in silenzio produce
        # un CSV parziale che l'analisi poi rifiuta, ma solo dopo che il tempo e' speso.
        if r.returncode != 0:
            print(f"  cella FALLITA con exit={r.returncode} dopo {time.time()-t0:.0f}s")
            fallite += 1
        else:
            fatte += 1

    print(f"\n  {fatte} celle completate, {saltate} saltate, {fallite} fallite")
    return 1 if fallite else 0


if __name__ == "__main__":
    sys.exit(main())
