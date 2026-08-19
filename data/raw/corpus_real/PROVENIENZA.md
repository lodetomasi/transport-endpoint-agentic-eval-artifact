# Provenienza del corpus `corpus_real/`

Questo corpus esiste per rispondere alla principale minaccia di validità
esterna dello studio: i 60 programmi di `corpus/` sono stati scritti da noi
per l'esperimento (programmi "giocattolo"). I 19 programmi qui sotto sono
invece **codice reale**, estratto da progetti open source con licenza
permissiva (MIT / BSD / Apache-2.0 / ISC / public-domain-CC0), a cui è stato
aggiunto **solo** un `main()` minimale per renderli eseguibili da riga di
comando in modo deterministico (argv/stdin -> stdout, nessun random/tempo/
rete/file). Ogni file indica esplicitamente, con marcatori
`BEGIN/END verbatim third-party code`, quali righe sono codice di terzi e
quali sono il nostro wrapper.

Nessun file qui dentro contiene codice GPL: tutte le licenze sotto sono
ridistribuibili insieme all'artefatto.

## Tabella di provenienza

| File | Progetto di origine | URL | Licenza | Commit/versione | Modifiche |
|---|---|---|---|---|---|
| `r01_sha256.c` | B-Con/crypto-algorithms | https://github.com/B-Con/crypto-algorithms (sha256.c, sha256.h) | Public domain (dichiarazione esplicita nel README del progetto, nessuna licenza SPDX rilevata da GitHub) | HEAD di `master` al momento del fetch (2026-08) | Aggiunto `main()` che hasha `argv[1]` e stampa hex. `<memory.h>` non necessario qui (sha256.c usa già `<string.h>` a monte). |
| `r02_sha1.c` | B-Con/crypto-algorithms | https://github.com/B-Con/crypto-algorithms (sha1.c, sha1.h) | Public domain (idem) | idem | Aggiunto `main()`. Sostituito `#include <memory.h>` con `#include <string.h>` (equivalente portabile per `memset()`; `<memory.h>` non è uno header standard). |
| `r03_md5.c` | B-Con/crypto-algorithms | https://github.com/B-Con/crypto-algorithms (md5.c, md5.h) | Public domain (idem) | idem | Aggiunto `main()`. Stessa sostituzione `<memory.h>` -> `<string.h>`. |
| `r04_rot13.c` | B-Con/crypto-algorithms | https://github.com/B-Con/crypto-algorithms (rot-13.c, rot-13.h) | Public domain (idem) | idem | Aggiunto `main()` con buffer mutabile e limite `MAX_LEN=255` (rifiuto esplicito, non troncamento silenzioso). |
| `r05_arcfour.c` | B-Con/crypto-algorithms | https://github.com/B-Con/crypto-algorithms (arcfour.c, arcfour.h) | Public domain (idem) | idem | Aggiunto `main()` che deriva key/keystream da argv e stampa il ciphertext in hex. Nessuna riga dell'algoritmo modificata. Verificato contro il vettore di test RC4 standard key="Key" pt="Plaintext" -> `bbf316e8d940af0ad3`. |
| `r06_base64.c` | littlstar/b64.c | https://github.com/littlstar/b64.c (b64.h, buffer.c, encode.c, decode.c) | MIT (Copyright (c) 2014 Little Star Media, Inc.) | HEAD di `master` | Concatenazione meccanica di 4 file upstream in uno; nessuna riga di logica cambiata. Verificato contro `base64`/`base64 -d` di sistema. |
| `r07_crc8.c` | lammertb/libcrc | https://github.com/lammertb/libcrc (src/crc8.c) | MIT (Copyright (c) 1999-2016 Lammert Bies) | HEAD di `master` | Nessuna modifica alla tabella o all'algoritmo; solo `main()` aggiunto. |
| `r08_crc16.c` | lammertb/libcrc | https://github.com/lammertb/libcrc (src/crc16.c, include/checksum.h per le costanti) | MIT (idem) | idem | Solo `main()` aggiunto. Verificato contro il vettore di test standard CRC-16/ARC("123456789") = 0xBB3D = 47933. |
| `r09_crc32.c` | lammertb/libcrc | https://github.com/lammertb/libcrc (src/crc32.c, include/checksum.h per `CRC_START_32`) | MIT (idem) | idem | **Adattamento documentato**: la tabella di lookup upstream viene inclusa da `tab/gentab32.inc`, generato a build-time dal tool `crcgen` del progetto e NON presente nel repository git (verificato: `tab/` contiene solo un `README`). Abbiamo ricalcolato la tabella a 256 entry con lo stesso algoritmo di generazione bit-reversed che libcrc stesso usa in chiaro per CRC-16/CRC-64 (`init_crc16_tab()` in crc16.c), per il polinomio `CRC_POLY_32 = 0xEDB88320`. La tabella è verificata byte-per-byte identica alla tabella CRC-32/zlib standard e il programma risultante produce `crc32("123456789") == 3421780262 (0xCBF43926)`, verificato contro `python3 -c "import zlib; print(zlib.crc32(b'123456789'))"`. |
| `r10_ini_parser.c` | benhoyt/inih | https://github.com/benhoyt/inih (ini.h, ini.c) | New BSD / BSD-3-Clause (Copyright (C) 2009-2025 Ben Hoyt) | HEAD di `master` | Concatenazione meccanica di ini.h + ini.c in un solo file; tutte le macro `INI_*` lasciate ai valori di default upstream. Solo `main()`/handler aggiunti. |
| `r11_jsmn_tokenizer.c` | zserge/jsmn | https://github.com/zserge/jsmn (jsmn.h) | MIT (Copyright (c) 2010 Serge Zaitsev) | HEAD di `master` | jsmn.h è pensato upstream per essere incluso direttamente in una unica translation unit (guardia `#ifndef JSMN_HEADER`); incollato qui invece di essere un header separato. Nessuna riga di logica cambiata. Solo `main()` aggiunto. |
| `r12_picohttpparser.c` | h2o/picohttpparser | https://github.com/h2o/picohttpparser (picohttpparser.c, picohttpparser.h) | MIT (una delle due licenze del dual-license MIT/Perl; usiamo i termini MIT) | HEAD di `master` | Concatenazione header+.c; rimossa solo la riga `#include "picohttpparser.h"` (il contenuto della dichiarazione è incollato inline). **Eccezione di dimensione dichiarata**: ~700 righe, sopra il target 50-300 usato altrove nel corpus, perché le funzioni sono mutuamente dipendenti e un estratto avrebbe richiesto riscrittura (quindi non sarebbe più "reale"). |
| `r13_tiny_regex.c` | kokke/tiny-regex-c | https://github.com/kokke/tiny-regex-c (re.c, re.h) | Unlicense / public domain | HEAD di `master` | Concatenazione header+.c; rimossa `#include "re.h"` sostituita dal contenuto inline; rimossa `re_print()` (funzione di debug upstream, mai chiamata, per tenere il file più snello -- unica omissione di codice upstream in tutto il corpus, dichiarata qui). **Eccezione di dimensione dichiarata**: ~500 righe, per lo stesso motivo di r12. |
| `r14_ksort_introsort.c` | attractivechaos/klib | https://github.com/attractivechaos/klib (ksort.h) | MIT (Copyright (c) 2008, 2011 Attractive Chaos) | HEAD di `master` | Copiata solo la macro `KSORT_INIT`/`KSORT_INIT_GENERIC` (non `KRADIX_SORT_INIT`, funzionalità separata non usata). **Adattamenti documentati**: (1) `drand48()` non è visibile sotto `-std=c11` stretto: dichiarata noi stessi con la sua vera firma POSIX (`extern double drand48(void);`) invece di modificare la macro; (2) `ks_sample_##name` (upstream la marca essa stessa "FIXME: NOT TESTED!!!", mai chiamata da noi) genera un warning `-Wsign-compare`; silenziato con `#pragma GCC diagnostic ignored` intorno alla singola istanziazione della macro, senza toccare il corpo verbatim. |
| `r15_pcg32.c` | imneme/pcg-c-basic | https://github.com/imneme/pcg-c-basic (pcg_basic.c, pcg_basic.h) | Apache License 2.0 (Copyright 2014 Melissa O'Neill) | HEAD di `master` | Solo `main()` aggiunto. Verificato bit-per-bit contro una reimplementazione Python indipendente dello stesso algoritmo PCG32 (LCG a 64 bit + xorshift + rotazione). |
| `r16_siphash.c` | veorq/SipHash | https://github.com/veorq/SipHash (siphash.c, siphash.h) | CC0 1.0 Universal / public domain (dichiarazione esplicita nell'intestazione del file, autori Jean-Philippe Aumasson e Daniel J. Bernstein) | HEAD di `master` | Rimossi solo i blocchi `#ifdef DEBUG_SIPHASH` / macro `TRACE` (mai attivati upstream di default, puro debug). Solo `main()` aggiunto (parsing chiave hex + messaggio). Verificato **esattamente** contro il vettore di test ufficiale `vectors_sip64[0]` del progetto (messaggio vuoto, chiave `000102030405060708090a0b0c0d0e0f` -> digest `31 0e 0e dd 47 db 6f 72`). |
| `r17_musl_smoothsort.c` | kraj/musl (mirror di musl libc) | https://github.com/kraj/musl (src/stdlib/qsort.c) | MIT (Copyright (C) 2011 by Lynn Ochs; integrazione in musl di Rich Felker) | HEAD di `master` | **Adattamenti documentati**: (1) `ntz(x)` era `a_ctz_l(x)`, primitiva atomica interna di musl (`atomic.h`, non pubblica); sostituita con `__builtin_ctzl` (stessa semantica: indice del primo bit impostato di un `unsigned long` non-zero); (2) rimossa `weak_alias(__qsort_r, qsort_r)` (macro di linking interna a musl) e la funzione rinominata `smoothsort_qsort_r` invece di `qsort_r`, perché la libc della macchina di build (macOS) dichiara già un `qsort_r` con una **firma incompatibile** (ordine argomenti stile BSD, non stile GNU/musl) in `<stdlib.h>`, causando un vero errore di compilazione ("conflicting types") se si riusa quel nome; (3) `#define _BSD_SOURCE` upstream rimosso (serviva solo per l'header interno non più incluso); (4) alcuni confronti verbatim (`int` vs `size_t`) generano `-Wsign-compare`, e `cycle()` genera un falso positivo `-Wdangling-pointer` (GCC 12+) per un pattern di uso di buffer locale sicuro ma non visibile allo static analyzer; entrambi silenziati con pragma, nessuna riga logica cambiata. |
| `r18_musl_memmem.c` | kraj/musl (mirror di musl libc) | https://github.com/kraj/musl (src/string/memmem.c) | MIT | HEAD di `master` | Nessun adattamento strutturale. Un solo confronto verbatim (`z-h < l`, `ptrdiff_t` vs `size_t`) genera `-Wsign-compare`, silenziato con pragma. |
| `r19_openbsd_strtonum.c` | openbsd/src | https://github.com/openbsd/src (lib/libc/stdlib/strtonum.c, `$OpenBSD: strtonum.c,v 1.8 2015/09/13 08:31:48 guenther Exp $`) | Licenza permissiva stile ISC (Copyright (c) 2004 Ted Unangst e Todd Miller: "Permission to use, copy, modify, and distribute...") | Revisione 1.8 (2015-09-13) | Rimossa `DEF_WEAK(strtonum);` (macro di linking interna a OpenBSD libc, non definita fuori dal loro build). Nessuna altra riga cambiata. |

