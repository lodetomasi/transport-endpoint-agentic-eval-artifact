/*
 * prog35_perfect_numbers.c
 *
 * Classifies a positive integer n (argv[1]) as "perfect", "abundant"
 * or "deficient" by comparing n to the sum of its proper divisors
 * (all divisors of n strictly less than n).
 *
 * Assumption: 1 <= n <= 1,000,000 (bound enforced at runtime) so that
 * the O(n) divisor-sum loop finishes quickly and the running sum
 * never overflows a long.
 *
 * Output: "n=<n> sum=<s> <class>" or an error token.
 */
#include <stdio.h>
#include <stdlib.h>

#define BOUND 1000000L

static long proper_divisor_sum(long n) {
    long sum = 0;
    for (long i = 1; i < n; i++) {
        if (n % i == 0) {
            sum += i;
        }
    }
    return sum;
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

    if (n < 1) {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n > BOUND) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    long sum = proper_divisor_sum(n);

    int cmp;
    if (sum < n) {
        cmp = -1;
    } else if (sum == n) {
        cmp = 0;
    } else {
        cmp = 1;
    }

    switch (cmp) {
        case -1:
            printf("n=%ld sum=%ld deficient\n", n, sum);
            break;
        case 0:
            printf("n=%ld sum=%ld perfect\n", n, sum);
            break;
        default:
            printf("n=%ld sum=%ld abundant\n", n, sum);
            break;
    }

    return 0;
}
