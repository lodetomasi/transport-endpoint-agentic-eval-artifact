/*
 * prog03_binary_search.c
 *
 * Iterative binary search. argv[1] is the target value, argv[2..] is a
 * sorted (ascending, caller's responsibility) array of integers. Prints
 * the 0-based index of the target if found, otherwise -1.
 *
 * If fewer than 2 arguments are given (no target, or target but empty
 * array), prints "NO_INPUT". Binary search requires a sorted array as
 * a precondition; if the given array is not non-decreasing, prints
 * "NOT_SORTED" instead of searching it.
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_N 256

static int is_sorted_ascending(const long *arr, int n) {
    for (int i = 1; i < n; i++) {
        if (arr[i - 1] > arr[i]) {
            return 0;
        }
    }
    return 1;
}

static int binary_search(const long *arr, int n, long target) {
    int lo = 0;
    int hi = n - 1;

    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }
    return -1;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("NO_INPUT\n");
        return 0;
    }

    long target = strtol(argv[1], NULL, 10);
    int n = argc - 2;
    if (n > MAX_N) {
        n = MAX_N;
    }

    long values[MAX_N];
    for (int i = 0; i < n; i++) {
        values[i] = strtol(argv[i + 2], NULL, 10);
    }

    if (!is_sorted_ascending(values, n)) {
        printf("NOT_SORTED\n");
        return 0;
    }

    int idx = binary_search(values, n, target);
    printf("%d\n", idx);

    return 0;
}
