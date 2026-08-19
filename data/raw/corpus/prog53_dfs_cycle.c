/*
 * prog53_dfs_cycle.c
 *
 * Cycle detection in a directed graph using depth-first search with
 * a three-color scheme (white/gray/black). The graph has a fixed
 * number of nodes (0..N-1); its edges are given as argv pairs
 * "a b" meaning a directed edge a -> b.
 *
 * Prints "CYCLE" if a directed cycle exists, "ACYCLIC" otherwise, or
 * "INVALID_INPUT" if the number of edge-tokens is odd or any node
 * index is out of range.
 */
#include <stdio.h>
#include <stdlib.h>

#define N 8
#define WHITE 0
#define GRAY 1
#define BLACK 2

static int adj[N][N];
static int color[N];
static int found_cycle;

static int valid_node(long v) {
    return v >= 0 && v < N;
}

static void dfs(int u) {
    if (found_cycle) {
        return;
    }
    color[u] = GRAY;
    for (int v = 0; v < N; v++) {
        if (!adj[u][v]) {
            continue;
        }
        if (color[v] == GRAY) {
            found_cycle = 1;
            return;
        }
        if (color[v] == WHITE) {
            dfs(v);
            if (found_cycle) {
                return;
            }
        }
    }
    color[u] = BLACK;
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
    }

    int n_edges = n_tokens / 2;
    for (int i = 0; i < n_edges; i++) {
        long a = strtol(argv[1 + 2 * i], NULL, 10);
        long b = strtol(argv[2 + 2 * i], NULL, 10);
        if (!valid_node(a) || !valid_node(b)) {
            printf("INVALID_INPUT\n");
            return 0;
        }
        adj[a][b] = 1;
    }

    for (int i = 0; i < N; i++) {
        color[i] = WHITE;
    }
    found_cycle = 0;

    for (int i = 0; i < N; i++) {
        if (color[i] == WHITE) {
            dfs(i);
            if (found_cycle) {
                break;
            }
        }
    }

    if (found_cycle) {
        printf("CYCLE\n");
    } else {
        printf("ACYCLIC\n");
    }
    return 0;
}
