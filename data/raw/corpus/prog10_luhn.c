/*
 * prog10_luhn.c
 *
 * Validates a numeric string (e.g. a credit card number) against the
 * Luhn checksum algorithm. argv[1] is the digit string.
 *
 * Prints "VALID" or "INVALID". A string containing any non-digit
 * character, or with fewer than 2 digits, is "INVALID". A string
 * longer than MAX_LEN digits (far beyond any real payment card
 * number) is rejected as "TOO_LONG" rather than silently truncated.
 */
#include <stdio.h>
#include <string.h>

#define MAX_LEN 32

static int all_digits(const char *s, size_t len) {
    for (size_t i = 0; i < len; i++) {
        if (s[i] < '0' || s[i] > '9') {
            return 0;
        }
    }
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("INVALID\n");
        return 0;
    }

    const char *s = argv[1];
    size_t len = strlen(s);

    if (len < 2) {
        printf("INVALID\n");
        return 0;
    }

    if (len > MAX_LEN) {
        printf("TOO_LONG\n");
        return 0;
    }

    if (!all_digits(s, len)) {
        printf("INVALID\n");
        return 0;
    }

    int sum = 0;
    int double_it = 0; /* start from the rightmost digit, don't double it */

    for (long i = (long)len - 1; i >= 0; i--) {
        int digit = s[i] - '0';
        if (double_it) {
            digit *= 2;
            if (digit > 9) {
                digit -= 9;
            }
        }
        sum += digit;
        double_it = !double_it;
    }

    if (sum % 10 == 0) {
        printf("VALID\n");
    } else {
        printf("INVALID\n");
    }

    return 0;
}
