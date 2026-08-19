/*
 * prog18_caesar_cipher.c
 *
 * Applies a Caesar (shift) cipher to argv[2] using shift amount
 * argv[1] (a signed decimal integer, any magnitude; it is reduced
 * modulo 26 internally, including negative shifts). Letters keep
 * their case; digits, punctuation and all other bytes pass through
 * unchanged.
 *
 * argv[1] must be a valid decimal integer: an optional leading '+' or
 * '-' followed by one or more digits, nothing else. Any other form
 * (empty, trailing garbage, embedded spaces, ...) is rejected.
 *
 * Prints the ciphered text, or "USAGE" if fewer than 2 arguments are
 * given, or if argv[1] is not a well-formed integer, or if argv[2]
 * exceeds MAX_LEN bytes.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LEN 1024

static int is_valid_integer(const char *s) {
    size_t i = 0;
    if (s[0] == '+' || s[0] == '-') {
        i = 1;
    }
    if (s[i] == '\0') {
        return 0; /* sign with no digits */
    }
    for (; s[i] != '\0'; i++) {
        if (s[i] < '0' || s[i] > '9') {
            return 0;
        }
    }
    return 1;
}

static int normalize_shift(long shift) {
    int s = (int)(shift % 26);
    if (s < 0) {
        s += 26;
    }
    return s;
}

static char shift_char(char c, int shift) {
    if (c >= 'a' && c <= 'z') {
        return (char)('a' + (c - 'a' + shift) % 26);
    }
    if (c >= 'A' && c <= 'Z') {
        return (char)('A' + (c - 'A' + shift) % 26);
    }
    return c;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("USAGE\n");
        return 0;
    }

    if (!is_valid_integer(argv[1])) {
        printf("USAGE\n");
        return 0;
    }

    const char *text = argv[2];
    size_t len = strlen(text);
    if (len > MAX_LEN) {
        printf("USAGE\n");
        return 0;
    }

    long raw_shift = strtol(argv[1], NULL, 10);
    int shift = normalize_shift(raw_shift);

    for (size_t i = 0; i < len; i++) {
        putchar(shift_char(text[i], shift));
    }
    putchar('\n');

    return 0;
}
