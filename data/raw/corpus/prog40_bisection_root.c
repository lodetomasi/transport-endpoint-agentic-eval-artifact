/*
 * prog40_bisection_root.c
 *
 * Approximates sqrt(target) (argv[1], target >= 0) by bisection on
 * f(x) = x*x - target over [0, target+1], which always brackets the
 * root since f(0) <= 0 and f(target+1) > 0 for target >= 0. Runs a
 * FIXED number of iterations (not a floating-point epsilon check) so
 * the result is identical on any conformant IEEE-754 double platform.
 *
 * Assumption: 0 <= target <= 1,000,000 (bound enforced at runtime).
 * The 60 fixed iterations below are far more than enough to converge
 * to full double precision for this range.
 *
 * Output: "%.6f" of the approximate square root, or an error token.
 */
#include <stdio.h>
#include <stdlib.h>

#define BOUND 1000000L
#define ITERATIONS 60

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("NO_INPUT\n");
        return 0;
    }

    char *endptr = NULL;
    long target = strtol(argv[1], &endptr, 10);
    if (endptr == argv[1] || *endptr != '\0') {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (target < 0) {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (target > BOUND) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    double lo = 0.0;
    double hi = (double)target + 1.0;
    double mid = lo;

    for (int i = 0; i < ITERATIONS; i++) {
        mid = lo + (hi - lo) / 2.0;
        if (mid * mid > (double)target) {
            hi = mid;
        } else {
            lo = mid;
        }
    }

    printf("%.6f\n", mid);
    return 0;
}
