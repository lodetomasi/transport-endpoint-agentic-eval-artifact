/*
 * prog33_mod_pow.c
 *
 * Fast modular exponentiation: computes (base ^ exp) mod m for
 * argv[1]=base, argv[2]=exp, argv[3]=m, using square-and-multiply.
 *
 * Assumption: 0 < m <= 1,000,000,000 (bound enforced at runtime), so
 * that any product of two residues modulo m, i.e. up to (m-1)*(m-1)
 * (~1e18), fits safely inside a signed 64-bit long long (max ~9.2e18).
 * exp must be >= 0 (negative exponents are not supported: modular
 * inverse is out of scope for this program).
 *
 * Output: "result=<r>" or an error token, one line.
 */
#include <stdio.h>
#include <stdlib.h>

#define MOD_BOUND 1000000000LL

int main(int argc, char **argv) {
    if (argc < 4) {
        printf("NO_INPUT\n");
        return 0;
    }

    char *end_base = NULL, *end_exp = NULL, *end_mod = NULL;
    long long base = strtoll(argv[1], &end_base, 10);
    long long exp = strtoll(argv[2], &end_exp, 10);
    long long mod = strtoll(argv[3], &end_mod, 10);

    if (end_base == argv[1] || *end_base != '\0' ||
        end_exp == argv[2] || *end_exp != '\0' ||
        end_mod == argv[3] || *end_mod != '\0') {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (mod <= 0) {
        printf("BAD_MODULUS\n");
        return 0;
    }

    if (mod > MOD_BOUND) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    if (exp < 0) {
        printf("NEGATIVE_EXPONENT\n");
        return 0;
    }

    base = base % mod;
    if (base < 0) {
        base += mod;
    }

    long long result = 1 % mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp /= 2;
    }

    printf("result=%lld\n", result);
    return 0;
}
