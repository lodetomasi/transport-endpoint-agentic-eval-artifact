/*
 * prog26_wildcard_match.c
 *
 * Matches argv[2] (text) against argv[1] (pattern) using shell-style
 * wildcards: '*' matches any sequence of characters (including
 * empty), '?' matches exactly one character, any other character
 * matches itself literally. Matching is computed with an iterative
 * dynamic-programming table (no recursion, so no risk of exponential
 * blow-up on adversarial patterns with many '*').
 *
 * Prints "MATCH" or "NO_MATCH". If either argument is missing, or
 * either string exceeds MAX_LEN bytes, prints "USAGE".
 */
#include <stdio.h>
#include <string.h>

#define MAX_LEN 64

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("USAGE\n");
        return 0;
    }

    const char *pat = argv[1];
    const char *txt = argv[2];
    size_t pn = strlen(pat);
    size_t tn = strlen(txt);

    if (pn > MAX_LEN || tn > MAX_LEN) {
        printf("USAGE\n");
        return 0;
    }

    /* dp[i][j] = pattern[0..i) matches text[0..j) */
    static int dp[MAX_LEN + 1][MAX_LEN + 1];

    for (size_t i = 0; i <= pn; i++) {
        for (size_t j = 0; j <= tn; j++) {
            dp[i][j] = 0;
        }
    }
    dp[0][0] = 1;

    for (size_t i = 1; i <= pn; i++) {
        if (pat[i - 1] == '*') {
            dp[i][0] = dp[i - 1][0];
        }
    }

    for (size_t i = 1; i <= pn; i++) {
        for (size_t j = 1; j <= tn; j++) {
            char pc = pat[i - 1];
            if (pc == '*') {
                dp[i][j] = dp[i - 1][j] || dp[i][j - 1];
            } else if (pc == '?' || pc == txt[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1];
            } else {
                dp[i][j] = 0;
            }
        }
    }

    printf("%s\n", dp[pn][tn] ? "MATCH" : "NO_MATCH");
    return 0;
}
