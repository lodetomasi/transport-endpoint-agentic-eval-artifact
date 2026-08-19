/*
 * r17_musl_smoothsort.c
 *
 * REAL CODE, not written for this experiment. Everything between the
 * BEGIN/END verbatim markers below is copied verbatim from musl
 * libc's qsort_r() implementation
 * (https://github.com/kraj/musl/blob/master/src/stdlib/qsort.c, MIT
 * License, Copyright (C) 2011 by Lynn Ochs, minor integration changes
 * by Rich Felker 2011-04-27). This is Dijkstra's Smoothsort, the
 * algorithm musl actually ships as the standard C library `qsort()` /
 * `qsort_r()` on every musl-based Linux system (e.g. Alpine Linux) --
 * i.e. this is production code running on real machines today, not a
 * textbook illustration. See ../corpus_real/PROVENIENZA.md for exact
 * provenance.
 *
 * ADAPTATIONS (documented, not silent):
 *  1. Upstream includes musl's internal "atomic.h" and defines
 *     `ntz(x)` (number of trailing zero bits) as `a_ctz_l(x)`, a
 *     musl-internal atomic-count-trailing-zeros primitive that is
 *     not part of any public header and cannot be pulled in
 *     standalone. `a_ctz_l` and `__builtin_ctzl` compute the exact
 *     same thing (index of the lowest set bit of a nonzero `unsigned
 *     long`), so we define `ntz(x)` as `__builtin_ctzl((unsigned
 *     long)(x))` instead -- a portable compiler builtin available on
 *     GCC and Clang, in place of a musl-private one.
 *  2. Upstream ends with `weak_alias(__qsort_r, qsort_r);`, a
 *     glibc/musl-internal ELF weak-symbol-aliasing macro used so that
 *     musl's libc.so can export both `__qsort_r` and `qsort_r` for
 *     the same code. That macro is not defined outside musl's build.
 *     We name the function `smoothsort_qsort_r` instead of `qsort_r`
 *     -- not just to drop the weak-alias plumbing, but because the
 *     host platform's own <stdlib.h> already declares a `qsort_r`
 *     with a genuinely different, incompatible signature (BSD/macOS:
 *     `qsort_r(base, nel, width, thunk, int(*)(void*,const void*,const
 *     void*))`, thunk-first; musl/glibc: `qsort_r(base, nel, width,
 *     int(*)(const void*,const void*,void*), arg)`, comparator-first).
 *     Reusing the reserved libc name `qsort_r` for a function with a
 *     different ABI is a real conflict (this file fails to compile
 *     on macOS otherwise: "conflicting types for 'qsort_r'"), not a
 *     stylistic choice, so we renamed it. No algorithmic line was
 *     changed.
 *  3. `#define _BSD_SOURCE` (upstream's feature-test macro, needed
 *     only to expose `atomic.h`'s own declarations inside musl's own
 *     build) was dropped, since we no longer include that header.
 *  4. Several comparisons in the verbatim body below (e.g. `n >= 8 *
 *     sizeof(size_t)` where `n` is `int`; `lp[pshift - 1] >= high -
 *     head` mixing `size_t` and pointer difference) trigger
 *     `-Wsign-compare` under `-Wextra`, which musl's own build does
 *     not enable. `cycle()` also stashes the address of a
 *     function-local `tmp[256]` buffer into the caller-supplied `ar[]`
 *     array for the duration of the same call (the pointer never
 *     escapes `cycle()`, so this is safe, but GCC's newer
 *     `-Wdangling-pointer` cannot see that and flags it anyway).
 *     Rather than rewrite upstream's comparisons or restructure its
 *     buffer-passing convention, we bracket the verbatim block in
 *     `#pragma GCC diagnostic ignored "-Wsign-compare"` and
 *     `"-Wdangling-pointer"` so it compiles cleanly under this
 *     corpus's stricter warning flags with zero functional changes.
 *
 * The only other addition (clearly marked below) is a minimal main()
 * that parses argv[1..] as signed longs, sorts them with
 * smoothsort_qsort_r() (see ADAPTATION 2 for the rename) using a
 * plain numeric comparator, and prints the sorted list
 * (mirrors prog01/prog02 of the synthetic corpus, but backed by the
 * real smoothsort implementation shipped in musl libc instead of one
 * written for this study).
 *
 * Usage: r17_musl_smoothsort <int> [<int> ...]
 * Prints the sorted list space-separated, or "EMPTY" if no numbers
 * were given.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* BEGIN verbatim third-party code: qsort.c (musl libc, MIT,          */
