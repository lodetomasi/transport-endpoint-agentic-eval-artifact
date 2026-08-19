/*
 * prog32_prime_factorization.c
 *
 * Prime factorization of a single positive integer given in argv[1],
 * printed as "p1^e1 p2^e2 ..." in increasing order of prime factor,
 * via trial division up to sqrt(n).
 *
 * Assumption: 1 <= n <= 1,000,000,000 (bound enforced at runtime) so
 * that trial division to sqrt(n) (~31623 steps worst case) finishes
 * quickly and p*p never overflows a long.
 *
 * n <= 1 has no prime factorization: prints "NONE".
 * Missing argument: prints "NO_INPUT". Non-numeric argument: "BAD_INPUT".
 */
#include <stdio.h>
#include <stdlib.h>

#define BOUND 1000000000L

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

    if (n > BOUND) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    if (n <= 1) {
        printf("NONE\n");
        return 0;
    }

    long m = n;
    int first = 1;

    for (long p = 2; p * p <= m; p++) {
        if (m % p == 0) {
            int exp = 0;
            while (m % p == 0) {
                m /= p;
                exp++;
            }
            if (!first) {
                printf(" ");
            }
            printf("%ld^%d", p, exp);
            first = 0;
        }
    }

    if (m > 1) {
        if (!first) {
            printf(" ");
        }
        printf("%ld^1", m);
        first = 0;
    }

    printf("\n");
    return 0;
}
