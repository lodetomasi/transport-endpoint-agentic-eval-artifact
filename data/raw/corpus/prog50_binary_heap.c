/*
 * prog50_binary_heap.c
 *
 * Binary min-heap (priority queue) stored in a static array, driven
 * by a sequence of commands given as argv tokens:
 *   "Ix"  insert integer x (token starts with 'I', rest is the number)
 *   "X"   extract the minimum
 * Any other token is treated as an invalid command.
 *
 * One result line is printed per command:
 *   "INS x" / "FULL"  for insert
 *   "MIN x" / "EMPTY" for extract-min
 *   "ERR"             for an unrecognized command
 * If there are no commands at all, prints "NOOP".
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_HEAP 16

static long heap[MAX_HEAP];
static int size;

static void sift_up(int i) {
    while (i > 0) {
        int parent = (i - 1) / 2;
        if (heap[parent] <= heap[i]) {
            break;
        }
        long tmp = heap[parent];
        heap[parent] = heap[i];
        heap[i] = tmp;
        i = parent;
    }
}

static void sift_down(int i) {
    while (1) {
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        int smallest = i;
        if (left < size && heap[left] < heap[smallest]) {
            smallest = left;
        }
        if (right < size && heap[right] < heap[smallest]) {
            smallest = right;
        }
        if (smallest == i) {
            break;
        }
        long tmp = heap[smallest];
        heap[smallest] = heap[i];
        heap[i] = tmp;
        i = smallest;
    }
}

static int heap_insert(long v) {
    if (size >= MAX_HEAP) {
        return 0;
    }
    heap[size] = v;
    sift_up(size);
    size++;
    return 1;
}

static int heap_extract_min(long *out) {
    if (size <= 0) {
        return 0;
    }
    *out = heap[0];
    size--;
    heap[0] = heap[size];
    sift_down(0);
    return 1;
}

int main(int argc, char **argv) {
    size = 0;

    if (argc <= 1) {
        printf("NOOP\n");
        return 0;
    }

    for (int i = 1; i < argc; i++) {
        const char *tok = argv[i];

        if (tok[0] == 'I') {
            char *end;
            long v = strtol(tok + 1, &end, 10);
            if (end == tok + 1 || *end != '\0') {
                printf("ERR\n");
                continue;
            }
            if (heap_insert(v)) {
                printf("INS %ld\n", v);
            } else {
                printf("FULL\n");
            }
        } else if (tok[0] == 'X' && tok[1] == '\0') {
            long v;
            if (heap_extract_min(&v)) {
                printf("MIN %ld\n", v);
            } else {
                printf("EMPTY\n");
            }
        } else {
            printf("ERR\n");
        }
    }

    return 0;
}
