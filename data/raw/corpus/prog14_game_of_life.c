/*
 * prog14_game_of_life.c
 *
 * Conway's Game of Life on a small fixed-size grid, run for a given
 * number of generations. Cells outside the grid are always dead (no
 * wrap-around / no torus topology).
 *
 * stdin format:
 *   line 1: "<generations> <rows> <cols>"
 *   next <rows> lines: <cols> characters, '#' = alive, '.' = dead
 *
 * Prints the grid after evolving it for <generations> steps, one row
 * per line, same alphabet ('#'/'.'). Prints "BAD_INPUT" if the header
 * is malformed or dimensions exceed the fixed maximum size.
 */
#include <stdio.h>
#include <string.h>

#define MAX_DIM 16

static char cur[MAX_DIM][MAX_DIM];
static char next_gen[MAX_DIM][MAX_DIM];

static int count_neighbors(int rows, int cols, int r, int c) {
    int count = 0;
    for (int dr = -1; dr <= 1; dr++) {
        for (int dc = -1; dc <= 1; dc++) {
            if (dr == 0 && dc == 0) {
                continue;
            }
            int rr = r + dr;
            int cc = c + dc;
            if (rr >= 0 && rr < rows && cc >= 0 && cc < cols) {
                if (cur[rr][cc] == '#') {
                    count++;
                }
            }
        }
    }
    return count;
}

int main(void) {
    int generations, rows, cols;

    if (scanf("%d %d %d", &generations, &rows, &cols) != 3) {
        printf("BAD_INPUT\n");
        return 0;
    }
    if (rows <= 0 || cols <= 0 || rows > MAX_DIM || cols > MAX_DIM || generations < 0) {
        printf("BAD_INPUT\n");
        return 0;
    }

    /* consume the rest of the header line */
    int ch;
    while ((ch = getchar()) != '\n' && ch != EOF) {
        /* discard */
    }

    char line[MAX_DIM + 2];
    for (int r = 0; r < rows; r++) {
        if (!fgets(line, sizeof(line), stdin)) {
            printf("BAD_INPUT\n");
            return 0;
        }
        for (int c = 0; c < cols; c++) {
            cur[r][c] = (line[c] == '#') ? '#' : '.';
        }
    }

    for (int g = 0; g < generations; g++) {
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                int n = count_neighbors(rows, cols, r, c);
                if (cur[r][c] == '#') {
                    next_gen[r][c] = (n == 2 || n == 3) ? '#' : '.';
                } else {
                    next_gen[r][c] = (n == 3) ? '#' : '.';
                }
            }
        }
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                cur[r][c] = next_gen[r][c];
            }
        }
    }

    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
            putchar(cur[r][c]);
        }
        putchar('\n');
    }

    return 0;
}
