/*
 * prog30_escape_unescape.c
 *
 * argv[1] = mode, one of "escape" or "unescape".
 * argv[2] = text to transform.
 *
 * escape: replaces raw newline, tab, backslash and double-quote bytes
 *   with the two-character sequences \n, \t, \\, \" respectively; all
 *   other bytes pass through unchanged.
 *
 * unescape: replaces the sequences \n, \t, \\, \" with the
 *   corresponding raw byte. Any other backslash escape (including a
 *   trailing lone backslash at end of string) is invalid and makes
 *   the whole result "INVALID".
 *
 * Prints the transformed text, or "INVALID_MODE" if argv[1] is not
 * one of the two modes, or "USAGE" if fewer than 2 arguments given.
 */
#include <stdio.h>
#include <string.h>

#define MAX_LEN 1024

static void do_escape(const char *s, char *out) {
    size_t o = 0;
    for (size_t i = 0; s[i] != '\0' && o < MAX_LEN * 2 - 1; i++) {
        char c = s[i];
        switch (c) {
            case '\n':
                out[o++] = '\\'; out[o++] = 'n';
                break;
            case '\t':
                out[o++] = '\\'; out[o++] = 't';
                break;
            case '\\':
                out[o++] = '\\'; out[o++] = '\\';
                break;
            case '"':
                out[o++] = '\\'; out[o++] = '"';
                break;
            default:
                out[o++] = c;
                break;
        }
    }
    out[o] = '\0';
}

/* Returns 1 on success, 0 if an invalid escape sequence was found. */
static int do_unescape(const char *s, char *out) {
    size_t o = 0;
    size_t len = strlen(s);
    for (size_t i = 0; i < len; i++) {
        char c = s[i];
        if (c != '\\') {
            out[o++] = c;
            continue;
        }
        if (i + 1 >= len) {
            return 0; /* trailing lone backslash */
        }
        char next = s[++i];
        switch (next) {
            case 'n':
                out[o++] = '\n';
                break;
            case 't':
                out[o++] = '\t';
                break;
            case '\\':
                out[o++] = '\\';
                break;
            case '"':
                out[o++] = '"';
                break;
            default:
                return 0;
        }
    }
    out[o] = '\0';
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("USAGE\n");
        return 0;
    }

    const char *mode = argv[1];
    const char *input = argv[2];
    static char out[MAX_LEN * 2];

    if (strlen(input) >= MAX_LEN) {
        printf("USAGE\n");
        return 0;
    }

    if (strcmp(mode, "escape") == 0) {
        do_escape(input, out);
    } else if (strcmp(mode, "unescape") == 0) {
        if (!do_unescape(input, out)) {
            printf("INVALID\n");
            return 0;
        }
    } else {
        printf("INVALID_MODE\n");
        return 0;
    }

    printf("%s\n", out);
    return 0;
}
