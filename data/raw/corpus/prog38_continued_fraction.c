/*
 * prog38_continued_fraction.c
 *
 * Converts a fraction num/denom (argv[1], argv[2]) into its simple
 * continued fraction representation [a0; a1, a2, ...], using floor
 * division at every step of the Euclidean algorithm so negative
 * fractions follow the standard mathematical convention.
 *
 * Assumption: |num|,|denom| <= 100,000, denom != 0 (bound enforced at
 * runtime). Under this bound every remainder is strictly smaller in
 * absolute value than its predecessor, so the loop terminates in at
 * most ~30 steps and no multiplication overflows a long. A defensive
 * iteration cap guards against any unexpected non-termination.
 *
 * denom == 0: prints "BAD_INPUT".
 */
#include <stdio.h>
#include <stdlib.h>

#define BOUND 100000L
#define MAX_TERMS 200

static long floor_div(long a, long b) {
    long q = a / b;
    long r = a % b;
    if (r != 0 && ((r < 0) != (b < 0))) {
        q--;
    }
    return q;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("NO_INPUT\n");
        return 0;
    }

    char *end_num = NULL, *end_den = NULL;
    long num = strtol(argv[1], &end_num, 10);
    long den = strtol(argv[2], &end_den, 10);

    if (end_num == argv[1] || *end_num != '\0' || end_den == argv[2] || *end_den != '\0') {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (den == 0) {
        printf("BAD_INPUT\n");
        return 0;
    }

    long abs_num = num < 0 ? -num : num;
    long abs_den = den < 0 ? -den : den;
    if (abs_num > BOUND || abs_den > BOUND) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    long terms_arr[MAX_TERMS];
    int terms = 0;
    long a = num, b = den;

    while (b != 0) {
        if (terms >= MAX_TERMS) {
            printf("ERROR\n");
            return 0;
        }
        long q = floor_div(a, b);
        long r = a - q * b;
        terms_arr[terms] = q;
        terms++;
        a = b;
        b = r;
    }

    printf("[");
    for (int i = 0; i < terms; i++) {
        if (i == 0) {
            printf("%ld", terms_arr[i]);
            if (terms > 1) {
                printf("; ");
            }
        } else {
            if (i > 1) {
                printf(", ");
            }
            printf("%ld", terms_arr[i]);
        }
    }
    printf("]\n");
    return 0;
}
