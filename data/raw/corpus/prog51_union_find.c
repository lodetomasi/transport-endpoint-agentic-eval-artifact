/*
 * prog51_union_find.c
 *
 * Union-Find (disjoint set) over a fixed universe of N elements
 * (0..N-1), with path compression and union by rank.
 *
 * Commands are read from argv as a flat token sequence:
 *   "U" a b   union the sets containing a and b
 *   "F" a     print the representative (root) of a's set
 *   "C" a b   print YES if a and b are in the same set, else NO
 * Any element index outside 0..N-1 makes the command print
 * "INVALID". An unrecognized opcode also prints "INVALID" and
 * consumes just that one token (so parsing can resynchronize).
 *
 * If there are no tokens at all, prints "NOOP".
 */
#include <stdio.h>
#include <stdlib.h>

#define N 10

static int parent[N];
static int rank_[N];

static void uf_init(void) {
    for (int i = 0; i < N; i++) {
        parent[i] = i;
        rank_[i] = 0;
    }
}

static int uf_find(int x) {
    while (parent[x] != x) {
        parent[x] = parent[parent[x]];
        x = parent[x];
    }
    return x;
}

static void uf_union(int a, int b) {
    int ra = uf_find(a);
    int rb = uf_find(b);
    if (ra == rb) {
        return;
    }
    if (rank_[ra] < rank_[rb]) {
        parent[ra] = rb;
    } else if (rank_[ra] > rank_[rb]) {
        parent[rb] = ra;
    } else {
        parent[rb] = ra;
        rank_[ra]++;
    }
}

static int valid_node(long v) {
    return v >= 0 && v < N;
}

int main(int argc, char **argv) {
    uf_init();

    if (argc <= 1) {
        printf("NOOP\n");
        return 0;
    }

    int i = 1;
    while (i < argc) {
        const char *op = argv[i];

        if (op[0] == 'U' && op[1] == '\0' && i + 2 < argc) {
            long a = strtol(argv[i + 1], NULL, 10);
            long b = strtol(argv[i + 2], NULL, 10);
            if (!valid_node(a) || !valid_node(b)) {
                printf("INVALID\n");
            } else {
                uf_union((int)a, (int)b);
                printf("UNION %ld %ld\n", a, b);
            }
            i += 3;
        } else if (op[0] == 'F' && op[1] == '\0' && i + 1 < argc) {
            long a = strtol(argv[i + 1], NULL, 10);
            if (!valid_node(a)) {
                printf("INVALID\n");
            } else {
                printf("FIND %ld=%d\n", a, uf_find((int)a));
            }
            i += 2;
        } else if (op[0] == 'C' && op[1] == '\0' && i + 2 < argc) {
            long a = strtol(argv[i + 1], NULL, 10);
            long b = strtol(argv[i + 2], NULL, 10);
            if (!valid_node(a) || !valid_node(b)) {
                printf("INVALID\n");
            } else {
                printf("%s\n", uf_find((int)a) == uf_find((int)b) ? "YES" : "NO");
            }
            i += 3;
        } else {
            printf("INVALID\n");
            i += 1;
        }
    }

    return 0;
}
