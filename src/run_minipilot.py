#!/usr/bin/env python3
"""Mini-pilot: misura ICC e SD della pass-rate.

NON e' l'esperimento S1. Serve solo a stimare due parametri (ICC intra-binario e SD
della pass-rate tra run) che i due power analysis in dialectic.md hanno dovuto
ipotizzare invece di misurare. Con quei numeri si fissa la soglia pre-registrata.

Pipeline per ogni run:
  decomp/<prog>_flat.json  ->  agente (N turni, tool-calling)  ->  candidato C
  -> ricompilazione in Docker x86-64 -> M test -> pass_rate in [0,1]

Separazione host/container:
  - host: loop dell'agente (serve rete per l'API del modello)
  - container: ricompilazione ed esecuzione dei test (serve x86-64 Linux)
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

# La radice e' il progetto, non src/: i dati stanno in data/raw/ e il codice in src/.
ROOT = Path(__file__).resolve().parents[1]
# ...e il codice si importa da src/, che e' dove sta questo file. Due costanti,
# perche' unirle rompe l'una o l'altra e l'errore arriva a meta' raccolta.
SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC / "harness"))
sys.path.insert(0, str(SRC / "llm"))

from agent_loop import run_agent  # noqa: E402
from ghidra_static_client import GhidraStaticClient  # noqa: E402
from monolithic import run_monolithic  # noqa: E402
from best_of_n import run_best_of_n  # noqa: E402

DOCKER_IMAGE = "s1-minipilot:smoke"
def extract_c_source(text: str) -> str:
    """Estrae il codice C da una risposta che puo' contenere prosa o fence markdown.

    Osservato nel run v2 (2026-08-09): il modello a volte risponde con
    "**Solution Explanation** ... ```c <codice> ```" invece del solo sorgente. Scrivere
    quel testo tale e quale in candidate.c produce un errore di compilazione, che
    verrebbe registrato come pass_rate=0 — cioe' misureremmo la conformita' al formato
    invece della capacita' di reverse engineering. L'estrazione e' quindi parte della
    misura corretta, non un aiuto all'agente.
    """
    if not text:
        return ""
    # 1) blocco fenced ```c ... ``` (o ``` ... ```)
    if "```" in text:
        parts = text.split("```")
        for i in range(1, len(parts), 2):
            block = parts[i]
            first_nl = block.find("\n")
            if first_nl != -1:
                lang = block[:first_nl].strip().lower()
                body = block[first_nl + 1:]
            else:
                lang, body = "", block
            if lang in ("c", "cpp", "") and ("#include" in body or "int main" in body):
                return body.strip() + "\n"
    # 2) nessun fence: taglia la prosa iniziale fino alla prima riga di codice C
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        s = line.strip()
        if s.startswith("#include") or s.startswith("#define") or s.startswith("int main"):
            return "\n".join(lines[idx:]).strip() + "\n"
    return text.strip() + "\n"


def compile_and_test(candidate_c: str, tests: list, workdir: Path) -> dict:
    """Ricompila il candidato in Docker x86-64 ed esegue gli M test.

    Ritorna dict con pass_rate, n_passed, n_tests, compiled (bool), detail.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    src = workdir / "candidate.c"
    src.write_text(candidate_c)
    (workdir / "tests.json").write_text(json.dumps({"tests": tests}))

    runner = workdir / "run_tests.py"
    runner.write_text(
        "import json,subprocess,sys\n"
        "spec=json.load(open('/w/tests.json'))\n"
        "r=subprocess.run(['clang','-O0','-o','/tmp/cand','/w/candidate.c'],"
        "capture_output=True,text=True)\n"
        "if r.returncode!=0:\n"
        "    print(json.dumps({'compiled':False,'n_passed':0,"
        "'stderr':r.stderr[:2000]})); sys.exit(0)\n"
        "p=0; det=[]\n"
        "for t in spec['tests']:\n"
        "    try:\n"
        "        x=subprocess.run(['/tmp/cand']+[str(a) for a in t.get('args',[])],"
        "input=t.get('stdin',''),capture_output=True,text=True,timeout=10)\n"
        "        ok = x.stdout==t['expected_stdout']\n"
        "    except Exception as e:\n"
        "        ok=False; det.append(str(e)[:100])\n"
        "    p+= 1 if ok else 0\n"
        "print(json.dumps({'compiled':True,'n_passed':p,'detail':det[:3]}))\n"
    )

    try:
        r = subprocess.run(
            ["docker", "run", "--rm", "--platform", "linux/amd64",
             "-v", f"{workdir}:/w", "--entrypoint", "python3", DOCKER_IMAGE, "/w/run_tests.py"],
            capture_output=True, text=True, timeout=300,
        )
        out = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e:  # noqa: BLE001
        return {"pass_rate": 0.0, "n_passed": 0, "n_tests": len(tests),
                "compiled": False, "detail": f"harness_error: {type(e).__name__}: {e}"}

    n_passed = out.get("n_passed", 0)
    return {
        "pass_rate": n_passed / len(tests) if tests else 0.0,
        "n_passed": n_passed,
        "n_tests": len(tests),
        "compiled": out.get("compiled", False),
        "detail": out.get("stderr", "") or str(out.get("detail", "")),
    }


