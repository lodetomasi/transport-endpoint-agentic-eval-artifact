/*
 * prog08_base_convert.c
 *
 * Converts a number between two bases.
 *   argv[1] = number string (optional leading '-', digits 0-9 and
 *             letters A-Z/a-z for bases above 10)
 *   argv[2] = source base (2..36)
 *   argv[3] = destination base (2..36)
 *
 * Prints the converted number (uppercase letters), or "INVALID" if the
 * bases are out of range, an argument is missing, or the number string
 * contains a digit not valid in the source base.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int digit_value(char c) {
    if (c >= '0' && c <= '9') {
        return c - '0';
    }
    if (c >= 'A' && c <= 'Z') {
        return c - 'A' + 10;
    }
    if (c >= 'a' && c <= 'z') {
        return c - 'a' + 10;
    }
    return -1;
}

static char value_digit(int v) {
    if (v < 10) {
        return (char)('0' + v);
    }
    return (char)('A' + (v - 10));
}

int main(int argc, char **argv) {
    if (argc < 4) {
        printf("INVALID\n");
        return 0;
    }

    int from_base = (int)strtol(argv[2], NULL, 10);
    int to_base = (int)strtol(argv[3], NULL, 10);

    if (from_base < 2 || from_base > 36 || to_base < 2 || to_base > 36) {
        printf("INVALID\n");
        return 0;
    }

    const char *s = argv[1];
    int negative = 0;
    size_t i = 0;
    if (s[0] == '-') {
        negative = 1;
        i = 1;
    }
    if (s[i] == '\0') {
        printf("INVALID\n");
        return 0;
    }

    long value = 0;
    for (; s[i] != '\0'; i++) {
        int d = digit_value(s[i]);
        if (d < 0 || d >= from_base) {
            printf("INVALID\n");
            return 0;
        }
        value = value * from_base + d;
    }

    if (value == 0) {
        printf("0\n");
        return 0;
    }

    char buf[128];
    int pos = 0;
    while (value > 0) {
        int d = (int)(value % to_base);
        buf[pos++] = value_digit(d);
        value /= to_base;
    }

    if (negative) {
        printf("-");
    }
    for (int j = pos - 1; j >= 0; j--) {
        printf("%c", buf[j]);
    }
    printf("\n");

    return 0;
}
