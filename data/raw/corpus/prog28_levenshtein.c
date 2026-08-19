/*
 * prog28_levenshtein.c
 *
 * Computes the Levenshtein edit distance between argv[1] and argv[2]
 * (minimum number of single-character insertions, deletions, or
 * substitutions to turn one string into the other), via the standard
 * iterative dynamic-programming table.
 *
 * Prints the integer distance, or "TOO_LONG" if either string exceeds
 * MAX_LEN bytes, or "USAGE" if fewer than 2 arguments are given.
 */
#include <stdio.h>
#include <string.h>

#define MAX_LEN 64

static int min3(int a, int b, int c) {
    int m = a;
    if (b < m) {
        m = b;
    }
    if (c < m) {
        m = c;
    }
    return m;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("USAGE\n");
        return 0;
    }

    const char *a = argv[1];
    const char *b = argv[2];
    size_t an = strlen(a);
    size_t bn = strlen(b);

    if (an > MAX_LEN || bn > MAX_LEN) {
        printf("TOO_LONG\n");
        return 0;
    }

    static int dp[MAX_LEN + 1][MAX_LEN + 1];

    for (size_t i = 0; i <= an; i++) {
        dp[i][0] = (int)i;
    }
    for (size_t j = 0; j <= bn; j++) {
        dp[0][j] = (int)j;
    }

    for (size_t i = 1; i <= an; i++) {
        for (size_t j = 1; j <= bn; j++) {
            if (a[i - 1] == b[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1];
            } else {
                int deletion = dp[i - 1][j] + 1;
                int insertion = dp[i][j - 1] + 1;
                int substitution = dp[i - 1][j - 1] + 1;
                dp[i][j] = min3(deletion, insertion, substitution);
            }
        }
    }

    printf("%d\n", dp[an][bn]);
    return 0;
}
