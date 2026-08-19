/*
 * prog54_topo_sort.c
 *
 * Topological sort (Kahn's algorithm) of a directed graph with a
 * fixed number of nodes (0..N-1). Edges are given as argv pairs
 * "a b" meaning a directed edge a -> b. All N nodes always appear in
 * the output, including isolated ones. Ties among nodes with
 * indegree zero are always broken by picking the smallest index
 * first, which makes the result deterministic.
 *
 * Prints the topological order space-separated, or "CYCLE" if the
 * graph has a directed cycle, or "INVALID_INPUT" if the number of
 * edge-tokens is odd or a node index is out of range.
 */
#include <stdio.h>
#include <stdlib.h>

#define N 8

static int adj[N][N];
static int indegree[N];
static int done[N];

static int valid_node(long v) {
    return v >= 0 && v < N;
}

int main(int argc, char **argv) {
    int n_tokens = argc - 1;

    if (n_tokens % 2 != 0) {
        printf("INVALID_INPUT\n");
        return 0;
    }

    for (int r = 0; r < N; r++) {
        for (int c = 0; c < N; c++) {
            adj[r][c] = 0;
        }
        indegree[r] = 0;
        done[r] = 0;
    }

    int n_edges = n_tokens / 2;
    for (int i = 0; i < n_edges; i++) {
        long a = strtol(argv[1 + 2 * i], NULL, 10);
        long b = strtol(argv[2 + 2 * i], NULL, 10);
        if (!valid_node(a) || !valid_node(b)) {
            printf("INVALID_INPUT\n");
            return 0;
        }
        if (!adj[a][b]) {
            adj[a][b] = 1;
            indegree[b]++;
        }
    }

    int order[N];
    int order_len = 0;

    for (int step = 0; step < N; step++) {
        int pick = -1;
        for (int i = 0; i < N; i++) {
            if (!done[i] && indegree[i] == 0) {
                pick = i;
                break;
            }
        }
        if (pick == -1) {
            break;
        }
        done[pick] = 1;
        order[order_len++] = pick;
        for (int v = 0; v < N; v++) {
            if (adj[pick][v]) {
                indegree[v]--;
            }
        }
    }

    if (order_len != N) {
        printf("CYCLE\n");
        return 0;
    }

    for (int i = 0; i < N; i++) {
        if (i > 0) {
            printf(" ");
        }
        printf("%d", order[i]);
    }
    printf("\n");

    return 0;
}
