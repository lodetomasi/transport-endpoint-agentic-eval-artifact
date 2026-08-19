/*
 * prog37_binomial_coefficient.c
 *
 * Computes the binomial coefficient C(n,k) for argv[1]=n, argv[2]=k
 * using Pascal's recursive identity C(n,k)=C(n-1,k-1)+C(n-1,k), with
 * memoization to keep the call count bounded.
 *
 * Assumption: 0 <= n <= 60 (bound enforced at runtime), which keeps
 * every intermediate value (the largest being C(60,30) =
 * 118264581564861420) safely inside a signed 64-bit long long.
 * By convention C(n,k) = 0 when k < 0 or k > n.
 *
 * Output: the decimal value of C(n,k), or an error token.
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_N 60

static long long memo[MAX_N + 1][MAX_N + 1];
static char computed[MAX_N + 1][MAX_N + 1];

static long long binom(int n, int k) {
    if (k < 0 || k > n) {
        return 0;
    }
    if (k == 0 || k == n) {
        return 1;
    }
    if (computed[n][k]) {
        return memo[n][k];
    }
    long long result = binom(n - 1, k - 1) + binom(n - 1, k);
    memo[n][k] = result;
    computed[n][k] = 1;
    return result;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("NO_INPUT\n");
        return 0;
    }

    char *end_n = NULL, *end_k = NULL;
    long n = strtol(argv[1], &end_n, 10);
    long k = strtol(argv[2], &end_k, 10);

    if (end_n == argv[1] || *end_n != '\0' || end_k == argv[2] || *end_k != '\0') {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n < 0 || n > MAX_N) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    printf("%lld\n", binom((int)n, (int)k));
    return 0;
}
