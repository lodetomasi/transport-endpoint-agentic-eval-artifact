/*
 * prog34_fibonacci_memo.c
 *
 * Computes the n-th Fibonacci number (F(0)=0, F(1)=1) via top-down
 * recursion with memoization, for argv[1]=n.
 *
 * Assumption: 0 <= n <= 90 (bound enforced at runtime), since
 * F(90) = 2880067194370816120 is the largest Fibonacci value that
 * still fits comfortably inside a signed 64-bit long long
 * (max ~9.2e18) without overflow; F(93) would already overflow it.
 *
 * Output: the decimal value of F(n), or an error token.
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_N 90

static long long memo[MAX_N + 1];
static char computed[MAX_N + 1];

static long long fib(int n) {
    if (n == 0) {
        return 0;
    }
    if (n == 1) {
        return 1;
    }
    if (computed[n]) {
        return memo[n];
    }
    long long result = fib(n - 1) + fib(n - 2);
    memo[n] = result;
    computed[n] = 1;
    return result;
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

    if (n < 0) {
        printf("NEGATIVE\n");
        return 0;
    }

    if (n > MAX_N) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    printf("%lld\n", fib((int)n));
    return 0;
}
