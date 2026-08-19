# Hash congelati — C2

Congelati il 2026-08-13, **prima che esista una sola riga di dati di C2**.
L'ultima riga della tabella e' stata aggiunta il 2026-08-15 con lo stesso criterio,
prima che esistesse una riga della **ri-raccolta**: i quattro criteri con cui si
leggera' il confronto fra le due raccolte sono codice, e il codice e' congelato
prima dei dati che dovra' leggere.

Un hash dichiarato e mai riverificato e' documentazione, non protezione: lo verifica
`./verifica_hash.sh`, che distingue una successione documentata da una divergenza muta.
Se modifichi un file congelato, il documento di successione si scrive **prima**.

| file | sha256 | nota |
|---|---|---|
| `PREREGISTRAZIONE.md` | `2e25c38040e16f5e9352faae96e9ebd2aee65272fca927d3bb13bbc71d1fd6bd` |
| `analysis/analyze_c2.py` | `c478df38aa1adb748c11d45b3e22648f92e6a28503f3552d1aca1811c0babed2` |
| `analysis/potenza.py` | `fc5802f73edf1a53a854b8eda8a3f182091c181118c83f20bdc10088d322cb32` |
| `configs/binari_holdout.txt` | `099f811fd0b56158f39adeccf89a7fc2329c4dc12ecf9b91dcfd7dff8cf98735` |
| `src/raccogli_c2.py` | `0da84fd40762517b7d12c240c7d7748f8ac509ddd701d757405884f32f7fc059` |
| `analysis/confronto_riraccolta.py` | `76cd6c126400210b7ab101f98f39b6b958087be8eabf515f5e2991acf36e4719` | scritto il 2026-08-15 alle 22:01, quando la ri-raccolta aveva prodotto **112 righe su 5.880** (1,9%), tutte della cella `gpt-oss-120b/databricks/native`. Committato il 2026-08-16 alle 15:35, al 73,4%. Vedi la nota sotto: la formulazione precedente diceva «prima che producesse una riga» ed era falsa |

L'analisi e' congelata **insieme** alle ipotesi. In C1 le ipotesi erano congelate e
l'analisi scritta a dati visti, che lascia intatta tutta la liberta' che la
pre-registrazione doveva chiudere: quale test, su quale sottoinsieme, con quale
esclusione.

## Successioni

| # | file | documento |
|---|---|---|
| 01 | `src/raccogli_c2.py` | [SUCCESSIONE-01-preflight.md](registro/SUCCESSIONE-01-preflight.md) |
| 02 | `src/raccogli_c2.py` | [SUCCESSIONE-02-ripresa.md](registro/SUCCESSIONE-02-ripresa.md) |
| 03 | `analysis/analyze_c2.py` | [SUCCESSIONE-03-t9-t10.md](registro/SUCCESSIONE-03-t9-t10.md) |
| 04 | `src/raccogli_c2.py` | [SUCCESSIONE-04-partizione.md](registro/SUCCESSIONE-04-partizione.md) |
| 05 | `src/llm/llm_client.py` | [SUCCESSIONE-05-toolconfig-converse.md](registro/SUCCESSIONE-05-toolconfig-converse.md) |
| 06 | `src/raccogli_c2.py` | [SUCCESSIONE-06-sesto-meccanismo.md](registro/SUCCESSIONE-06-sesto-meccanismo.md) |
| 07 | (nessun file congelato: dichiara la minaccia della workdir condivisa) | [SUCCESSIONE-07-rischio-workdir.md](registro/SUCCESSIONE-07-rischio-workdir.md) |
| 08 | `src/raccogli_c2.py` | [SUCCESSIONE-08-ablazione-batching.md](registro/SUCCESSIONE-08-ablazione-batching.md) |
| 09 | `src/raccogli_c2.py`, `src/completa_celle.py` | [SUCCESSIONE-09-braccio-riraccolta.md](registro/SUCCESSIONE-09-braccio-riraccolta.md) |

Le voci 08 e 09 toccano lo stesso file gia' coperto dalle voci piu' vecchie: e' la catena, non una
duplicazione. Questo indice elencava sei voci mentre sul disco ce n'erano nove — la guardia automatica
non ne risentiva (verifica `verifica_hash.sh` legge la directory, non questa tabella), ma un lettore
umano sottocontava di un terzo.

