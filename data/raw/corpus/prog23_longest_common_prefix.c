/*
 * prog23_longest_common_prefix.c
 *
 * Computes the longest common prefix (LCP) of the strings given as
 * argv[1..argc-1].
 *
 * Prints "EMPTY" if no arguments are given at all. Prints "TOO_MANY"
 * if more than MAX_ARGS strings are given (rejected outright rather
 * than silently considering only a subset). Prints "TOO_LONG" if any
 * single string exceeds MAX_STR_LEN bytes. Otherwise prints the LCP
 * followed by a newline -- this may be an empty line if the strings
 * share no common prefix (including the case of a single
 * empty-string argument, whose LCP with itself is itself: the empty
 * string).
 */
#include <stdio.h>
#include <string.h>

#define MAX_ARGS 64
#define MAX_STR_LEN 1024

static size_t common_prefix_len(const char *a, const char *b, size_t limit) {
    size_t j = 0;
    while (j < limit && a[j] != '\0' && b[j] != '\0' && a[j] == b[j]) {
        j++;
    }
    return j;
}

int main(int argc, char **argv) {
    int n = argc - 1;

    if (n <= 0) {
        printf("EMPTY\n");
        return 0;
    }

    if (n > MAX_ARGS) {
        printf("TOO_MANY\n");
        return 0;
    }

    for (int i = 1; i <= n; i++) {
        if (strlen(argv[i]) > MAX_STR_LEN) {
            printf("TOO_LONG\n");
            return 0;
        }
    }

    const char *first = argv[1];
    size_t prefix_len = strlen(first);

    for (int i = 2; i <= n; i++) {
        prefix_len = common_prefix_len(first, argv[i], prefix_len);
        if (prefix_len == 0) {
            break;
        }
    }

    for (size_t k = 0; k < prefix_len; k++) {
        putchar(first[k]);
    }
    putchar('\n');

    return 0;
}
