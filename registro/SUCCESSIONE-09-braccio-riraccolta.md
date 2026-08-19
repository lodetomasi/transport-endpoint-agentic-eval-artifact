# Successione 09 — un terzo braccio: la ri-raccolta isolata

**Data**: 2026-08-15, scritta **prima** della modifica e **prima** di spendere.
**Innesco**: `EMENDAMENTO-06` decide la ri-raccolta; `<revisione-avversariale-dell-apparato>`, convocato dal gate
dei $5, ha verificato che **il codice per eseguirla non esiste** e ha trovato quattro modi in
cui scriverlo di getto avrebbe distrutto dati o comprato righe che nessuno legge.

## I file

`src/raccogli_c2.py` (congelato), `src/completa_celle.py`.

**Hash di `src/raccogli_c2.py` dopo questa successione**: `a91a2a9edf1dbbcf93645e5c0d1c1b8915c3e626f274e27746802e90e810e33c`
**Hash precedente**: `eb58dd2f86c26112746299d36407a9bbc56ee249379d3a94956ace0081aaf80b` (dichiarato dalla successione 08).

`run_minipilot.py` **non** cambia: la correzione del tag di cella e' gia' entrata con la
successione 08, e il difetto dello stem si chiude a monte, nel nome del file che il
driver gli passa.

## Cosa il critico ha trovato, e perché ciascuna cosa cambia il disegno del codice

**1. `deficit()` avrebbe detto «CHIUSA già» per tutte e sedici.** Verificato eseguendo
`completa_celle.py`: 16 celle su 16 risultano chiuse, perché lo sono. Il driver avrebbe
stampato sedici righe di successo, speso zero e chiuso con exit 0 — la firma che questo
progetto ha già imparato a riconoscere, e che la successione 08 documenta per l'ablazione.

**2. Nessun codice scrive `results/riraccolta/`**, che `analysis/confronto_riraccolta.py` —
congelato poche ore fa — si aspetta. La pipeline era dichiarata e non cablata.

**3. Se i nuovi file finissero nella radice di `results/`**, `analyze_c2.carica()` accumula i
valori per binario nell'ordine alfabetico dei file e `media_per_binario` prende `v[:8]`: i
primi otto. Ogni cella è già a otto validi, quindi ogni riga nuova verrebbe **troncata via in
silenzio**. Non mescolata: scartata. Si comprerebbero 5.805 misurazioni che l'analisi congelata
non guarda, senza un errore, senza un avviso. Inoltre `sonnet/databricks/native` ha già tutti e
quattro i suffissi occupati, e `prossimo_suffisso()` uscirebbe con «esauriti i suffissi» a
metà raccolta, dopo aver speso sulle altre quindici celle.

**4. Se i nuovi file avessero lo stesso NOME in una cartella diversa**, il difetto peggiore:
`run_minipilot.py` deriva il tag di traiettoria e di workdir da `Path(args.out).stem` — il
**nome**, non il percorso. Stesso nome ⇒ stesso tag ⇒ `write_trajectory` apre in `"w"` sopra
`results/trajectories/c2_<cella>/progNN_rK.jsonl`, che esiste già con 360 file per cella.
Avremmo **sovrascritto le traiettorie originali**, cioè distrutto i dati che la ri-raccolta
serve a confrontare, violando IR-5 in silenzio e senza possibilità di recupero.

Il quarto è la ragione per cui questa successione non si limita a cambiare una cartella.

## Cosa cambia

**Un parametro `braccio`, non un secondo booleano.** `percorso_cella`, `valide_per_binario`,
`prossimo_suffisso` e `deficit` prendevano `ablazione=False`. Con due bracci servirebbero due
booleani mutuamente esclusivi, e la prima volta che qualcuno ne passa due veri il codice sceglie
in silenzio. Diventa `braccio` con quattro valori dichiarati — `confermativo`, `ablazione`,
`riraccolta`, `esplorativo` — e un valore sconosciuto solleva invece di ricadere sul default.

I percorsi, uno per braccio, con **nomi di file distinti** e non solo cartelle distinte:

| braccio | file |
|---|---|
| confermativo | `results/c2_<eti>_<infra>_<trasp><suf>.csv` |
| ablazione | `results/ablazione/c2a_<eti>_<infra>_<trasp>1<suf>.csv` |
| **ri-raccolta** | **`results/riraccolta/c2r_<eti>_<infra>_<trasp><suf>.csv`** |
| esplorativo | `results/esplorativo/c2x_<eti>_<infra>_<trasp><suf>.csv` |

Il prefisso `c2r_` non è cosmetico: è ciò che rende distinto lo `stem`, e quindi il tag della
workdir e della directory di traiettorie. È la correzione del difetto 4, e sta nel nome del
file perché è da lì che il tag viene derivato.

**`raccogli_c2.py` guadagna `--riraccolta`**, che seleziona il braccio. Il controllo «CHIUSA
già» **non si tocca**: continua a chiedere il deficit, ma lo chiede al braccio giusto, dove la
cartella è vuota e quindi mancano tutte le run. Nessun flag di forzatura, nessun bypass: la
domanda resta la stessa e cambia solo a chi viene posta. Un `--forza` che ignora un controllo di
completezza sarebbe esattamente il genere di scorciatoia che le regole del progetto vietano.

**`analyze_c2.py` non si tocca.** Fa glob non ricorsivo su `results/*.csv` e la ri-raccolta sta
in una sottocartella: è invisibile al confermativo **per costruzione**, come già l'ablazione e
l'esplorativo. Per analizzare la nuova raccolta si esegue lo stesso script congelato con
`--results results/riraccolta`, che è il modo in cui era già stato scritto per essere usato.

## Cosa NON cambia

Roster, 45 binari, 8 run, 12 turni, temperatura 0, i due trasporti, i due cloud, la famiglia dei
dieci test, `m = 10`, le soglie, i falsificatori. La ri-raccolta è la stessa misura con
l'apparato corretto, e questa successione riguarda solo dove i file vanno a finire.

## Come si verifica, e nei due sensi

Il test si scrive **prima**, e deve contenere il caso che oggi fallisce e quello che deve
continuare a passare:

1. `deficit(braccio="riraccolta")` deve dire che **mancano tutte** le 45×8 run di ogni cella,
   perché la cartella è vuota. È il caso che oggi risponderebbe «CHIUSA già».
2. `deficit(braccio="confermativo")` deve **continuare** a dire che non manca nulla. Senza
   questo, una funzione che dichiara tutto incompleto passerebbe il primo controllo.
3. `percorso_cella` deve dare quattro percorsi **distinti a due a due** per gli stessi
   argomenti, e i loro `stem` devono essere distinti — perché è lo stem, non il percorso, a
   diventare il tag della workdir.
4. Un braccio sconosciuto deve sollevare, non ricadere sul confermativo.

## Il costo del non farlo

Senza il punto 4 dei controlli, il difetto peggiore trovato dal critico costerebbe le 5.760
traiettorie della raccolta originale — sovrascritte da quella nuova, senza errore. È lo stesso
danno che `SUCCESSIONE-07` descrive per la workdir condivisa, con la differenza che qui sarebbe
stato completo invece che probabilistico.
