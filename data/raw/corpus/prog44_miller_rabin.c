/*
 * prog44_miller_rabin.c
 *
 * Deterministic Miller-Rabin primality test for argv[1]=n. For
 * n < 3,215,031,751 it is a known result that testing witnesses
 * a in {2,3,5,7} is sufficient to decide primality exactly (no
 * probabilistic error is possible in this range).
 *
 * Assumption: 0 <= n < 3,215,031,751 (bound enforced at runtime). This
 * keeps every value below the modulus n during the test, so any
 * product of two such residues (< n*n < 1.034e19) fits inside an
 * unsigned 64-bit long long (max ~1.844e19) without overflow.
 *
 * Output: "PRIME" or "NOT_PRIME", or an error token.
 */
#include <stdio.h>
#include <stdlib.h>

#define BOUND 3215031751ULL

static unsigned long long mulmod(unsigned long long a, unsigned long long b, unsigned long long m) {
    return (a % m) * (b % m) % m;
}

static unsigned long long modpow(unsigned long long base, unsigned long long exp, unsigned long long m) {
    unsigned long long result = 1 % m;
    base = base % m;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = mulmod(result, base, m);
        }
        base = mulmod(base, base, m);
        exp /= 2;
    }
    return result;
}

static int is_probable_prime(unsigned long long n) {
    if (n < 2) {
        return 0;
    }

    unsigned long long small_primes[] = {2, 3, 5, 7, 11, 13};
    for (int i = 0; i < 6; i++) {
        if (n == small_primes[i]) {
            return 1;
        }
        if (n % small_primes[i] == 0) {
            return 0;
        }
    }

    unsigned long long d = n - 1;
    int r = 0;
    while (d % 2 == 0) {
        d /= 2;
        r++;
    }

    unsigned long long witnesses[] = {2, 3, 5, 7};
    for (int w = 0; w < 4; w++) {
        unsigned long long a = witnesses[w];
        unsigned long long x = modpow(a, d, n);
        if (x == 1 || x == n - 1) {
            continue;
        }
        int composite = 1;
        for (int i = 0; i < r - 1; i++) {
            x = mulmod(x, x, n);
            if (x == n - 1) {
                composite = 0;
                break;
            }
        }
        if (composite) {
            return 0;
        }
    }

    return 1;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("NO_INPUT\n");
        return 0;
    }

    char *endptr = NULL;
    long long n_signed = strtoll(argv[1], &endptr, 10);
    if (endptr == argv[1] || *endptr != '\0') {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n_signed < 0) {
        printf("NOT_PRIME\n");
        return 0;
    }

    if ((unsigned long long)n_signed >= BOUND) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    if (is_probable_prime((unsigned long long)n_signed)) {
        printf("PRIME\n");
    } else {
        printf("NOT_PRIME\n");
    }

    return 0;
}
