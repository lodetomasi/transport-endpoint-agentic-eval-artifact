/*
 * prog24_query_string_parser.c
 *
 * Reads a single line from stdin holding a URL-style query string of
 * the form "key1=val1&key2=val2&...". Parses it into ordered
 * key/value pairs and prints one "<key>=<value>" per line.
 *
 * Parsing rules:
 *   - Pairs are separated by '&'.
 *   - A pair with no '=' has an empty value ("key" -> "key=").
 *   - A '+' in either key or value decodes to a literal space.
 *   - "%XX" (two hex digits, upper or lower case) decodes to the byte
 *     0xXX. A malformed percent escape (missing/non-hex digits, or a
 *     '%' with fewer than 2 characters left) is copied through
 *     literally (the '%' and whatever follows it, unmodified).
 *   - An empty pair (from "&&" or a leading/trailing '&') is skipped.
 *
 * If stdin has no line at all, prints "NO_INPUT".
 */
#include <stdio.h>
#include <string.h>

#define MAX_LINE 2048
#define MAX_PAIRS 64

static int hex_value(char c) {
    if (c >= '0' && c <= '9') {
        return c - '0';
    }
    if (c >= 'a' && c <= 'f') {
        return c - 'a' + 10;
    }
    if (c >= 'A' && c <= 'F') {
        return c - 'A' + 10;
    }
    return -1;
}

/* Percent/plus-decodes src (length src_len) into dst, NUL-terminated. */
static void decode(const char *src, size_t src_len, char *dst) {
    size_t o = 0;
    size_t i = 0;
    while (i < src_len) {
        char c = src[i];
        if (c == '+') {
            dst[o++] = ' ';
            i++;
        } else if (c == '%' && i + 2 < src_len) {
            int hi = hex_value(src[i + 1]);
            int lo = hex_value(src[i + 2]);
            if (hi >= 0 && lo >= 0) {
                dst[o++] = (char)((hi << 4) | lo);
                i += 3;
            } else {
                dst[o++] = c;
                i++;
            }
        } else {
            dst[o++] = c;
            i++;
        }
    }
    dst[o] = '\0';
}

int main(void) {
    static char line[MAX_LINE];

    if (!fgets(line, sizeof(line), stdin)) {
        printf("NO_INPUT\n");
        return 0;
    }

    size_t len = strlen(line);
    while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) {
        line[len - 1] = '\0';
        len--;
    }

    int pair_count = 0;
    size_t start = 0;

    for (size_t i = 0; i <= len && pair_count < MAX_PAIRS; i++) {
        if (i == len || line[i] == '&') {
            size_t pair_len = i - start;
            if (pair_len > 0) {
                size_t eq_pos = pair_len;
                for (size_t k = 0; k < pair_len; k++) {
                    if (line[start + k] == '=') {
                        eq_pos = k;
                        break;
                    }
                }
                static char key[MAX_LINE];
                static char val[MAX_LINE];
                decode(line + start, eq_pos, key);
                if (eq_pos < pair_len) {
                    decode(line + start + eq_pos + 1, pair_len - eq_pos - 1, val);
                } else {
                    val[0] = '\0';
                }
                printf("%s=%s\n", key, val);
                pair_count++;
            }
            start = i + 1;
        }
    }

    return 0;
}
