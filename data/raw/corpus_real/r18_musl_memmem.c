/*
 * r18_musl_memmem.c
 *
 * REAL CODE, not written for this experiment. Everything between the
 * BEGIN/END verbatim markers below is copied verbatim from musl
 * libc's memmem() implementation
 * (https://github.com/kraj/musl/blob/master/src/string/memmem.c, MIT
 * License). This implements the two-way string-matching algorithm
 * (Crochemore & Perrin) for the general case, with small hand-coded
 * fast paths for 2/3/4-byte needles; it is the actual memmem() every
 * musl-based Linux system (e.g. Alpine Linux) calls when a program
 * uses the POSIX memmem() function. See
 * ../corpus_real/PROVENIENZA.md for exact provenance.
 *
 * ADAPTATION (documented, not silent): `twoway_memmem()` compares a
 * pointer difference (`z - h`, type `ptrdiff_t`/`long`) against `l`
 * (type `size_t`) in `if (z-h < l) return 0;`. This trips
 * `-Wsign-compare` under `-Wextra`, which musl's own build does not
 * enable. Rather than rewrite the comparison, we bracket the verbatim
 * block in `#pragma GCC diagnostic ignored "-Wsign-compare"` so it
 * compiles cleanly under this corpus's stricter warning flags with
 * zero functional changes. Otherwise no adaptation was needed: this
 * file only includes <string.h> and <stdint.h>, both standard, and
 * defines a single self-contained function.
 *
 * The only addition (clearly marked below) is a minimal main() that
 * searches for argv[2] inside argv[1] using memmem() and prints the
 * byte offset of the first match, or "NOT_FOUND", so the library can
 * be exercised as a standalone CLI program.
 *
 * Usage: r18_musl_memmem <haystack> <needle>
 * Prints the 0-based byte offset of the first occurrence of <needle>
 * in <haystack>, or "NOT_FOUND", or "USAGE" if fewer than two
 * arguments were given.
 */
#include <stdio.h>
#include <string.h>
#include <stdint.h>

/* ------------------------------------------------------------------ */
/* BEGIN verbatim third-party code: memmem.c (musl libc, MIT)         */
/* ------------------------------------------------------------------ */

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsign-compare" /* see ADAPTATION note above */

static char *twobyte_memmem(const unsigned char *h, size_t k, const unsigned char *n)
{
	uint16_t nw = n[0]<<8 | n[1], hw = h[0]<<8 | h[1];
	for (h+=2, k-=2; k; k--, hw = hw<<8 | *h++)
		if (hw == nw) return (char *)h-2;
	return hw == nw ? (char *)h-2 : 0;
}

static char *threebyte_memmem(const unsigned char *h, size_t k, const unsigned char *n)
{
	uint32_t nw = (uint32_t)n[0]<<24 | n[1]<<16 | n[2]<<8;
	uint32_t hw = (uint32_t)h[0]<<24 | h[1]<<16 | h[2]<<8;
	for (h+=3, k-=3; k; k--, hw = (hw|*h++)<<8)
		if (hw == nw) return (char *)h-3;
	return hw == nw ? (char *)h-3 : 0;
}

static char *fourbyte_memmem(const unsigned char *h, size_t k, const unsigned char *n)
{
	uint32_t nw = (uint32_t)n[0]<<24 | n[1]<<16 | n[2]<<8 | n[3];
	uint32_t hw = (uint32_t)h[0]<<24 | h[1]<<16 | h[2]<<8 | h[3];
	for (h+=4, k-=4; k; k--, hw = hw<<8 | *h++)
		if (hw == nw) return (char *)h-4;
	return hw == nw ? (char *)h-4 : 0;
}

#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))

#define BITOP(a,b,op) \
 ((a)[(size_t)(b)/(8*sizeof *(a))] op (size_t)1<<((size_t)(b)%(8*sizeof *(a))))

