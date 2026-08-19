# Emendamento 02 — un terzo cloud, dichiarato **esplorativo**

**Data**: 2026-08-14. **Stato**: raccolta confermativa in corso, 2 celle su 16 chiuse.

## Cosa si aggiunge

Quattro celle su **Azure AI Foundry**: `gpt-oss-120b` e `llama-3.3-70b`, entrambi i trasporti,
gli stessi 45 binari, le stesse 8 run.

Sono i **soli due modelli serviti da tutti e tre i cloud**, e sono entrambi a pesi aperti.

| | |
|---|---|
| celle | 2 modelli × 1 infrastruttura × 2 trasporti = **4** |
| run | 1.440 |
| costo previsto | **~$6** |

## Perché è esplorativo, e non entra nella famiglia

`PREREGISTRAZIONE.md` §7 congela **dieci** test con `m` fisso, su due infrastrutture. Aggiungere
Azure alla famiglia confermativa significherebbe cambiare `m` **a dati parzialmente visti**, e
cambiare `m` sposta ogni soglia di Holm dei test già dentro. È esattamente la libertà che la
pre-registrazione esiste per chiudere.

Quindi:

- il braccio Azure **non entra** nella famiglia dei dieci test;
- `m` resta **10**;
- nessuna soglia si muove;
- i suoi risultati si riportano come **esplorativi**, con quella parola, in una sezione propria.

## Cosa può dire, essendo esplorativo

Un esplorativo non conferma. Ma può fare due cose che valgono:

1. **Togliere l'attacco più ovvio.** «Due infrastrutture non sono una popolazione» è il primo
   rilievo che un revisore scrive. Con una terza, l'affermazione passa da «differiscono» a
   «differiscono, e non a coppie» — o, se i tre concordano, il risultato nullo diventa molto
   più informativo di quanto lo sarebbe con due.
2. **Generare l'ipotesi del capitolo successivo.** È il ruolo proprio di un braccio
   esplorativo, ed è dichiarato prima invece che scoperto dopo.

## Perché costa così poco, e perché questo è il punto

L'apparato è già in piedi: il ramo `azure` di `llm_client.py` è scritto e **verificato
end-to-end** dal 2026-08-13, i quattro deployment sono attivi, le tariffe sono in
`configs/pricing.json` con la fonte, e il censimento ha già sondato entrambi i trasporti su
entrambi i modelli.

Sei dollari per rimuovere il rilievo più prevedibile è il miglior rapporto disponibile in
questo studio.

## Un limite che va dichiarato adesso

Su Azure il roster è **più piccolo per una ragione che è essa stessa un risultato**: i modelli
Anthropic non ci sono affatto, `gpt-oss-20b` è rifiutato per quota inesistente, e
`llama-3.1-8b` è deprecato dal 13/06/2026 mentre gli altri due cloud lo servono ancora.

Quindi il braccio Azure **non è** una replica del confermativo su una terza infrastruttura: è
la sua intersezione a pesi aperti. Va scritto così, e non come «abbiamo aggiunto un cloud».

## Effetto sul tetto

`$6` su un tetto di `$200`, con proiezione confermativa a `$124,88`. Il totale previsto passa a
**~$131**.
