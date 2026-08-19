/*
 * prog07_stats.c
 *
 * Computes mean, median, and population variance of a list of integers
 * given as argv[1..argc-1]. Population variance is used (divide by n,
 * not n-1) since the input is treated as the full data set, not a
 * sample.
 *
 * Output format: "mean=%.4f median=%.4f variance=%.4f"
 * If no numbers are given, prints "NO_DATA".
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_N 256

static void sort_ascending(double *arr, int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) {
                double tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
}

static double compute_mean(const double *arr, int n) {
    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum / (double)n;
}

static double compute_median(double *arr, int n) {
    double sorted_copy[MAX_N];
    for (int i = 0; i < n; i++) {
        sorted_copy[i] = arr[i];
    }
    sort_ascending(sorted_copy, n);

    if (n % 2 == 1) {
        return sorted_copy[n / 2];
    } else {
        return (sorted_copy[n / 2 - 1] + sorted_copy[n / 2]) / 2.0;
    }
}

static double compute_variance(const double *arr, int n, double mean) {
    double sum_sq_diff = 0.0;
    for (int i = 0; i < n; i++) {
        double diff = arr[i] - mean;
        sum_sq_diff += diff * diff;
    }
    return sum_sq_diff / (double)n;
}

int main(int argc, char **argv) {
    int n = argc - 1;
    if (n <= 0) {
        printf("NO_DATA\n");
        return 0;
    }
    if (n > MAX_N) {
        n = MAX_N;
    }

    double values[MAX_N];
    for (int i = 0; i < n; i++) {
        values[i] = strtod(argv[i + 1], NULL);
    }

    double mean = compute_mean(values, n);
    double median = compute_median(values, n);
    double variance = compute_variance(values, n, mean);

    printf("mean=%.4f median=%.4f variance=%.4f\n", mean, median, variance);

    return 0;
}