Un documento di successione deve **nominare il file e dichiarare l'hash effettivo**. Nominarlo
soltanto non basta: una successione qualunque nel passato del file coprirebbe in silenzio ogni
modifica seguente, e la guardia risponderebbe a «questo file ha mai avuto una successione?»
invece che a «questa modifica e' documentata?». Lo verifica `verifica_hash.sh` nei due sensi.

Hash precedente di `src/raccogli_c2.py`: `915cbc91a35271b22ce0e8f007d0796c81b9b8f1bce274f22e82a5fb76e78850`.

Hash di `src/raccogli_c2.py` prima della successione 02: `dd763e594c46b9b0214f928438ebb4fbfd028b666be89e6791ad30c643bb96a0`.

Hash di `analysis/analyze_c2.py` prima della successione 03: `fd48f379c93578099731cb7134ce11472872156eb9c6940e69f0572a47dcc3b8`.

Hash di `src/raccogli_c2.py` prima della successione 04: `989cfc24ecf469326c90d55b85beef1baf361b69559a67ee6b87ae2a90cb646f`.

Hash di `src/raccogli_c2.py` prima della successione 06: `8fd465d28f554c28c5802acddf9169130c8018aa5a8413b4d55e802b784930fd`.

## La precedenza del congelamento: cosa e' verificabile e cosa no

Questa tabella diceva che `confronto_riraccolta.py` era stato congelato «prima che la ri-raccolta
producesse una riga». **Era falso**, e il seggio adversariale del gauntlet lo ha trovato dai
timestamp dei dati grezzi. I numeri esatti, ognuno ricalcolabile dai CSV in `results/riraccolta/`:

- `confronto_riraccolta.py` scritto (mtime 2026-08-15 22:01) -> 112 righe su 5.880, **1,9%**
- `EMENDAMENTO-06` scritto (mtime 2026-08-16 08:22) -> 1.611 righe, 27,4%
- entrambi committati (`8e64dd9`, 2026-08-16 15:35:36) -> 4.318 righe, **73,4%**

I tre conteggi si ricalcolano dai timestamp delle righe in `results/riraccolta/` con
`python3 revisione/stato_a_cutoff.py <istante>`, al **secondo esatto** dell'evento. Una versione
precedente di questo elenco riportava 4.315 per il terzo, che e' lo stesso conteggio troncato al minuto:
i due numeri non erano in disaccordo, erano a due precisioni. Vale la pena dirlo perche' e' il tipo di
divergenza che un revisore trova e legge come un'incoerenza.

(Elenco e non tabella di proposito: `verifica_hash.sh` legge ogni riga che inizia con una barra
verticale come una voce «file | hash», quindi una tabella markdown in questo file gli fa
segnalare due divergenze inesistenti. E' successo aggiungendo questa nota, e lo script aveva
ragione a lamentarsi di righe che non sapeva interpretare.)

**Due affermazioni diverse, e vanno separate perche' hanno forza diversa.**

*La sostanza regge.* Le 112 righe appartengono a **una cella su sedici**, un solo modello. I
quattro criteri confrontano otto contrasti appaiati fra le due raccolte: con un modello solo
nessuno degli otto e' calcolabile, quindi la scrittura dei criteri non poteva essere informata
dal loro esito. Questo si verifica dai CSV rilasciati.

*La verificabilita' non regge, e questo e' il punto che conta.* L'unica prova che un terzo puo'
controllare e' la storia committata, e quella dice 73,4%. Un mtime si riscrive con `touch`, e
questo stesso progetto dichiara altrove che «la garanzia vera e' la storia committata» — cioe'
esattamente lo standard che qui non e' soddisfatto. Un hash dichiarato in un file non committato
e' auto-referenziale: nulla impedisce di cambiare insieme il file e la sua impronta.

**Cosa cambia per chi legge il paper**: la ri-raccolta come base primaria e i suoi quattro criteri
sono argomentati, non certificati. La differenza rispetto a `PREREGISTRAZIONE.md` --- committato il
2026-08-13 alle 22:00, ventidue ore prima della prima riga della raccolta originale, e quello si
verifica --- e' che li' la precedenza e' provata e qui e' dichiarata. Il paper lo dice dove
dichiara i criteri, invece di lasciarlo trovare a un revisore.
