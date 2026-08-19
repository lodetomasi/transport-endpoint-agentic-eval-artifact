/*
 * prog43_catalan.c
 *
 * Computes the n-th Catalan number (argv[1]) via the bottom-up
 * dynamic-programming recurrence C(0)=1,
 * C(i) = sum_{j=0}^{i-1} C(j) * C(i-1-j), using a nested loop.
 *
 * Assumption: 0 <= n <= 30 (bound enforced at runtime): Catalan(30) =
 * 3814986502092304 (~3.8e15), which together with every intermediate
 * product/sum used to reach it stays safely inside a signed 64-bit
 * long long (max ~9.2e18).
 *
 * Output: the decimal value of Catalan(n), or an error token.
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_N 30

/*
 * Fills dp[0..n] with Catalan(0..n) using the standard convolution
 * recurrence and returns Catalan(n). Caller guarantees 0 <= n <= MAX_N.
 */
static long long catalan(long n) {
    long long dp[MAX_N + 1];
    dp[0] = 1;

    for (long i = 1; i <= n; i++) {
        long long total = 0;
        for (long j = 0; j < i; j++) {
            total += dp[j] * dp[i - 1 - j];
        }
        dp[i] = total;
    }

    return dp[n];
}

static int parse_n(const char *text, long *out) {
    char *endptr = NULL;
    long value = strtol(text, &endptr, 10);
    if (endptr == text || *endptr != '\0') {
        return 0;
    }
    *out = value;
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("NO_INPUT\n");
        return 0;
    }

    long n = 0;
    if (!parse_n(argv[1], &n)) {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n < 0) {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n > MAX_N) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    printf("%lld\n", catalan(n));
    return 0;
}
