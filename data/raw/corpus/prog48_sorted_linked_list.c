/*
 * prog48_sorted_linked_list.c
 *
 * Builds a singly linked list, implemented with a static array of
 * nodes and index-based links (no malloc), inserting each argv value
 * in ascending sorted order. Equal values are inserted after any
 * existing equal values, so relative insertion order among duplicates
 * is preserved.
 *
 * Prints the resulting list space-separated, or "EMPTY" if no values
 * were given.
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_NODES 64
#define NIL (-1)

static long value[MAX_NODES];
static int next[MAX_NODES];
static int head;
static int used;

static void insert_sorted(long v) {
    if (used >= MAX_NODES) {
        return;
    }
    int node = used++;
    value[node] = v;
    next[node] = NIL;

    if (head == NIL || v < value[head]) {
        next[node] = head;
        head = node;
        return;
    }

    int cur = head;
    while (next[cur] != NIL && value[next[cur]] <= v) {
        cur = next[cur];
    }
    next[node] = next[cur];
    next[cur] = node;
}

int main(int argc, char **argv) {
    head = NIL;
    used = 0;

    int n = argc - 1;
    if (n <= 0) {
        printf("EMPTY\n");
        return 0;
    }
    if (n > MAX_NODES) {
        n = MAX_NODES;
    }

    for (int i = 0; i < n; i++) {
        long v = strtol(argv[i + 1], NULL, 10);
        insert_sorted(v);
    }

    int first = 1;
    for (int cur = head; cur != NIL; cur = next[cur]) {
        if (!first) {
            printf(" ");
        }
        printf("%ld", value[cur]);
        first = 0;
    }
    printf("\n");

    return 0;
}
