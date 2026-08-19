/*
 * prog39_horner.c
 *
 * Evaluates a polynomial at x using Horner's method. argv[1] is x;
 * argv[2..] are the coefficients, highest degree first (so
 * "2 -1 3" with x=5 means 2*x^2 - x + 3).
 *
 * Assumption: |x| <= 10, at most 12 coefficients, |coefficient| <= 1000
 * (all bounds enforced at runtime). Worst case magnitude reached by
 * the running accumulator is on the order of 1000*10^11 = 1e14, far
 * below the signed 64-bit long long range (~9.2e18), so no
 * multiplication or addition in the Horner loop can overflow.
 *
 * No coefficients given: prints "EMPTY" (the zero polynomial).
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_X 10L
#define MAX_COEFF 1000L
#define MAX_TERMS 12

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("NO_INPUT\n");
        return 0;
    }

    char *end_x = NULL;
    long x = strtol(argv[1], &end_x, 10);
    if (end_x == argv[1] || *end_x != '\0') {
        printf("BAD_INPUT\n");
        return 0;
    }

    long abs_x = x < 0 ? -x : x;
    if (abs_x > MAX_X) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    int n = argc - 2;
    if (n == 0) {
        printf("EMPTY\n");
        return 0;
    }
    if (n > MAX_TERMS) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    long coeffs[MAX_TERMS];
    for (int i = 0; i < n; i++) {
        char *end_c = NULL;
        long c = strtol(argv[i + 2], &end_c, 10);
        if (end_c == argv[i + 2] || *end_c != '\0') {
            printf("BAD_INPUT\n");
            return 0;
        }
        long abs_c = c < 0 ? -c : c;
        if (abs_c > MAX_COEFF) {
            printf("OUT_OF_RANGE\n");
            return 0;
        }
        coeffs[i] = c;
    }

    long long value = 0;
    for (int i = 0; i < n; i++) {
        value = value * x + coeffs[i];
    }

    printf("%lld\n", value);
    return 0;
}
