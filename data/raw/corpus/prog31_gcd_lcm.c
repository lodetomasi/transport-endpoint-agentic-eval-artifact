/*
 * prog31_gcd_lcm.c
 *
 * Computes GCD and LCM of two integers passed as argv[1] and argv[2]
 * using the iterative Euclidean algorithm. Negative inputs are handled
 * via absolute value.
 *
 * Assumption: |a|,|b| <= 1,000,000 so that GCD/LCM and every
 * intermediate multiplication fit safely inside a long without
 * overflow (bound enforced at runtime, see BOUND below).
 *
 * Output: "gcd=<g> lcm=<l>" or an error token, one line.
 */
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define BOUND 1000000L

static long gcd_iter(long a, long b) {
    while (b != 0) {
        long t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("USAGE\n");
        return 0;
    }

    char *end_a = NULL, *end_b = NULL;
    long a = strtol(argv[1], &end_a, 10);
    long b = strtol(argv[2], &end_b, 10);

    if (end_a == argv[1] || *end_a != '\0' || end_b == argv[2] || *end_b != '\0') {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (a == LONG_MIN || b == LONG_MIN) {
        printf("OVERFLOW\n");
        return 0;
    }

    long abs_a = a < 0 ? -a : a;
    long abs_b = b < 0 ? -b : b;

    if (abs_a > BOUND || abs_b > BOUND) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    if (abs_a == 0 && abs_b == 0) {
        printf("gcd=0 lcm=0\n");
        return 0;
    }

    long g = gcd_iter(abs_a, abs_b);

    long lcm;
    if (g == 0) {
        lcm = 0;
    } else {
        lcm = (abs_a / g) * abs_b;
    }

    printf("gcd=%ld lcm=%ld\n", g, lcm);
    return 0;
}
