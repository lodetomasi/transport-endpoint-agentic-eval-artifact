/*
 * prog55_connected_components.c
 *
 * Connected components of an undirected graph with a fixed number of
 * nodes (0..N-1), found via breadth-first search. Edges are given as
 * argv pairs "a b". Each component is printed as a brace-enclosed,
 * comma-separated, ascending list of its members; components are
 * printed in ascending order of their smallest member.
 *
 * Output format: "<count>: {members} {members} ...\n"
 *
 * Prints "INVALID_INPUT" if the number of edge-tokens is odd or a
 * node index is out of range.
 */
#include <stdio.h>
#include <stdlib.h>

#define N 8

static int adj[N][N];
static int visited[N];
static int queue_[N];

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
        visited[r] = 0;
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
        adj[b][a] = 1;
    }

    int components[N][N];
    int comp_size[N];
    int comp_count = 0;

    for (int start = 0; start < N; start++) {
        if (visited[start]) {
            continue;
        }
        int qhead = 0, qtail = 0;
        queue_[qtail++] = start;
        visited[start] = 1;

        int members[N];
        int m_len = 0;

        while (qhead < qtail) {
            int u = queue_[qhead++];
            members[m_len++] = u;
            for (int v = 0; v < N; v++) {
                if (adj[u][v] && !visited[v]) {
                    visited[v] = 1;
                    queue_[qtail++] = v;
                }
            }
        }

        /* insertion sort the small member list ascending */
        for (int i = 1; i < m_len; i++) {
            int key = members[i];
            int j = i - 1;
            while (j >= 0 && members[j] > key) {
                members[j + 1] = members[j];
                j--;
            }
            members[j + 1] = key;
        }

        for (int i = 0; i < m_len; i++) {
            components[comp_count][i] = members[i];
        }
        comp_size[comp_count] = m_len;
        comp_count++;
    }

    printf("%d:", comp_count);
    for (int i = 0; i < comp_count; i++) {
        printf(" {");
        for (int j = 0; j < comp_size[i]; j++) {
            if (j > 0) {
                printf(",");
            }
            printf("%d", components[i][j]);
        }
        printf("}");
    }
    printf("\n");

    return 0;
}
