/*
 * prog41_series_sum.c
 *
 * Computes a partial sum of one of three known convergent series,
 * selected by argv[1]=mode over argv[2]=n terms:
 *   mode 1: sum_{k=1}^{n} 1/k^2               (-> pi^2/6)
 *   mode 2: sum_{k=1}^{n} (-1)^(k+1) / k       (-> ln 2)
 *   mode 3: sum_{k=0}^{n} 1/k!                (-> e)
 * Any other mode prints "BAD_MODE".
 *
 * Assumption: 0 <= n <= 100,000 (bound enforced at runtime), chosen
 * only to bound running time; the term-by-term accumulation used
 * below (dividing the running term by k rather than forming k!
 * directly) never overflows a double regardless of n.
 *
 * Output: "%.6f" of the partial sum, or an error token.
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_N 100000L

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("NO_INPUT\n");
        return 0;
    }

    char *end_mode = NULL, *end_n = NULL;
    long mode = strtol(argv[1], &end_mode, 10);
    long n = strtol(argv[2], &end_n, 10);

    if (end_mode == argv[1] || *end_mode != '\0' || end_n == argv[2] || *end_n != '\0') {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n < 0) {
        printf("BAD_INPUT\n");
        return 0;
    }

    if (n > MAX_N) {
        printf("OUT_OF_RANGE\n");
        return 0;
    }

    double sum = 0.0;

    switch (mode) {
        case 1:
            for (long k = 1; k <= n; k++) {
                sum += 1.0 / ((double)k * (double)k);
            }
            break;
        case 2:
            for (long k = 1; k <= n; k++) {
                double term = 1.0 / (double)k;
                if (k % 2 == 0) {
                    term = -term;
                }
                sum += term;
            }
            break;
        case 3: {
            double term = 1.0;
            sum = 1.0;
            for (long k = 1; k <= n; k++) {
                term /= (double)k;
                sum += term;
            }
            break;
        }
        default:
            printf("BAD_MODE\n");
            return 0;
    }

    printf("%.6f\n", sum);
    return 0;
}
