/*
 * prog21_date_validator.c
 *
 * Validates that argv[1] is a calendar date in strict "YYYY-MM-DD"
 * format: exactly 4 digits, '-', exactly 2 digits, '-', exactly 2
 * digits (no other characters, no leading '+', fixed field widths).
 * The parser is a small finite state machine over field position and
 * digits-seen-in-field.
 *
 * After the format check, the date is validated against the Gregorian
 * calendar: month in 1..12, day in 1..days_in_month(month, year),
 * with the standard leap year rule (divisible by 4, except centuries
 * not divisible by 400).
 *
 * Prints "VALID" or "INVALID".
 */
#include <stdio.h>
#include <string.h>

static int is_digit(char c) {
    return c >= '0' && c <= '9';
}

static int is_leap_year(int y) {
    if (y % 400 == 0) {
        return 1;
    }
    if (y % 100 == 0) {
        return 0;
    }
    return y % 4 == 0;
}

static int days_in_month(int month, int year) {
    static const int days[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (month == 2 && is_leap_year(year)) {
        return 29;
    }
    return days[month - 1];
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("INVALID\n");
        return 0;
    }

    const char *s = argv[1];
    size_t len = strlen(s);

    if (len != 10) {
        printf("INVALID\n");
        return 0;
    }

    for (size_t i = 0; i < len; i++) {
        int expect_digit = (i != 4 && i != 7);
        if (expect_digit) {
            if (!is_digit(s[i])) {
                printf("INVALID\n");
                return 0;
            }
        } else {
            if (s[i] != '-') {
                printf("INVALID\n");
                return 0;
            }
        }
    }

    int year = (s[0] - '0') * 1000 + (s[1] - '0') * 100 +
               (s[2] - '0') * 10 + (s[3] - '0');
    int month = (s[5] - '0') * 10 + (s[6] - '0');
    int day = (s[8] - '0') * 10 + (s[9] - '0');

    if (month < 1 || month > 12) {
        printf("INVALID\n");
        return 0;
    }

    if (day < 1 || day > days_in_month(month, year)) {
        printf("INVALID\n");
        return 0;
    }

    printf("VALID\n");
    return 0;
}
