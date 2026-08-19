# `results/invalidati/` — spostati, non cancellati

`results/` è append-only. Un lotto invalidato non si elimina: si sposta qui, dove nessuna
analisi lo legge, e la ragione sta in [`../README-validita.md`](../README-validita.md) con il
lotto, la causa e il ricalcolo.

Lo spostamento serve a una cosa sola, ed è meccanica: `analysis/analyze_c2.py` è **congelato** e
fa `glob` **non ricorsivo** su `results/*.csv`. Un file invalidato lasciato lì verrebbe letto
comunque, e l'ordine di `sorted()` lo farebbe pure vincere sui suoi sostituti, perché l'analisi
tiene le **prime** 8 run valide per binario. Un'annotazione in prosa non lo impedisce.

I dati restano nel deposito e nella storia di git. Chiunque può rifare i conti su ciò che è
stato scartato, che è il punto dell'append-only.

| lotto | perché |
|---|---|
| `c2_gpt-oss-120b_bedrock_native{,_redo,_redo2}.csv` + traiettorie | Effetto di selezione da un difetto del client: su Bedrock il turno finale senza tool non è esprimibile, e sopravvivevano solo le run che avevano sottomesso **prima** di quel turno. Causa e correzione in [`SUCCESSIONE-05`](../../registro/SUCCESSIONE-05-toolconfig-converse.md). 453 righe, di cui 29 col `ValidationException` esplicito. |