/* Copyright (C) 2011 by Lynn Ochs)                                    */
/* ------------------------------------------------------------------ */

/* Smoothsort, an adaptive variant of Heapsort.  Memory usage: O(1).
   Run time: Worst case O(n log n), close to O(n) in the mostly-sorted case. */

#include <stdint.h>

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsign-compare" /* see ADAPTATION 4 above */
#if defined(__GNUC__) && !defined(__clang__)
#pragma GCC diagnostic ignored "-Wdangling-pointer" /* GCC 12+ only, see ADAPTATION 4 above */
#endif

#define ntz(x) ((int)__builtin_ctzl((unsigned long)(x))) /* see ADAPTATION 1 above */

typedef int (*cmpfun)(const void *, const void *, void *);

/* returns index of first bit set, excluding the low bit assumed to always
 * be set, starting from low bit of p[0] up through high bit of p[1] */
static inline int pntz(size_t p[2]) {
	if (p[0] != 1) return ntz(p[0] - 1);
	if (p[1]) return 8*sizeof(size_t) + ntz(p[1]);
	return 0;
}

static void cycle(size_t width, unsigned char* ar[], int n)
{
	unsigned char tmp[256];
	size_t l;
	int i;

	if(n < 2) {
		return;
	}

	ar[n] = tmp;
	while(width) {
		l = sizeof(tmp) < width ? sizeof(tmp) : width;
		memcpy(ar[n], ar[0], l);
		for(i = 0; i < n; i++) {
			memcpy(ar[i], ar[i + 1], l);
			ar[i] += l;
		}
		width -= l;
	}
}

/* shl() and shr() need n > 0 */
static inline void shl(size_t p[2], int n)
{
	if(n >= 8 * sizeof(size_t)) {
		n -= 8 * sizeof(size_t);
		p[1] = p[0];
		p[0] = 0;
		if (!n) return;
	}
	p[1] <<= n;
	p[1] |= p[0] >> (sizeof(size_t) * 8 - n);
	p[0] <<= n;
}

static inline void shr(size_t p[2], int n)
{
	if(n >= 8 * sizeof(size_t)) {
		n -= 8 * sizeof(size_t);
		p[0] = p[1];
		p[1] = 0;
		if (!n) return;
	}
	p[0] >>= n;
	p[0] |= p[1] << (sizeof(size_t) * 8 - n);
	p[1] >>= n;
}

/* power-of-two length for working array so that we can mask indices and
 * not depend on any invariant of the algorithm for spatial memory safety.
 * the original size was just 14*sizeof(size_t)+1 */
#define AR_LEN  (16 * sizeof(size_t))
#define AR_MASK (AR_LEN - 1)

static void sift(unsigned char *head, size_t width, cmpfun cmp, void *arg, int pshift, size_t lp[])
{
	unsigned char *rt, *lf;
	unsigned char *ar[AR_LEN];
	int i = 1;

	ar[0] = head;
	while(pshift > 1) {
		rt = head - width;
		lf = head - width - lp[pshift - 2];

		if(cmp(ar[0], lf, arg) >= 0 && cmp(ar[0], rt, arg) >= 0) {
			break;
		}
		if(cmp(lf, rt, arg) >= 0) {
			ar[i++ & AR_MASK] = lf;
			head = lf;
			pshift -= 1;
		} else {
			ar[i++ & AR_MASK] = rt;
			head = rt;
			pshift -= 2;
		}
	}
	cycle(width, ar, i & AR_MASK);
}

