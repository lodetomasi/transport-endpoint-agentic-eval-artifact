# Snapshot dei dati del capitolo precedente

Questo non è il capitolo precedente: sono **le sole celle** che servono a riprodurre i due
numeri che questo paper ne cita, copiate qui perché il deposito sia autosufficiente.

| cosa | perché sta qui |
|---|---|
| `s03_haiku45_N12*.csv` e `s03t_haiku45_N12*.csv` | la coppia nativo/testuale su cui `analysis/potenza.py` calibrò la potenza, e da cui `analysis/stimatori_c1_c2` ricalcola l'84% contro il 130,7% |
| `trajectories/s03_haiku45_N12*` e `trajectories/s03t_haiku45_N12*` | i log per-turno da cui si conta l'esposizione a `list_strings`, 100% contro 86,7% |

Con questo snapshot, `analysis/esposizione_list_strings_c1.py` gira dal deposito:

```bash
C2_S1_RESULTS=data/c1-snapshot python3 analysis/esposizione_list_strings_c1.py
```

**Cosa NON c'è**: le altre celle del capitolo precedente, i suoi binari, il suo harness. Chi
volesse rifare quel capitolo ha bisogno del suo artefatto, non di questo. Qui c'è quanto basta
perché ogni numero che *questo* paper cita sia ricalcolabile senza uscire dal deposito.
