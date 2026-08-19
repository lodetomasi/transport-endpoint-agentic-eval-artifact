/*
 * prog02_quicksort.c
 *
 * Recursive quicksort (Lomuto partition scheme) on signed integers
 * passed via argv[1..argc-1]. Prints sorted list space-separated,
 * or "EMPTY" if no arguments given.
 *
 * Deterministic pivot choice: always the last element of the current
 * sub-range, so results do not depend on randomness.
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_N 256

static void swap_long(long *a, long *b) {
    long tmp = *a;
    *a = *b;
    *b = tmp;
}

static int partition(long *arr, int low, int high) {
    long pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap_long(&arr[i], &arr[j]);
        }
    }
    swap_long(&arr[i + 1], &arr[high]);
    return i + 1;
}

static void quicksort(long *arr, int low, int high) {
    if (low < high) {
        int p = partition(arr, low, high);
        quicksort(arr, low, p - 1);
        quicksort(arr, p + 1, high);
    }
}

int main(int argc, char **argv) {
    long values[MAX_N];
    int n = argc - 1;

    if (n <= 0) {
        printf("EMPTY\n");
        return 0;
    }

    if (n > MAX_N) {
        n = MAX_N;
    }

    for (int i = 0; i < n; i++) {
        values[i] = strtol(argv[i + 1], NULL, 10);
    }

    quicksort(values, 0, n - 1);

    for (int i = 0; i < n; i++) {
        if (i > 0) {
            printf(" ");
        }
        printf("%ld", values[i]);
    }
    printf("\n");

    return 0;
}
