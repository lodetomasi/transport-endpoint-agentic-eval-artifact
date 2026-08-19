/*
 * prog05_rle.c
 *
 * Run-length encoding of a string given as argv[1]. Each maximal run of
 * identical characters is encoded as "<count><char>". Example:
 * "aaabbc" -> "3a2b1c".
 *
 * If argv[1] is missing, prints "NO_INPUT". If argv[1] is the empty
 * string, prints "EMPTY". Digit characters ('0'-'9') are rejected with
 * "INVALID_CHAR" because they would make the encoded output ambiguous
 * to decode (counts and literal digits could not be told apart).
 */
#include <stdio.h>
#include <string.h>

#define MAX_LEN 1024

static int contains_digit(const char *s, size_t len) {
    for (size_t i = 0; i < len; i++) {
        if (s[i] >= '0' && s[i] <= '9') {
            return 1;
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("NO_INPUT\n");
        return 0;
    }

    const char *s = argv[1];
    size_t len = strlen(s);
    if (len == 0) {
        printf("EMPTY\n");
        return 0;
    }
    if (len > MAX_LEN) {
        len = MAX_LEN;
    }

    if (contains_digit(s, len)) {
        printf("INVALID_CHAR\n");
        return 0;
    }

    size_t i = 0;
    while (i < len) {
        char c = s[i];
        size_t run = 1;
        while (i + run < len && s[i + run] == c) {
            run++;
        }
        printf("%zu%c", run, c);
        i += run;
    }
    printf("\n");

    return 0;
}