def write_trajectory(res, prog: str, run_id: int, outdir: Path) -> str:
    """Scrive il log per-turno di un run agentico in JSONL.

    Chiude il buco piu' grave rilevato in review: il meccanismo che il paper
    afferma ("i turni recuperano informazione") e' una tesi su COSA fa l'agente
    turno per turno, ma era inferita da pass-rate aggregati. Senza questi record
    non e' verificabile ne' dai lettori ne' da noi quale frazione del binario
    l'agente abbia effettivamente visto.

    Una riga per turno con: tool offerti, tool chiamati con argomenti, se la
    risposta era vuota, stop reason, token e costo.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{prog}_r{run_id}.jsonl"
    with path.open("w") as fh:
        for t in getattr(res, "turns", []) or []:
            fh.write(json.dumps({
                "turn": t.turn,
                "tools_offered": list(getattr(t, "tools_offered", []) or []),
                # Si propaga OGNI chiave, non solo name e arguments: il flag
                # `scartata_da_ablazione` viveva nel turn_log e si perdeva qui, cosi' che una
                # traiettoria non poteva distinguere una chiamata eseguita da una rifiutata.
                # Il controllo negativo della successione 08 avrebbe fermato una raccolta sana.
                "tool_calls": [dict(c) for c in (t.tool_calls or [])],
                "n_tool_results": len(t.tool_results or []),
                "response_chars": len(t.response_text or ""),
                "stop_reason": getattr(t, "stop_reason", None),
                "infra_failure": bool(getattr(t, "infra_failure", False)),
                "usage": dict(t.usage or {}),
                "cost_usd": getattr(t, "cost_usd", 0.0),
            }) + "\n")
    return str(path.relative_to(outdir.parent.parent)) if outdir.parent.parent in path.parents else str(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=2, help="run indipendenti per binario")
    ap.add_argument("--turns", type=int, default=4)
    ap.add_argument("--model", default="databricks-gpt-oss-120b")
    ap.add_argument("--provider", default="databricks")
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--mono-extra", default="",
                    help="istruzione aggiuntiva al prompt monolitico (controllo esplorativo: "
                         "verifica se un vincolo di formulazione spiega un divario fra bracci)")
    ap.add_argument("--tool-protocol", default="native", choices=["native", "text"],
                    help="come viaggiano le chiamate ai tool: campo `tools` nativo, oppure "

                         "righe TOOL_CALL nel testo (per endpoint che rifiutano il nativo)")
    ap.add_argument("--max-calls-per-turn", type=int, default=None,
                    help="ablazione: esegue solo le prime N tool call di ogni turno nel ramo "
                         "nativo e registra le scartate. Con N=1 il nativo ha il vincolo che "
                         "il testuale ha per costruzione, e i due bracci differiscono per il "
                         "solo protocollo. Default: nessun limite.")
    ap.add_argument("--temperature", type=float, default=None)
    ap.add_argument("--limit", type=int, default=None, help="usa solo i primi N binari")
    ap.add_argument("--bon", type=int, default=0,
                    help="braccio best-of-N: numero di campioni paralleli (0 = disattivato)")
    ap.add_argument("--only", default=None,
                    help="regex/prefisso per selezionare i binari (es. 'prog(1[6-9]|[2-5][0-9]|60)')")
    ap.add_argument("--mono-funcs", type=int, default=6,
                    help="funzioni max nel prompt monolitico (controllo di capacita di contesto)")
    ap.add_argument("--mono-chars", type=int, default=40000,
                    help="caratteri max nel prompt monolitico")
    ap.add_argument("--mono-pad-full", action="store_true",
                    help="riempie il prompt troncato con testo dichiarato irrilevante fino "
                         "alla lunghezza del dump intero: separa l'effetto della LUNGHEZZA "
                         "da quello dell'INFORMAZIONE nel controllo del cap")
    ap.add_argument("--mono-select", default="native", choices=["native", "callgraph"],
                    help="regola di selezione delle funzioni per il braccio monolitico: "
                         "native = ordine del dump (default, usato in tutto il paper); "
                         "callgraph = main e i suoi callee, euristica a costo zero")
    ap.add_argument("--corpus", default="data/raw/corpus",
                    help="cartella dei sorgenti e dei .tests.json (corpus | corpus_real)")
    ap.add_argument("--decomp", default="data/raw/decomp",
                    help="cartella dei JSON decompilati (decomp | decomp_stripped)")
    ap.add_argument("--out", default="results/results.csv")
    ap.add_argument("--etichetta", default=None,
                    help="nome del modello indipendente dall'endpoint, es. "
                         "'claude-haiku-4-5'. Lo stesso modello ha id diversi sui "
                         "due cloud e la cella appaiata li deve riconoscere uguali.")
    ap.add_argument("--binari-file", default=None,
                    help="file con un binary_id per riga: l'elenco CONGELATO. "
                         "'i primi 45' non e' una specifica, e' un ordinamento.")
    args = ap.parse_args()

    decomps = sorted((ROOT / args.decomp).glob("*_flat.json"))
    if args.only:
        import re
        pat = re.compile(args.only)
        decomps = [d for d in decomps if pat.match(d.stem)]
    if args.limit:
        decomps = decomps[:args.limit]

    if args.binari_file:
        ammessi = {x.split('#')[0].strip()
                   for x in open(args.binari_file).read().splitlines()
                   if x.split('#')[0].strip()}
        if not ammessi:
            sys.exit(f"{args.binari_file} non contiene nessun binary_id (solo commenti o "
                     f"righe vuote). Un elenco vuoto non e' un elenco: passerebbe la guardia "
                     f"e produrrebbe zero run senza che niente lo dica.")
        prima = len(decomps)
        decomps = [d for d in decomps if d.stem.replace('_flat','') in ammessi]
        mancanti = ammessi - {d.stem.replace('_flat','') for d in decomps}
        if mancanti:
            sys.exit(f"{len(mancanti)} binari dell'elenco congelato non hanno un "
                     f"decompilato: {sorted(mancanti)[:5]}. Un braccio che gira su un "
                     f"sottoinsieme silenzioso non e' il braccio dichiarato.")
        print(f'elenco congelato: {len(decomps)} binari su {prima} disponibili')
    if not decomps:
        print(f"Nessun file *_flat.json in {args.decomp}/.")
        return 1

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not out_path.exists()
    fh = out_path.open("a", newline="")
    w = csv.writer(fh)
    if new_file:
        w.writerow(["binary_id", "run_id", "pass_rate", "n_passed", "n_tests",
                    "compiled", "infra_failure", "candidate_chars", "n_turns",
                    "cost_usd", "in_tokens", "out_tokens", "model", "provider",
                    "elapsed_s", "error", "timestamp",

                    # C2: la cella e' (modello x infrastruttura x trasporto). Scritte
                    # esplicitamente e non dedotte dal nome del file: un nome si rinomina,
                    # una colonna no.
                    "modello", "infra", "trasporto"])

    total_cost = 0.0
    for dj in decomps:
        prog = dj.stem.replace("_flat", "")
        tests_file = ROOT / args.corpus / f"{prog}.tests.json"
        if not tests_file.exists():
            print(f"SKIP {prog}: manca {tests_file.name}")
            continue
        tests = json.loads(tests_file.read_text())["tests"]
        client = GhidraStaticClient(dj)

        for run_id in range(1, args.runs + 1):
            t0 = time.time()
            err = ""
            infra = False
            cand = ""
            cost = in_tok = out_tok = 0
            # Braccio best-of-N: valutato a parte perche' produce PIU' candidati e
            # due metriche distinte (oracle_best = copertura, mean = selezione casuale).
            if args.bon:
                samples = run_best_of_n(
                    binary_id=prog, n_samples=args.bon, model=args.model,
                    provider=args.provider, max_tokens=args.max_tokens,
                    ghidra_client=client,
                )
                rates = []
                cost = 0.0
                for si, (temp, sr) in enumerate(samples):
                    cost += sr.total_cost_usd or 0.0
                    src = extract_c_source(sr.candidate_source or "")
                    if src.strip():
                        t = compile_and_test(
                            src, tests,
                            ROOT / "results" / "workbon" / f"{prog}_r{run_id}_s{si}")
                        rates.append(t["pass_rate"])
                    else:
                        rates.append(0.0)
                best = max(rates) if rates else 0.0
                mean = sum(rates) / len(rates) if rates else 0.0
                total_cost += cost
                w.writerow([prog, run_id, f"{best:.4f}", "", len(tests), True, False,
                            0, f"bon{args.bon}", f"{cost:.6f}", 0, 0,
                            args.model, args.provider, f"{time.time()-t0:.1f}",
                            f"oracle_best={best:.4f};mean={mean:.4f};rates={rates}",
                            time.strftime("%Y-%m-%dT%H:%M:%S"),

                            args.etichetta or args.model, args.provider, args.tool_protocol])
                fh.flush()
                print(f"{prog} run{run_id}: best-of-{args.bon} oracle={best:.2f} "
                      f"mean={mean:.2f} cost=${cost:.4f}")
                continue

            try:
                if args.turns == 0:
                    # Baseline monolitico: stessa informazione, zero iterazione.
                    res = run_monolithic(
                        binary_id=prog, model=args.model, provider=args.provider,
                        max_tokens=args.max_tokens, temperature=args.temperature,
                        ghidra_client=client,
                        max_funcs=args.mono_funcs, max_chars=args.mono_chars,
                        select=args.mono_select,
                        # Controllo lunghezza-vs-informazione: il bersaglio per binario
                        # lo calcola _build_context, che sa come il braccio non troncato
                        # assembla il proprio blocco.
                        pad_to_chars=1 if args.mono_pad_full else 0,
                        extra_system=args.mono_extra,
                    )
                else:
                    res = run_agent(
                        binary_id=prog, n_turns=args.turns, model=args.model,
                        provider=args.provider, max_tokens=args.max_tokens,
                        temperature=args.temperature, ghidra_client=client,
                        tool_protocol=args.tool_protocol,
                        max_calls_per_turn=args.max_calls_per_turn,
                    )
                cand = res.candidate_source or ""
                if args.turns > 0:
                    # La sottocartella deriva dal nome del file di output, non dal solo
                    # conteggio di turni: lo Studio 02 gira sugli STESSI nomi di programma
                    # dello Studio 01 (prog01..prog60, corpus a intensita' 2), quindi una
                    # cartella "N12" condivisa avrebbe fatto sovrascrivere le traiettorie
                    # di uno studio con quelle dell'altro, in silenzio e senza errori.
                    tag = Path(args.out).stem or f"N{args.turns}"
                    write_trajectory(res, prog, run_id,
                                     ROOT / "results" / "trajectories" / tag)
                infra = bool(getattr(res, "infra_failure", False))
                cost = getattr(res, "total_cost_usd", 0.0) or 0.0
                in_tok = getattr(res, "total_tokens_in", 0) or 0
                out_tok = getattr(res, "total_tokens_out", 0) or 0
                err = getattr(res, "error", "") or ""
            except Exception as e:  # noqa: BLE001 -- un run fallito non ferma lo sweep
                err = f"{type(e).__name__}: {e}"

            cand = extract_c_source(cand)
            if cand.strip():
                # La cartella di compilazione porta il TAG DELLA CELLA, non solo programma e
                # run: senza, sedici celle condividono 360 directory e due driver concorrenti
                # possono valutare il candidato l'uno dell'altro senza alzare alcun flag.
                # Lo stesso ragionamento era gia' applicato alle traiettorie venti righe sopra
                # ("in silenzio e senza errori") e non a questa. Vedi SUCCESSIONE-07.
                cella_tag = Path(args.out).stem or f"N{args.turns}"
                tr = compile_and_test(
                    cand, tests,
                    ROOT / "results" / "workv3" / cella_tag / f"{prog}_r{run_id}")
            else:
                tr = {"pass_rate": 0.0, "n_passed": 0, "n_tests": len(tests),
                      "compiled": False, "detail": "nessun candidato prodotto"}

            total_cost += cost
            w.writerow([prog, run_id, f"{tr['pass_rate']:.4f}", tr["n_passed"], tr["n_tests"],
                        tr["compiled"], infra, len(cand), args.turns,
                        f"{cost:.6f}", in_tok, out_tok, args.model, args.provider,
                        f"{time.time()-t0:.1f}", (err or tr.get("detail", ""))[:300],
                        time.strftime("%Y-%m-%dT%H:%M:%S"),

                        args.etichetta or args.model, args.provider, args.tool_protocol])
            fh.flush()
            flag = " [INFRA_FAIL]" if infra else ""
            print(f"{prog} run{run_id}: pass_rate={tr['pass_rate']:.2f} "
                  f"({tr['n_passed']}/{tr['n_tests']}) compiled={tr['compiled']} "
                  f"cost=${cost:.4f}{flag}")

    fh.close()
    print(f"\nCosto totale: ${total_cost:.4f}  ->  {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
