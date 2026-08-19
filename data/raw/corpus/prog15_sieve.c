/*
 * prog15_sieve.c
 *
 * Sieve of Eratosthenes. argv[1] = N (upper bound, inclusive). Prints
 * all primes <= N, space separated. Prints "NONE" if N < 2. Prints
 * "NO_INPUT" if argv[1] is missing. Prints "BAD_INPUT" if argv[1] is
 * not a valid base-10 integer (e.g. contains letters). N is capped at
 * 1,000,000 to bound memory use; larger requests are truncated to
 * that cap.
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_N 1000000

static char is_composite[MAX_N + 1];

static int count_primes(long n) {
    int count = 0;
    for (long i = 2; i <= n; i++) {
        if (!is_composite[i]) {
            count++;
        }
    }
    return count;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("NO_INPUT\n");
        return 0;
    }

    char *endptr = NULL;
    long n = strtol(argv[1], &endptr, 10);
    if (endptr == argv[1] || *endptr != '\0') {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n > MAX_N) {
        n = MAX_N;
    }
    if (n < 2) {
        printf("NONE\n");
        return 0;
    }

    for (long i = 0; i <= n; i++) {
        is_composite[i] = 0;
    }

    for (long p = 2; p * p <= n; p++) {
        if (!is_composite[p]) {
            for (long multiple = p * p; multiple <= n; multiple += p) {
                is_composite[multiple] = 1;
            }
        }
    }

    /* Diagnostic only, does not affect the stdout list of primes. */
    fprintf(stderr, "note: found %d primes up to %ld\n", count_primes(n), n);

    int first = 1;
    for (long i = 2; i <= n; i++) {
        if (!is_composite[i]) {
            if (!first) {
                printf(" ");
            }
            printf("%ld", i);
            first = 0;
        }
    }
    printf("\n");

    return 0;
}