## Come è stato generato il ground truth (`*.tests.json`)

Per ognuno dei 19 programmi sono stati scelti 5 casi di test (via
`/private/tmp/.../scratchpad/gen_tests_real.py`, script one-off non incluso
nell'artefatto consegnato), poi:

1. il programma è stato compilato con `gcc-15 -Wall -Wextra -std=c11 -Werror`;
2. il binario compilato è stato **eseguito realmente** su ciascun input;
3. `expected_stdout` nel `.tests.json` è lo stdout **effettivamente prodotto**
   da quell'esecuzione (non calcolato a mano).

Questo garantisce che il ground truth sia corretto per costruzione rispetto
al codice sorgente reale. Dove possibile abbiamo *anche* incrociato l'output
con un tool di riferimento indipendente (vedi tabella sopra e output di
verifica più sotto): `shasum -a 256`, `shasum -a 1`, `md5` di sistema,
`base64`/`base64 -d` di sistema, `python3 -c "import zlib; zlib.crc32(...)"`,
il vettore di test standard CRC-16/ARC, il vettore di test ufficiale
SipHash-2-4, il vettore di test standard RC4, e una reimplementazione Python
indipendente di PCG32.

## Finding empirico dal sanitizer (da riportare, non da nascondere)

`clang -fsanitize=address,undefined` su `r01_sha256.c`, `r02_sha1.c` e
`r03_md5.c` (crypto-algorithms di Brad Conte) segnala un **vero
undefined-behavior per lo standard C**, non un artefatto del nostro wrapper:

```
sha256.c / sha1.c / md5.c: runtime error: left shift of 128 by 24 places
cannot be represented in type 'int'
```

Causa: nell'espansione del message schedule (`data[j] << 24`), `data[j]` è
un `unsigned char` (`BYTE`) promosso a `int`; quando il byte vale `0x80`
(cioè 128) e cade in una posizione multiplo di 4 all'interno del blocco (cioè
`datalen % 4 == 0` al momento del padding), lo shift a sinistra di 24 posizioni
eccede il bit di segno di un `int` a 32 bit con segno: è undefined behavior
per lo standard C, anche se **ogni compilatore mainstream (gcc, clang, MSVC)
lo implementa con wraparound a due complementi ben definito**, che è
esattamente il motivo per cui questa implementazione "di base" molto diffusa
produce hash bit-esatti da oltre un decennio nonostante il warning.

