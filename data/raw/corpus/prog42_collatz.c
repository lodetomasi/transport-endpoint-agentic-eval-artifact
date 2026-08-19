/*
 * prog42_collatz.c
 *
 * Counts the number of Collatz steps for a starting value n (argv[1])
 * to reach 1, under the rule: n -> n/2 if even, n -> 3n+1 if odd.
 *
 * Assumption: 1 <= n <= 1,000,000,000 (bound enforced at runtime). The
 * Collatz conjecture has been verified computationally far beyond
 * this range, so every such n is known to reach 1; a defensive
 * iteration cap (STEP_LIMIT) and a defensive magnitude cap
 * (VALUE_LIMIT, using unsigned long long) guard against non-
 * termination or overflow even if that were not the case.
 *
 * Output: "n=<n> steps=<count>" or an error token.
 */
#include <stdio.h>
#include <stdlib.h>

#define BOUND 1000000000L
#define STEP_LIMIT 1000000L
#define VALUE_LIMIT 1000000000000000ULL

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("NO_INPUT\n");
        return 0;
    }

    char *endptr = NULL;
    long start = strtol(argv[1], &endptr, 10);
    if (endptr == argv[1] || *endptr != '\0') {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (start < 1) {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (start > BOUND) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    unsigned long long n = (unsigned long long)start;
    long steps = 0;

    while (n != 1) {
        if (steps >= STEP_LIMIT) {
            printf("STEP_LIMIT_EXCEEDED\n");
            return 0;
        }
        if (n > VALUE_LIMIT) {
            printf("OVERFLOW_GUARD\n");
            return 0;
        }
        if (n % 2 == 0) {
            n /= 2;
        } else {
            n = 3 * n + 1;
        }
        steps++;
    }

    printf("n=%ld steps=%ld\n", start, steps);
    return 0;
}
