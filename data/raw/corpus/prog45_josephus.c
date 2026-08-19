/*
 * prog45_josephus.c
 *
 * Solves the Josephus problem: n people (argv[1]) stand in a circle,
 * every k-th (argv[2]) person is eliminated going around, and the
 * position (1-indexed) of the last survivor is printed. Uses the
 * standard iterative recurrence J(1)=0, J(p) = (J(p-1)+k) mod p.
 *
 * Assumption: 1 <= n <= 1,000,000, 1 <= k <= 1,000,000,000 (bounds
 * enforced at runtime). Under these bounds J(p-1) < p <= n and k are
 * both far below LONG_MAX, so J(p-1)+k cannot overflow a long.
 *
 * Output: the 1-indexed survivor position, or an error token.
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_N 1000000L
#define MAX_K 1000000000L

/*
 * Returns the 0-indexed survivor position for n people, elimination
 * step k, via the iterative recurrence J(1)=0, J(p)=(J(p-1)+k) mod p.
 * Caller guarantees n >= 1 and k >= 1.
 */
static long josephus_survivor(long n, long k) {
    long survivor = 0;
    for (long p = 2; p <= n; p++) {
        survivor = (survivor + k) % p;
    }
    return survivor;
}

static int parse_long(const char *text, long *out) {
    char *endptr = NULL;
    long value = strtol(text, &endptr, 10);
    if (endptr == text || *endptr != '\0') {
        return 0;
    }
    *out = value;
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("NO_INPUT\n");
        return 0;
    }

    long n = 0, k = 0;
    if (!parse_long(argv[1], &n) || !parse_long(argv[2], &k)) {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n < 1 || k < 1) {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n > MAX_N || k > MAX_K) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    printf("%ld\n", josephus_survivor(n, k) + 1);
    return 0;
}
