/*
 * prog49_bst.c
 *
 * Binary search tree built with a static array of nodes (index-based
 * left/right links, no malloc). Duplicate values are ignored (set
 * semantics: a value already present is not inserted again).
 *
 * argv[1]   = traversal mode: "in", "pre", or "post"
 * argv[2..] = integer values to insert, in the order given
 *
 * Prints the requested traversal, space-separated, or "EMPTY" if no
 * values were inserted, or "INVALID_MODE" if argv[1] is not one of
 * the three recognized modes.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_NODES 64
#define NIL (-1)

static long value[MAX_NODES];
static int left[MAX_NODES];
static int right[MAX_NODES];
static int root;
static int used;
static int printed;

/* Allocates a fresh leaf node holding v and returns its index, or
   NIL if the static node pool is exhausted. */
static int new_node(long v) {
    if (used >= MAX_NODES) {
        return NIL;
    }
    value[used] = v;
    left[used] = NIL;
    right[used] = NIL;
    return used++;
}

static void insert(long v) {
    if (root == NIL) {
        root = new_node(v);
        return;
    }

    int cur = root;
    while (1) {
        if (v == value[cur]) {
            return; /* duplicate: ignore */
        }
        int *child = (v < value[cur]) ? &left[cur] : &right[cur];
        if (*child == NIL) {
            *child = new_node(v);
            return;
        }
        cur = *child;
    }
}

static void emit(long v) {
    if (printed) {
        printf(" ");
    }
    printf("%ld", v);
    printed = 1;
}

static void inorder(int node) {
    if (node == NIL) {
        return;
    }
    inorder(left[node]);
    emit(value[node]);
    inorder(right[node]);
}

static void preorder(int node) {
    if (node == NIL) {
        return;
    }
    emit(value[node]);
    preorder(left[node]);
    preorder(right[node]);
}

static void postorder(int node) {
    if (node == NIL) {
        return;
    }
    postorder(left[node]);
    postorder(right[node]);
    emit(value[node]);
}

int main(int argc, char **argv) {
    root = NIL;
    used = 0;
    printed = 0;

    if (argc < 2) {
        printf("INVALID_MODE\n");
        return 0;
    }

    const char *mode = argv[1];
    if (strcmp(mode, "in") != 0 && strcmp(mode, "pre") != 0 &&
        strcmp(mode, "post") != 0) {
        printf("INVALID_MODE\n");
        return 0;
    }

    int n = argc - 2;
    if (n > MAX_NODES) {
        n = MAX_NODES;
    }
    for (int i = 0; i < n; i++) {
        long v = strtol(argv[i + 2], NULL, 10);
        insert(v);
    }

    if (root == NIL) {
        printf("EMPTY\n");
        return 0;
    }

    if (strcmp(mode, "in") == 0) {
        inorder(root);
    } else if (strcmp(mode, "pre") == 0) {
        preorder(root);
    } else {
        postorder(root);
    }
    printf("\n");

    return 0;
}
