/*
 * prog29_roman_numeral_parser.c
 *
 * Parses argv[1] as a standard Roman numeral (subtractive notation,
 * values 1..3999; the classical system has no representation for 0
 * or for values >= 4000 without extra vinculum notation, which is
 * out of scope here).
 *
 * Validation strategy: greedily consume the largest matching symbol
 * or subtractive pair (M, CM, D, CD, C, XC, L, XL, X, IX, V, IV, I)
 * from the input to compute a candidate value, then render that
 * candidate value back into its unique canonical Roman form and
 * compare it byte-for-byte against the (uppercased) input. This
 * rejects non-canonical forms such as "IIII", "VV", or "IC" because
 * their canonical rendering would not match the original text.
 *
 * Prints the decimal value, or "INVALID" if argv[1] is missing,
 * contains characters outside "IVXLCDMivxlcdm", is empty, or does not
 * round-trip to itself.
 */
#include <stdio.h>
#include <string.h>

struct sym {
    const char *text;
    int value;
};

static const struct sym SYMS[] = {
    {"M", 1000}, {"CM", 900}, {"D", 500}, {"CD", 400},
    {"C", 100},  {"XC", 90},  {"L", 50},  {"XL", 40},
    {"X", 10},   {"IX", 9},   {"V", 5},   {"IV", 4},
    {"I", 1},
};
#define NUM_SYMS (sizeof(SYMS) / sizeof(SYMS[0]))

static char to_upper_ascii(char c) {
    if (c >= 'a' && c <= 'z') {
        return (char)(c - 'a' + 'A');
    }
    return c;
}

static int is_roman_char(char c) {
    switch (c) {
        case 'I': case 'V': case 'X': case 'L':
        case 'C': case 'D': case 'M':
            return 1;
        default:
            return 0;
    }
}

/* Renders value (1..3999) into out using the canonical greedy form. */
static void render(int value, char *out) {
    size_t pos = 0;
    for (size_t s = 0; s < NUM_SYMS; s++) {
        while (value >= SYMS[s].value) {
            size_t tl = strlen(SYMS[s].text);
            memcpy(out + pos, SYMS[s].text, tl);
            pos += tl;
            value -= SYMS[s].value;
        }
    }
    out[pos] = '\0';
}

int main(int argc, char **argv) {
    if (argc < 2 || argv[1][0] == '\0') {
        printf("INVALID\n");
        return 0;
    }

    static char upper[64];
    size_t len = strlen(argv[1]);
    if (len >= sizeof(upper)) {
        printf("INVALID\n");
        return 0;
    }
    for (size_t i = 0; i < len; i++) {
        char c = to_upper_ascii(argv[1][i]);
        if (!is_roman_char(c)) {
            printf("INVALID\n");
            return 0;
        }
        upper[i] = c;
    }
    upper[len] = '\0';

    /* Greedily parse to get a candidate value. */
    int value = 0;
    size_t i = 0;
    while (i < len) {
        int matched = 0;
        for (size_t s = 0; s < NUM_SYMS; s++) {
            size_t tl = strlen(SYMS[s].text);
            if (i + tl <= len && strncmp(upper + i, SYMS[s].text, tl) == 0) {
                value += SYMS[s].value;
                i += tl;
                matched = 1;
                break;
            }
        }
        if (!matched) {
            printf("INVALID\n");
            return 0;
        }
    }

    if (value < 1 || value > 3999) {
        printf("INVALID\n");
        return 0;
    }

    char canonical[32];
    render(value, canonical);

    if (strcmp(canonical, upper) != 0) {
        printf("INVALID\n");
        return 0;
    }

    printf("%d\n", value);
    return 0;
}