static void trinkle(unsigned char *head, size_t width, cmpfun cmp, void *arg, size_t pp[2], int pshift, int trusty, size_t lp[])
{
	unsigned char *stepson,
	              *rt, *lf;
	size_t p[2];
	unsigned char *ar[AR_LEN];
	int i = 1;
	int trail;

	p[0] = pp[0];
	p[1] = pp[1];

	ar[0] = head;
	while(p[0] != 1 || p[1] != 0) {
		stepson = head - lp[pshift];
		if(cmp(stepson, ar[0], arg) <= 0) {
			break;
		}
		if(!trusty && pshift > 1) {
			rt = head - width;
			lf = head - width - lp[pshift - 2];
			if(cmp(rt, stepson, arg) >= 0 || cmp(lf, stepson, arg) >= 0) {
				break;
			}
		}

		ar[i++ & AR_MASK] = stepson;
		head = stepson;
		trail = pntz(p);
		shr(p, trail);
		pshift += trail;
		trusty = 0;
	}
	if(!trusty) {
		cycle(width, ar, i & AR_MASK);
		sift(head, width, cmp, arg, pshift, lp);
	}
}

void smoothsort_qsort_r(void *base, size_t nel, size_t width, cmpfun cmp, void *arg) /* renamed from qsort_r, see ADAPTATION 2 above */
{
	size_t lp[12*sizeof(size_t)];
	size_t i, size = width * nel;
	unsigned char *head, *high;
	size_t p[2] = {1, 0};
	int pshift = 1;
	int trail;

	if (!size) return;

	head = base;
	high = head + size - width;

	/* Precompute Leonardo numbers, scaled by element width */
	for(lp[0]=lp[1]=width, i=2; (lp[i]=lp[i-2]+lp[i-1]+width) < size; i++);

	while(head < high) {
		if((p[0] & 3) == 3) {
			sift(head, width, cmp, arg, pshift, lp);
			shr(p, 2);
			pshift += 2;
		} else {
			if(lp[pshift - 1] >= high - head) {
				trinkle(head, width, cmp, arg, p, pshift, 0, lp);
			} else {
				sift(head, width, cmp, arg, pshift, lp);
			}

			if(pshift == 1) {
				shl(p, 1);
				pshift = 0;
			} else {
				shl(p, pshift - 1);
				pshift = 1;
			}
		}

		p[0] |= 1;
		head += width;
	}

	trinkle(head, width, cmp, arg, p, pshift, 0, lp);

	while(pshift != 1 || p[0] != 1 || p[1] != 0) {
		if(pshift <= 1) {
			trail = pntz(p);
			shr(p, trail);
			pshift += trail;
		} else {
			shl(p, 2);
			pshift -= 2;
			p[0] ^= 7;
			shr(p, 1);
			trinkle(head - lp[pshift] - width, width, cmp, arg, p, pshift + 1, 1, lp);
			shl(p, 1);
			p[0] |= 1;
			trinkle(head - width, width, cmp, arg, p, pshift, 1, lp);
		}
		head -= width;
	}
}

#pragma GCC diagnostic pop

/* ------------------------------------------------------------------ */
/* END verbatim third-party code.                                    */
/* BEGIN our addition: minimal CLI wrapper (not part of upstream).   */
/* ------------------------------------------------------------------ */

#define MAX_N 256

static int cmp_long(const void *a, const void *b, void *arg)
{
	(void)arg;
	long la = *(const long *)a;
	long lb = *(const long *)b;
	if (la < lb) return -1;
	if (la > lb) return 1;
	return 0;
}

int main(int argc, char **argv)
{
	long values[MAX_N];
	int n = argc - 1;

	if (n <= 0) {
		printf("EMPTY\n");
		return 0;
	}

	if (n > MAX_N) {
		n = MAX_N;
	}

	for (int i = 0; i < n; i++) {
		values[i] = strtol(argv[i + 1], NULL, 10);
	}

	smoothsort_qsort_r(values, (size_t)n, sizeof(long), cmp_long, NULL);

	for (int i = 0; i < n; i++) {
		if (i > 0) {
			printf(" ");
		}
		printf("%ld", values[i]);
	}
	printf("\n");

	return 0;
}