static char *twoway_memmem(const unsigned char *h, const unsigned char *z, const unsigned char *n, size_t l)
{
	size_t i, ip, jp, k, p, ms, p0, mem, mem0;
	size_t byteset[32 / sizeof(size_t)] = { 0 };
	size_t shift[256];

	/* Computing length of needle and fill shift table */
	for (i=0; i<l; i++)
		BITOP(byteset, n[i], |=), shift[n[i]] = i+1;

	/* Compute maximal suffix */
	ip = -1; jp = 0; k = p = 1;
	while (jp+k<l) {
		if (n[ip+k] == n[jp+k]) {
			if (k == p) {
				jp += p;
				k = 1;
			} else k++;
		} else if (n[ip+k] > n[jp+k]) {
			jp += k;
			k = 1;
			p = jp - ip;
		} else {
			ip = jp++;
			k = p = 1;
		}
	}
	ms = ip;
	p0 = p;

	/* And with the opposite comparison */
	ip = -1; jp = 0; k = p = 1;
	while (jp+k<l) {
		if (n[ip+k] == n[jp+k]) {
			if (k == p) {
				jp += p;
				k = 1;
			} else k++;
		} else if (n[ip+k] < n[jp+k]) {
			jp += k;
			k = 1;
			p = jp - ip;
		} else {
			ip = jp++;
			k = p = 1;
		}
	}
	if (ip+1 > ms+1) ms = ip;
	else p = p0;

	/* Periodic needle? */
	if (memcmp(n, n+p, ms+1)) {
		mem0 = 0;
		p = MAX(ms, l-ms-1) + 1;
	} else mem0 = l-p;
	mem = 0;

	/* Search loop */
	for (;;) {
		/* If remainder of haystack is shorter than needle, done */
		if (z-h < l) return 0;

		/* Check last byte first; advance by shift on mismatch */
		if (BITOP(byteset, h[l-1], &)) {
			k = l-shift[h[l-1]];
			if (k) {
				if (k < mem) k = mem;
				h += k;
				mem = 0;
				continue;
			}
		} else {
			h += l;
			mem = 0;
			continue;
		}

		/* Compare right half */
		for (k=MAX(ms+1,mem); k<l && n[k] == h[k]; k++);
		if (k < l) {
			h += k-ms;
			mem = 0;
			continue;
		}
		/* Compare left half */
		for (k=ms+1; k>mem && n[k-1] == h[k-1]; k--);
		if (k <= mem) return (char *)h;
		h += p;
		mem = mem0;
	}
}

void *memmem(const void *h0, size_t k, const void *n0, size_t l)
{
	const unsigned char *h = h0, *n = n0;

	/* Return immediately on empty needle */
	if (!l) return (void *)h;

	/* Return immediately when needle is longer than haystack */
	if (k<l) return 0;

	/* Use faster algorithms for short needles */
	h = memchr(h0, *n, k);
	if (!h || l==1) return (void *)h;
	k -= h - (const unsigned char *)h0;
	if (k<l) return 0;
	if (l==2) return twobyte_memmem(h, k, n);
	if (l==3) return threebyte_memmem(h, k, n);
	if (l==4) return fourbyte_memmem(h, k, n);

	return twoway_memmem(h, h+k, n, l);
}

#pragma GCC diagnostic pop

/* ------------------------------------------------------------------ */
/* END verbatim third-party code.                                    */
/* BEGIN our addition: minimal CLI wrapper (not part of upstream).   */
/* ------------------------------------------------------------------ */

int main(int argc, char **argv)
{
	if (argc < 3) {
		printf("USAGE\n");
		return 0;
	}

	const char *haystack = argv[1];
	const char *needle = argv[2];
	size_t haystack_len = strlen(haystack);
	size_t needle_len = strlen(needle);

	void *found = memmem(haystack, haystack_len, needle, needle_len);

	if (!found) {
		printf("NOT_FOUND\n");
		return 0;
	}

	printf("%ld\n", (long)((char *)found - haystack));

	return 0;
}
