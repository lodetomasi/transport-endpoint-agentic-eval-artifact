/*
 * prog01_bubble_sort.c
 *
 * Bubble sort on a list of signed integers passed as argv[1..argc-1].
 * Prints the sorted list space-separated, or the literal string "EMPTY"
 * if no numbers were given.
 *
 * Deterministic: no time, no randomness, no file I/O.
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_N 256

static void bubble_sort(long *arr, int n) {
    int i, j;
    for (i = 0; i < n - 1; i++) {
        int swapped = 0;
        for (j = 0; j < n - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) {
                long tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
                swapped = 1;
            }
        }
        if (!swapped) {
            break;
        }
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

    bubble_sort(values, n);

    for (int i = 0; i < n; i++) {
        if (i > 0) {
            printf(" ");
        }
        printf("%ld", values[i]);
    }
    printf("\n");

    return 0;
}
