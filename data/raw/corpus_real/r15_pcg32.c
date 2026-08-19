/*
 * r15_pcg32.c
 *
 * REAL CODE, not written for this experiment. The pcg32_srandom_r()
 * and pcg32_random_r() functions below are copied verbatim from
 * Melissa O'Neill's "pcg-c-basic" repository
 * (https://github.com/imneme/pcg-c-basic, files
 * pcg_basic.c/pcg_basic.h, Apache License 2.0). This is the reduced
 * "basic" reference implementation of the PCG family of pseudorandom
 * generators. See ../corpus_real/PROVENIENZA.md for exact provenance.
 *
 * Determinism note: this program is a PRNG, but it is not a source
 * of nondeterminism in the sense the corpus rules care about (no
 * time(), no /dev/urandom, no OS entropy). The seed and stream
 * selector are supplied entirely via argv, exactly like upstream's
 * own pcg32_srandom_r() API requires; the same argv always produces
 * the same output.
 *
 * The only addition (clearly marked below) is a minimal main() that
 * seeds a pcg32_random_t with argv[1] (initstate) and argv[2]
 * (initseq), then prints argv[3] consecutive 32-bit outputs as
 * unsigned decimal integers, one per line, so the library can be
 * exercised as a standalone CLI program.
 *
 * Usage: r15_pcg32 <initstate> <initseq> <count>
 * Prints <count> pseudorandom uint32 values (one per line), or
 * "USAGE" if fewer than three arguments were given.
 */
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

/* ------------------------------------------------------------------ */
/* BEGIN verbatim third-party code: pcg_basic.h (pcg-c-basic,         */
/* Apache-2.0)                                                         */
/* ------------------------------------------------------------------ */

struct pcg_state_setseq_64 {    /* Internals are *Private*. */
    uint64_t state;             /* RNG state.  All values are possible. */
    uint64_t inc;               /* Controls which RNG sequence (stream) is
                                    selected. Must *always* be odd. */
};
typedef struct pcg_state_setseq_64 pcg32_random_t;

#define PCG32_INITIALIZER   { 0x853c49e6748fea9bULL, 0xda3e39cb94b95bdbULL }

void pcg32_srandom_r(pcg32_random_t* rng, uint64_t initstate, uint64_t initseq);
uint32_t pcg32_random_r(pcg32_random_t* rng);

/* ------------------------------------------------------------------ */
/* END verbatim third-party header content.                          */
/* BEGIN verbatim third-party code: pcg_basic.c (pcg-c-basic,         */
/* Apache-2.0)                                                         */
/* ------------------------------------------------------------------ */

void pcg32_srandom_r(pcg32_random_t* rng, uint64_t initstate, uint64_t initseq)
{
    rng->state = 0U;
    rng->inc = (initseq << 1u) | 1u;
    pcg32_random_r(rng);
    rng->state += initstate;
    pcg32_random_r(rng);
}

uint32_t pcg32_random_r(pcg32_random_t* rng)
{
    uint64_t oldstate = rng->state;
    rng->state = oldstate * 6364136223846793005ULL + rng->inc;
    uint32_t xorshifted = ((oldstate >> 18u) ^ oldstate) >> 27u;
    uint32_t rot = oldstate >> 59u;
    return (xorshifted >> rot) | (xorshifted << ((-rot) & 31));
}

/* ------------------------------------------------------------------ */
/* END verbatim third-party code.                                    */
/* BEGIN our addition: minimal CLI wrapper (not part of upstream).   */
/* ------------------------------------------------------------------ */

int main(int argc, char **argv)
{
	if (argc < 4) {
		printf("USAGE\n");
		return 0;
	}

	uint64_t initstate = (uint64_t)strtoull(argv[1], NULL, 10);
	uint64_t initseq = (uint64_t)strtoull(argv[2], NULL, 10);
	long count = strtol(argv[3], NULL, 10);

	pcg32_random_t rng;
	pcg32_srandom_r(&rng, initstate, initseq);

	for (long i = 0; i < count; i++) {
		printf("%" PRIu32 "\n", pcg32_random_r(&rng));
	}

	return 0;
}
