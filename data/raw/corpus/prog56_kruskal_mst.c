/*
 * prog56_kruskal_mst.c
 *
 * Kruskal's minimum spanning tree algorithm on a small, fixed,
 * hardcoded weighted undirected graph with 6 nodes (0..5) and 9
 * edges. The edges are sorted by ascending weight once, then only
 * the first argv[1] edges of that sorted list are made available to
 * the algorithm (simulating a limited "edge budget"). A negative or
 * missing budget is invalid; a budget larger than the total number
 * of edges is silently clamped to the total.
 *
 * argv[1] = edge budget (integer)
 *
 * Prints "weight=<W> edges=<a0-b0,a1-b1,...>" listing the MST edges
 * in the order they were added, or "DISCONNECTED" if the available
 * edges cannot connect all 6 nodes, or "INVALID_ARGS" if argv[1] is
 * missing or not a valid non-negative integer.
 */
#include <stdio.h>
#include <stdlib.h>

#define NODES 6
#define NUM_EDGES 9

static int edge_a[NUM_EDGES] = { 0, 0, 1, 1, 2, 2, 3, 3, 4 };
static int edge_b[NUM_EDGES] = { 1, 2, 2, 3, 3, 4, 4, 5, 5 };
static int edge_w[NUM_EDGES] = { 4, 1, 2, 5, 8, 10, 2, 6, 3 };

static int parent[NODES];

static int uf_find(int x) {
    while (parent[x] != x) {
        parent[x] = parent[parent[x]];
        x = parent[x];
    }
    return x;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("INVALID_ARGS\n");
        return 0;
    }

    char *end;
    long budget = strtol(argv[1], &end, 10);
    if (end == argv[1] || *end != '\0' || budget < 0) {
        printf("INVALID_ARGS\n");
        return 0;
    }
    if (budget > NUM_EDGES) {
        budget = NUM_EDGES;
    }

    /* sort a working copy of edge indices by ascending weight
       (insertion sort, stable, small N) */
    int order[NUM_EDGES];
    for (int i = 0; i < NUM_EDGES; i++) {
        order[i] = i;
    }
    for (int i = 1; i < NUM_EDGES; i++) {
        int key = order[i];
        int j = i - 1;
        while (j >= 0 && edge_w[order[j]] > edge_w[key]) {
            order[j + 1] = order[j];
            j--;
        }
        order[j + 1] = key;
    }

    for (int i = 0; i < NODES; i++) {
        parent[i] = i;
    }

    int used_a[NODES - 1];
    int used_b[NODES - 1];
    int total_weight = 0;
    int mst_count = 0;

    for (int i = 0; i < budget; i++) {
        int e = order[i];
        int ra = uf_find(edge_a[e]);
        int rb = uf_find(edge_b[e]);
        if (ra != rb) {
            parent[ra] = rb;
            used_a[mst_count] = edge_a[e];
            used_b[mst_count] = edge_b[e];
            total_weight += edge_w[e];
            mst_count++;
        }
    }

    if (mst_count != NODES - 1) {
        printf("DISCONNECTED\n");
        return 0;
    }

    printf("weight=%d edges=", total_weight);
    for (int i = 0; i < mst_count; i++) {
        if (i > 0) {
            printf(",");
        }
        printf("%d-%d", used_a[i], used_b[i]);
    }
    printf("\n");

    return 0;
}
