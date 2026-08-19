/*
 * prog36_pascal_triangle.c
 *
 * Prints the first n rows (argv[1]) of Pascal's triangle, one row per
 * line, values space separated. Rows are built with the additive
 * recurrence (each entry is the sum of the two entries above it) so
 * no factorial is ever computed directly.
 *
 * Assumption: 0 <= n <= 60 (bound enforced at runtime): the largest
 * entry in row 60, C(60,30) = 118264581564861420, together with the
 * additions used to build it, stays safely inside a signed 64-bit
 * long long (max ~9.2e18).
 *
 * n == 0 prints "EMPTY".
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_ROWS 60

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("NO_INPUT\n");
        return 0;
    }

    char *endptr = NULL;
    long n = strtol(argv[1], &endptr, 10);
    if (endptr == argv[1] || *endptr != '\0') {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n < 0) {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n > MAX_ROWS) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    if (n == 0) {
        printf("EMPTY\n");
        return 0;
    }

    long long row[MAX_ROWS + 1];
    row[0] = 1;

    for (long r = 0; r < n; r++) {
        if (r > 0) {
            /* Grow the previous row in place, right to left, so that
             * row[c-1] (needed to compute the new row[c]) has not
             * been overwritten yet when it is read. row[0] is always
             * 1 and is never touched. */
            row[r] = 1;
            for (long c = r - 1; c >= 1; c--) {
                row[c] = row[c] + row[c - 1];
            }
        }

        for (long c = 0; c <= r; c++) {
            if (c > 0) {
                printf(" ");
            }
            printf("%lld", row[c]);
        }
        printf("\n");
    }

    return 0;
}
