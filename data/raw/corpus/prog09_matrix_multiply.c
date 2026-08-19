/*
 * prog09_matrix_multiply.c
 *
 * Multiplies two integer matrices A (R1xC1) and B (R2xC2).
 *
 * argv layout: R1 C1 R2 C2 <R1*C1 values of A, row-major>
 *              <R2*C2 values of B, row-major>
 *
 * Prints the R1xC2 result matrix, one row per line, values space
 * separated. Prints "DIM_MISMATCH" if C1 != R2 (multiplication is not
 * defined). Prints "BAD_INPUT" if not enough arguments are supplied.
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_DIM 16

int main(int argc, char **argv) {
    if (argc < 5) {
        printf("BAD_INPUT\n");
        return 0;
    }

    int r1 = (int)strtol(argv[1], NULL, 10);
    int c1 = (int)strtol(argv[2], NULL, 10);
    int r2 = (int)strtol(argv[3], NULL, 10);
    int c2 = (int)strtol(argv[4], NULL, 10);

    if (r1 <= 0 || c1 <= 0 || r2 <= 0 || c2 <= 0 ||
        r1 > MAX_DIM || c1 > MAX_DIM || r2 > MAX_DIM || c2 > MAX_DIM) {
        printf("BAD_INPUT\n");
        return 0;
    }

    int needed = 5 + r1 * c1 + r2 * c2;
    if (argc < needed) {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (c1 != r2) {
        printf("DIM_MISMATCH\n");
        return 0;
    }

    long a[MAX_DIM][MAX_DIM];
    long b[MAX_DIM][MAX_DIM];
    long result[MAX_DIM][MAX_DIM];

    int idx = 5;
    for (int i = 0; i < r1; i++) {
        for (int j = 0; j < c1; j++) {
            a[i][j] = strtol(argv[idx++], NULL, 10);
        }
    }
    for (int i = 0; i < r2; i++) {
        for (int j = 0; j < c2; j++) {
            b[i][j] = strtol(argv[idx++], NULL, 10);
        }
    }

    for (int i = 0; i < r1; i++) {
        for (int j = 0; j < c2; j++) {
            long sum = 0;
            for (int k = 0; k < c1; k++) {
                sum += a[i][k] * b[k][j];
            }
            result[i][j] = sum;
        }
    }

    for (int i = 0; i < r1; i++) {
        for (int j = 0; j < c2; j++) {
            if (j > 0) {
                printf(" ");
            }
            printf("%ld", result[i][j]);
        }
        printf("\n");
    }

    return 0;
}
