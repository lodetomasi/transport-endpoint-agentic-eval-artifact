/*
 * prog13_dijkstra.c
 *
 * Dijkstra's shortest path algorithm on a small, fixed, hardcoded
 * undirected weighted graph with 6 nodes (0..5). The graph itself is
 * not part of the input; only the source and destination node are.
 *
 * argv[1] = source node (0..5)
 * argv[2] = destination node (0..5)
 *
 * Prints "dist=<D> path=<n0>-<n1>-...-<nk>", or "UNREACHABLE" if there
 * is no path, or "INVALID_NODE" if source/destination are out of
 * range or arguments are missing.
 */
#include <stdio.h>
#include <stdlib.h>

#define N 6
#define INF 1000000

/* Fixed adjacency matrix. 0 means "no direct edge" except diagonal. */
static const int graph[N][N] = {
    /*      0   1   2   3   4   5 */
    /*0*/ {  0,  4,  1,  0,  0,  0 },
    /*1*/ {  4,  0,  2,  5,  0,  0 },
    /*2*/ {  1,  2,  0,  8, 10,  0 },
    /*3*/ {  0,  5,  8,  0,  2,  6 },
    /*4*/ {  0,  0, 10,  2,  0,  3 },
    /*5*/ {  0,  0,  0,  6,  3,  0 },
};

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("INVALID_NODE\n");
        return 0;
    }

    int src = (int)strtol(argv[1], NULL, 10);
    int dst = (int)strtol(argv[2], NULL, 10);

    if (src < 0 || src >= N || dst < 0 || dst >= N) {
        printf("INVALID_NODE\n");
        return 0;
    }

    int dist[N];
    int prev[N];
    int visited[N];

    for (int i = 0; i < N; i++) {
        dist[i] = INF;
        prev[i] = -1;
        visited[i] = 0;
    }
    dist[src] = 0;

    for (int iter = 0; iter < N; iter++) {
        int u = -1;
        int best = INF;
        for (int i = 0; i < N; i++) {
            if (!visited[i] && dist[i] < best) {
                best = dist[i];
                u = i;
            }
        }
        if (u == -1) {
            break;
        }
        visited[u] = 1;

        for (int v = 0; v < N; v++) {
            int w = graph[u][v];
            if (w > 0 && !visited[v] && dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                prev[v] = u;
            }
        }
    }

    if (dist[dst] >= INF) {
        printf("UNREACHABLE\n");
        return 0;
    }

    int path[N];
    int path_len = 0;
    int cur = dst;
    while (cur != -1) {
        path[path_len++] = cur;
        cur = prev[cur];
    }

    printf("dist=%d path=", dist[dst]);
    for (int i = path_len - 1; i >= 0; i--) {
        printf("%d", path[i]);
        if (i > 0) {
            printf("-");
        }
    }
    printf("\n");

    return 0;
}
