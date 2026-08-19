/*
 * prog17_whitespace_trim.c
 *
 * argv[1] is a string. Trims leading and trailing whitespace and
 * collapses every internal run of whitespace into a single space
 * character. Whitespace is space, tab, newline, carriage return,
 * vertical tab, and form feed.
 *
 * Prints the normalized string, or the literal "EMPTY" if the result
 * has zero length (including when argv[1] is missing or entirely
 * whitespace).
 */
#include <stdio.h>
#include <string.h>

#define MAX_LEN 1024

static int is_ws(char c) {
    return c == ' ' || c == '\t' || c == '\n' || c == '\r' ||
           c == '\v' || c == '\f';
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("EMPTY\n");
        return 0;
    }

    const char *s = argv[1];
    size_t len = strlen(s);
    if (len > MAX_LEN) {
        len = MAX_LEN;
    }

    static char out[MAX_LEN + 1];
    size_t out_len = 0;
    int pending_space = 0;
    int started = 0;

    for (size_t i = 0; i < len; i++) {
        char c = s[i];
        if (is_ws(c)) {
            if (started) {
                pending_space = 1;
            }
            continue;
        }

        if (pending_space) {
            out[out_len++] = ' ';
            pending_space = 0;
        }
        out[out_len++] = c;
        started = 1;
    }

    out[out_len] = '\0';

    if (out_len == 0) {
        printf("EMPTY\n");
    } else {
        printf("%s\n", out);
    }

    return 0;
}