Il byte di padding `0x80` viene inserito da **ogni** chiamata a
`sha256_final()`/`sha1_final()`/`md5_final()` (fa parte dello schema di
padding Merkle-Damgård), quindi questo non è un caso limite raro: si
manifesta per circa 1 lunghezza di messaggio su 4 (tutte le lunghezze con
`length % 4 == 0` all'ultimo blocco, incluso il messaggio vuoto). Lo abbiamo
**lasciato invariato** (non patchato) perché patchare significherebbe che
questo file non sarebbe più il codice terzo reale che dichiariamo di
distribuire; lo documentiamo qui invece. Correttezza del risultato non
compromessa: verificato contro `shasum -a 256`, `shasum -a 1`, `md5` di
sistema per tutti i 5 casi di test di ciascuno dei tre programmi (vedi output
di verifica riportato nella risposta finale).

Nessun altro finding ASan/UBSan sui restanti 16 programmi.

## Valutazione del rischio di contaminazione (memorizzazione da parte del modello)

| File | Rischio stimato | Motivazione |
|---|---|---|
| `r01_sha256.c`, `r02_sha1.c`, `r03_md5.c` | **Alto** | SHA-256/SHA-1/MD5 sono tra gli algoritmi più celebri e più ripetuti nei dataset di training (innumerevoli implementazioni "textbook" quasi identiche in circolazione, inclusa questa stessa da Brad Conte che è ampiamente ricopiata/forkata online). Un LLM potrebbe riconoscere l'algoritmo/la struttura anche solo dal binario decompilato senza vero reverse engineering. |
| `r06_base64.c` | **Medio-alto** | Base64 è un algoritmo estremamente comune con innumerevoli implementazioni quasi-identiche; la tabella `b64_table[]` e la struttura a 3-byte-in/4-byte-out sono facilmente riconoscibili. |
| `r13_tiny_regex.c` | **Medio** | tiny-regex-c è un progetto GitHub relativamente popolare (>2k stelle) e frequentemente citato in tutorial "come scrivere un motore regex minimale"; la struttura è meno "canonica" di un algoritmo da manuale ma è comunque un progetto noto. |
| `r14_ksort_introsort.c` | **Medio** | klib è ampiamente usato in bioinformatica (samtools, bwa) ed è quindi probabile che frammenti di `ksort.h` compaiano nel training set; introsort/combsort in sé sono algoritmi da manuale, ma questa specifica implementazione macro-based è piuttosto distintiva e quindi potenzialmente riconoscibile come "klib" specificamente. |
| `r09_crc32.c` | **Medio** | La tabella CRC-32 standard (polinomio 0xEDB88320) è probabilmente la tabella di lookup più ricopiata in assoluto nella storia della programmazione (zlib, PNG, Ethernet, migliaia di implementazioni); un modello potrebbe riconoscere "questa è la tabella CRC-32 standard" senza fare reverse engineering byte-per-byte. |
| `r15_pcg32.c` | **Medio** | PCG è relativamente noto (usato in NumPy, Rust `rand`, ecc.) e la costante moltiplicativa `6364136223846793005` è una "impronta digitale" molto riconoscibile e ricercabile testualmente. |
| `r16_siphash.c` | **Medio** | SipHash è usato in moltissimi linguaggi/runtime (hash table di Python, Rust, Ruby, ecc.) per la resistenza a hash-flooding; le costanti magiche `0x736f6d6570736575` ecc. sono citazioni testuali ("somepseudorandomlygeneratedbytes" in ASCII) molto distintive e ricercabili. |
| `r08_crc16.c`, `r07_crc8.c` | **Medio-basso** | CRC-16 "IBM"/ARC è discretamente noto; la tabella CRC-8 specifica per sensori SHT75 di libcrc è più oscura e meno probabile che sia stata vista isolatamente più volte nel training set. |
| `r04_rot13.c` | **Basso** | ROT-13 è concettualmente famosissimo ma l'implementazione stessa è talmente semplice (un ciclo con aritmetica modulare) che "riconoscerla" equivale comunque a capirla correttamente: rischio di scorciatoia minimo. |
| `r05_arcfour.c` | **Basso-medio** | RC4/ARCFOUR è un algoritmo noto ma l'implementazione specifica di Brad Conte (con `state[]`/`arcfour_generate_stream` separata dal keying) è meno "canonica" delle centinaia di RC4 quasi-identici in giro; rischio moderato ma inferiore a SHA/MD5. |
| `r10_ini_parser.c` | **Basso** | inih è un progetto reale ma di nicchia (parser INI, non un algoritmo da manuale); la logica di parsing con stato (`prev_name`, gestione multilinea, BOM UTF-8) è sufficientemente specifica da richiedere comprensione reale, non solo riconoscimento di pattern. |
| `r11_jsmn_tokenizer.c` | **Basso-medio** | jsmn è un progetto GitHub noto (>6k stelle) per la tokenizzazione JSON "senza allocazioni"; è più probabile che sia stato visto in training rispetto a inih, ma la logica specifica (gestione di `toksuper`, unione di array/oggetti) è comunque più articolata di un algoritmo da manuale. |
| `r12_picohttpparser.c` | **Basso** | Usato "sotto il cofano" da H2O e da vari moduli Perl, ma raramente discusso/ricopiato come tutorial standalone; è codice di libreria "di infrastruttura", oscuro rispetto a un algoritmo da manuale. |
| `r17_musl_smoothsort.c` | **Basso** | Smoothsort è un algoritmo di Dijkstra relativamente oscuro (molto meno diffuso di quicksort/mergesort nei tutorial), e questa specifica implementazione musl (variante "a due array circolari mascherati", numeri di Leonardo) è distintiva e complessa: buona probabilità che il modello debba davvero comprendere la struttura piuttosto che riconoscerla a memoria. |
| `r18_musl_memmem.c` | **Basso** | L'algoritmo "two-way string matching" (Crochemore-Perrin) è relativamente oscuro rispetto a KMP/Boyer-Moore nei tutorial standard; buon candidato "poco famoso" secondo il criterio richiesto. |
| `r19_openbsd_strtonum.c` | **Basso** | Funzione di validazione input piuttosto oscura fuori dall'ecosistema BSD; nessun algoritmo "celebre" sottostante, solo logica di controllo errori. |

**Raccomandazione**: se nel paper si vuole un sotto-campione "a basso rischio
di contaminazione" per un'analisi di sensitività, i candidati migliori sono
`r10_ini_parser`, `r12_picohttpparser`, `r17_musl_smoothsort`,
`r18_musl_memmem`, `r19_openbsd_strtonum` (tutti valutati "Basso" sopra).

## Programmi con eccezione dichiarata alla dimensione target (50-300 righe)

Conteggio righe effettivo (`wc -l`) di tutti i 19 file, dal più corto al più
lungo:

```
 74 r04_rot13.c            116 r19_openbsd_strtonum.c   229 r16_siphash.c            369 r11_jsmn_tokenizer.c
 91 r07_crc8.c             118 r05_arcfour.c            247 r03_md5.c                425 r10_ini_parser.c
 98 r15_pcg32.c            136 r09_crc32.c              281 r06_base64.c             487 r13_tiny_regex.c
116 r08_crc16.c            207 r01_sha256.c             316 r14_ksort_introsort.c    798 r12_picohttpparser.c
                           208 r02_sha1.c               336 r17_musl_smoothsort.c
```

10 dei 19 file rientrano nel target 50-300 righe. I restanti 6 lo superano;
elenchiamo qui ciascuno con il motivo, per non farlo passare come una
decisione silenziosa:

- `r01_sha256.c` (207), `r02_sha1.c` (208), `r03_md5.c` (247): includono
  ciascuno l'intera tabella di costanti (`k[64]` per SHA-256) o l'intera
  espansione a 4 fasi (MD5); l'algoritmo stesso è compatto ma le costanti
  numeriche occupano molte righe.
- `r06_base64.c` (281): concatenazione di 4 file upstream distinti
  (b64.h + buffer.c + encode.c + decode.c); nessuno dei 4 è grande
  singolarmente.
- `r10_ini_parser.c` (425): concatenazione di ini.h (che upstream conta da
  solo ~190 righe, quasi tutte macro `#define`/commenti di configurazione)
  + ini.c; la logica di parsing vera e propria è una singola funzione
  (`ini_parse_stream`) di ~160 righe.
- `r11_jsmn_tokenizer.c` (369): jsmn.h è un header-only upstream di 471
  righe (incluso il commento di licenza e le dichiarazioni); il nostro file
  è più corto dell'originale perché abbiamo rimosso i rami `#ifdef
  JSMN_STRICT` / `JSMN_PARENT_LINKS` mai attivati di default (documentato
  inline nei commenti del file, non qui separatamente perché è una
  semplificazione di configurazione, non di logica).
- `r14_ksort_introsort.c` (316): la macro `KSORT_INIT` upstream genera 10
  funzioni diverse (mergesort, heapsort, combsort, introsort, ksmall,
  shuffle, sample) in un unico blocco macro indivisibile; non potevamo
  tenerne solo una senza modificare la macro stessa.
- `r17_musl_smoothsort.c` (336): l'algoritmo smoothsort upstream è
  genuinamente più lungo di quicksort/mergesort per via della gestione dei
  numeri di Leonardo e dello stack di ripristino; nessuna funzione è stata
  aggiunta oltre a quelle strettamente necessarie.
- `r12_picohttpparser.c` (798) e `r13_tiny_regex.c` (487): già discussi
  sopra, funzioni mutuamente dipendenti non divisibili senza riscrittura.

Tutte queste eccezioni sono dichiarate qui, non silenziose, come richiesto
dalle regole del progetto ("Where the spec is ambiguous, stop and report the
ambiguity -- do not resolve it silently"). Chi userà questo corpus per un
esperimento sensibile al costo-di-contesto della decompilazione dovrebbe
considerare di trattare questi 6 file come una sotto-categoria "file reali
grandi" separata dagli altri 13, oppure escluderli da un confronto a parità
di dimensione con `corpus/`.

## Ambiguità riscontrate durante la costruzione (da riportare, non risolte da sole)

1. **Definizione di "reale" per codice con wrapper aggiunto**: la spec
   permette di aggiungere un `main()` se il codice originale è una libreria.
   Per 3 file (`r09_crc32.c`, `r14_ksort_introsort.c`, `r17_musl_smoothsort.c`)
   abbiamo dovuto fare adattamenti più profondi di un semplice `main()`
   (rigenerare una tabella non presente nel repo; rinominare una funzione per
   evitare collisione con `<stdlib.h>` della piattaforma di build; sostituire
   una primitiva interna non pubblica con un builtin del compilatore).
   Riteniamo che questi siano adattamenti di "impalcatura di compilazione"
   equivalenti in spirito al permesso "main() wrapper", e non modifiche
   all'algoritmo, ma segnaliamo esplicitamente la distinzione perché è una
   zona grigia della spec: un revisore più conservativo potrebbe voler
   escludere questi 3 file da un claim di "codice reale non modificato al
   100%". Li abbiamo mantenuti nel corpus con adattamento documentato riga
   per riga, non silenzioso, ma segnaliamo la decisione qui esplicitamente
   invece di darla per assunta.
2. **Corpus reale come sottoinsieme scelto da noi, non campione casuale**:
   i 19 programmi sono stati selezionati a mano da un piccolo insieme di
   progetti che soddisfacevano contemporaneamente licenza permissiva +
   nessuna dipendenza esterna + determinismo + dimensione gestibile. Questo
   introduce un bias di selezione (abbiamo scartato progetti con dipendenze
   difficili da rimuovere, come `fnmatch.c` di musl che dipende dagli
   header locale interni di musl). Non è un campione statisticamente
   rappresentativo di "tutto il codice C reale", ma di "codice C reale
   piccolo, standalone, permissivo, testabile via CLI" -- una popolazione
   più ristretta che dovrebbe essere nominata esplicitamente nel paper come
   tale, non genericamente come "codice reale".
