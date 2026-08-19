/*
 * prog52_bfs_grid.c
 *
 * Breadth-first search shortest path on a small, fixed, hardcoded
 * grid with obstacles ('#'). Open cells are '.'.
 *
 * argv[1] = start row, argv[2] = start col
 * argv[3] = end row,   argv[4] = end col
 *
 * Prints "dist=<D>" (the number of moves on the shortest path), or
 * "UNREACHABLE" if start and end are both open cells but no path
 * connects them, or "INVALID_CELL" if any coordinate is missing,
 * out of range, or lands on an obstacle.
 */
#include <stdio.h>
#include <stdlib.h>

#define ROWS 5
#define COLS 6

static const char grid[ROWS][COLS] = {
    { '.', '.', '.', '#', '.', '.' },
    { '.', '#', '.', '#', '.', '#' },
    { '.', '#', '.', '.', '#', '.' },
    { '.', '#', '#', '#', '.', '#' },
    { '.', '.', '.', '.', '.', '#' },
};

static int visited[ROWS][COLS];
static int dist[ROWS][COLS];
static int q_row[ROWS * COLS];
static int q_col[ROWS * COLS];

static int in_bounds(int r, int c) {
    return r >= 0 && r < ROWS && c >= 0 && c < COLS;
}

int main(int argc, char **argv) {
    if (argc < 5) {
        printf("INVALID_CELL\n");
        return 0;
    }

    int sr = (int)strtol(argv[1], NULL, 10);
    int sc = (int)strtol(argv[2], NULL, 10);
    int er = (int)strtol(argv[3], NULL, 10);
    int ec = (int)strtol(argv[4], NULL, 10);

    if (!in_bounds(sr, sc) || !in_bounds(er, ec) ||
        grid[sr][sc] == '#' || grid[er][ec] == '#') {
        printf("INVALID_CELL\n");
        return 0;
    }

    for (int r = 0; r < ROWS; r++) {
        for (int c = 0; c < COLS; c++) {
            visited[r][c] = 0;
            dist[r][c] = 0;
        }
    }

    int qhead = 0, qtail = 0;
    q_row[qtail] = sr;
    q_col[qtail] = sc;
    qtail++;
    visited[sr][sc] = 1;
    dist[sr][sc] = 0;

    static const int dr[4] = { -1, 1, 0, 0 };
    static const int dc[4] = { 0, 0, -1, 1 };

    while (qhead < qtail) {
        int r = q_row[qhead];
        int c = q_col[qhead];
        qhead++;

        if (r == er && c == ec) {
            printf("dist=%d\n", dist[r][c]);
            return 0;
        }

        for (int k = 0; k < 4; k++) {
            int nr = r + dr[k];
            int nc = c + dc[k];
            if (in_bounds(nr, nc) && grid[nr][nc] != '#' && !visited[nr][nc]) {
                visited[nr][nc] = 1;
                dist[nr][nc] = dist[r][c] + 1;
                q_row[qtail] = nr;
                q_col[qtail] = nc;
                qtail++;
            }
        }
    }

    printf("UNREACHABLE\n");
    return 0;
}
