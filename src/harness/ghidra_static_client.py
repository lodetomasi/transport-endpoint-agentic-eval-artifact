"""Client Ghidra "statico": stessa interfaccia di GhidraMCPClient, ma servita da un
JSON prodotto da Ghidra headless (ghidra_scripts/DecompileAll.py) invece che dal server
HTTP di GhidraMCP.

Motivo: il server HTTP di GhidraMCP e' un plugin della GUI di Ghidra e non viene
attivato da `analyzeHeadless` (upstream issue LaurieWired/GhidraMCP#75). Pilotarlo
richiederebbe la GUI sotto Xvfb, che e' un problema di scripting non risolto e non
necessario: per l'esperimento serve che l'agente possa *chiedere* le stesse
informazioni (lista funzioni, decompilato, stringhe) in piu' turni, non che quelle
informazioni arrivino da un server vivo.

Differenza di sostanza rispetto a GhidraMCP, da dichiarare nel paper: la
decompilazione e' pre-calcolata una volta per binario invece che on-demand. L'agente
mantiene il controllo su COSA guardare e QUANDO (il loop multi-turno e' preservato),
ma non puo' rinominare simboli o modificare il database Ghidra tra un turno e l'altro.
Per la misura di ICC/SD e per il confronto tra budget di turni questo e' equivalente;
per un claim su "l'agente migliora il proprio database" non lo sarebbe.
"""
from __future__ import annotations

import json
from pathlib import Path


class GhidraStaticError(RuntimeError):
    pass


class GhidraStaticClient:
    """Serve i dati di un binario decompilato da Ghidra headless."""

    def __init__(self, decomp_json: str | Path):
        self.path = Path(decomp_json)
        if not self.path.exists():
            raise GhidraStaticError(f"decomp json non trovato: {self.path}")
        self.data = json.loads(self.path.read_text())
        self._by_name = {f["name"]: f for f in self.data.get("functions", [])}

    # --- stessa interfaccia di GhidraMCPClient ---

    def list_functions(self) -> list[str]:
        out = []
        for f in self.data.get("functions", []):
            out.append(f"{f['name']} @ {f['entry_point']} (size={f['size']})")
        return out

    def decompile_function(self, name: str) -> str:
        f = self._by_name.get(name)
        if f is None:
            avail = ", ".join(sorted(self._by_name)[:20])
            raise GhidraStaticError(f"funzione {name!r} non trovata. Disponibili: {avail}")
        if not f.get("decompiled"):
            raise GhidraStaticError(
                f"decompilazione non riuscita per {name!r}: {f.get('error', 'ignoto')}")
        return f["decompiled"]

    def get_function_xrefs(self, name: str, offset: int = 0, limit: int = 100) -> list[str]:
        # Non disponibile nel dump statico: dichiarato esplicitamente invece di
        # restituire silenziosamente una lista vuota (che l'agente leggerebbe come
        # "nessun chiamante", un'informazione falsa).
        raise GhidraStaticError(
            "xrefs non disponibili nel dump statico; usa list_functions e decompile_function")

    def list_strings(self, offset: int = 0, limit: int = 2000,
                     filter: str | None = None) -> list[str]:
        items = self.data.get("strings", [])
        items = [s for s in items if not str(s.get("address", "")).startswith(".strtab")]
        vals = [f"{s['address']}: {s['value']}" for s in items]
        if filter:
            vals = [v for v in vals if filter.lower() in v.lower()]
        # La TABELLA DEI SIMBOLI non deve raggiungere il modello: la pre-registrazione lo
        # dichiara gia' fra le decisioni vincolanti ("tabella dei simboli rimossa"), ma la
        # rimozione copriva il binario e non le stringhe estratte da Ghidra. Emendamento 03.
        #
        # In .strtab stanno il nome del file sorgente (`prog36_pascal_triangle.c`, 61 binari
        # su 61) E i nomi delle funzioni originali (`quicksort`, `parse_expr`): entrambi
        # nominano l'algoritmo da ricostruire, ed e' lo stesso difetto che in C1 porto' il
        # baseline a 0,894.
        #
        # Il filtro e' sulla SEZIONE, non su una lista di parole: toglie cio' che il linker ha
        # lasciato e nient'altro. Le stringhe di .rodata restano tutte, comprese quelle che
        # descrivono il comportamento (`NOT_PALINDROME`, `LINES=%ld WORDS=%ld`) -- sono
        # l'output osservabile che il candidato deve riprodurre, e toglierle renderebbe il
        # compito impossibile invece che pulito.
        return vals[offset:offset + limit]

    def disassemble_function(self, address: str) -> list[str]:
        raise GhidraStaticError(
            "disassembly non disponibile nel dump statico; usa decompile_function")

    def call(self, tool_name: str, arguments: dict) -> str:
        """Dispatch identico a GhidraMCPClient.call."""
        try:
            if tool_name == "list_functions":
                return "\n".join(self.list_functions())
            if tool_name == "decompile_function":
                return self.decompile_function(arguments["name"])
            if tool_name == "list_strings":
                return "\n".join(self.list_strings(
                    offset=arguments.get("offset", 0),
                    limit=arguments.get("limit", 200),
                    filter=arguments.get("filter"),
                ))
            if tool_name == "get_function_xrefs":
                return "\n".join(self.get_function_xrefs(arguments["name"]))
            if tool_name == "disassemble_function":
                return "\n".join(self.disassemble_function(arguments["address"]))
            raise GhidraStaticError(f"tool sconosciuto: {tool_name}")
        except GhidraStaticError as e:
            # L'errore torna all'agente come output del tool: e' informazione
            # legittima per lui (puo' correggere la chiamata), non un crash.
            return f"ERROR: {e}"
