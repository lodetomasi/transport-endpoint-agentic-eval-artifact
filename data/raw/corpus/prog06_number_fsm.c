/*
 * prog06_number_fsm.c
 *
 * Finite state machine that validates whether argv[1] is a well-formed
 * decimal number matching the grammar:
 *   [+-]? digit+ ('.' digit+)? ([eE] [+-]? digit+)?
 *
 * Prints "VALID" or "INVALID".
 */
#include <stdio.h>
#include <string.h>

enum state {
    ST_START,
    ST_SIGN,
    ST_INT_DIGITS,
    ST_DOT,
    ST_FRAC_DIGITS,
    ST_EXP,
    ST_EXP_SIGN,
    ST_EXP_DIGITS,
    ST_INVALID
};

static int is_digit(char c) {
    return c >= '0' && c <= '9';
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("INVALID\n");
        return 0;
    }

    const char *s = argv[1];
    size_t len = strlen(s);
    enum state st = ST_START;

    for (size_t i = 0; i < len; i++) {
        char c = s[i];
        switch (st) {
            case ST_START:
                if (c == '+' || c == '-') {
                    st = ST_SIGN;
                } else if (is_digit(c)) {
                    st = ST_INT_DIGITS;
                } else {
                    st = ST_INVALID;
                }
                break;
            case ST_SIGN:
                if (is_digit(c)) {
                    st = ST_INT_DIGITS;
                } else {
                    st = ST_INVALID;
                }
                break;
            case ST_INT_DIGITS:
                if (is_digit(c)) {
                    st = ST_INT_DIGITS;
                } else if (c == '.') {
                    st = ST_DOT;
                } else if (c == 'e' || c == 'E') {
                    st = ST_EXP;
                } else {
                    st = ST_INVALID;
                }
                break;
            case ST_DOT:
                if (is_digit(c)) {
                    st = ST_FRAC_DIGITS;
                } else {
                    st = ST_INVALID;
                }
                break;
            case ST_FRAC_DIGITS:
                if (is_digit(c)) {
                    st = ST_FRAC_DIGITS;
                } else if (c == 'e' || c == 'E') {
                    st = ST_EXP;
                } else {
                    st = ST_INVALID;
                }
                break;
            case ST_EXP:
                if (c == '+' || c == '-') {
                    st = ST_EXP_SIGN;
                } else if (is_digit(c)) {
                    st = ST_EXP_DIGITS;
                } else {
                    st = ST_INVALID;
                }
                break;
            case ST_EXP_SIGN:
                if (is_digit(c)) {
                    st = ST_EXP_DIGITS;
                } else {
                    st = ST_INVALID;
                }
                break;
            case ST_EXP_DIGITS:
                if (is_digit(c)) {
                    st = ST_EXP_DIGITS;
                } else {
                    st = ST_INVALID;
                }
                break;
            case ST_INVALID:
                break;
        }
        if (st == ST_INVALID) {
            break;
        }
    }

    int accepting = (st == ST_INT_DIGITS || st == ST_FRAC_DIGITS || st == ST_EXP_DIGITS);
    printf("%s\n", accepting ? "VALID" : "INVALID");

    return 0;
}
