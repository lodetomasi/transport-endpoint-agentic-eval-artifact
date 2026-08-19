/*
 * prog27_soundex.c
 *
 * Computes the American Soundex code of argv[1], using the classic
 * (Odell-Russell / Knuth) rules:
 *   1. Keep the first letter of the word as-is (uppercased).
 *   2. Map remaining letters to digits:
 *        b,f,p,v       -> 1
 *        c,g,j,k,q,s,x,z -> 2
 *        d,t           -> 3
 *        l             -> 4
 *        m,n           -> 5
 *        r             -> 6
 *        a,e,i,o,u,y,h,w -> (no digit; see rule 3)
 *   3. Two letters with the same digit that are adjacent, or that are
 *      separated only by 'h' or 'w', collapse to a single digit
 *      (i.e. a repeated code digit is not emitted twice). Letters
 *      separated by a vowel (a,e,i,o,u,y) are NOT collapsed even if
 *      they map to the same digit.
 *   4. Stop after 3 digits; pad with trailing zeros if fewer than 3
 *      digits were produced.
 * Non-letter bytes in argv[1] are ignored entirely.
 *
 * Prints the 4-character code (one letter + 3 digits), or "EMPTY" if
 * argv[1] contains no ASCII letters at all (or is missing).
 */
#include <stdio.h>
#include <string.h>

static char to_upper_ascii(char c) {
    if (c >= 'a' && c <= 'z') {
        return (char)(c - 'a' + 'A');
    }
    return c;
}

static int is_letter(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}

/* Returns the soundex digit for an uppercase letter, or 0 if the
 * letter carries no digit (vowels, h, w, y). */
static int soundex_digit(char up) {
    switch (up) {
        case 'B': case 'F': case 'P': case 'V':
            return 1;
        case 'C': case 'G': case 'J': case 'K':
        case 'Q': case 'S': case 'X': case 'Z':
            return 2;
        case 'D': case 'T':
            return 3;
        case 'L':
            return 4;
        case 'M': case 'N':
            return 5;
        case 'R':
            return 6;
        default:
            return 0;
    }
}

static int is_hw(char up) {
    return up == 'H' || up == 'W';
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("EMPTY\n");
        return 0;
    }

    const char *s = argv[1];
    size_t len = strlen(s);

    /* find first letter */
    size_t start = 0;
    while (start < len && !is_letter(s[start])) {
        start++;
    }
    if (start == len) {
        printf("EMPTY\n");
        return 0;
    }

    char code[5];
    code[0] = to_upper_ascii(s[start]);
    int code_len = 1;
    int last_digit = soundex_digit(code[0]);

    for (size_t i = start + 1; i < len && code_len < 4; i++) {
        if (!is_letter(s[i])) {
            continue;
        }
        char up = to_upper_ascii(s[i]);
        if (is_hw(up)) {
            continue; /* transparent separator: does not reset last_digit */
        }
        int d = soundex_digit(up);
        if (d != 0 && d != last_digit) {
            code[code_len++] = (char)('0' + d);
        }
        last_digit = d; /* vowels (d==0) reset the adjacency chain */
    }

    while (code_len < 4) {
        code[code_len++] = '0';
    }
    code[4] = '\0';

    printf("%s\n", code);
    return 0;
}
