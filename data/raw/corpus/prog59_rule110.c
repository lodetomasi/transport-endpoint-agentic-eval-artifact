/*
 * prog59_rule110.c
 *
 * One-dimensional cellular automaton using Rule 110. The row width
 * is the length of the initial configuration; cells beyond the row's
 * edges are treated as a fixed dead ('0') boundary.
 *
 * argv[1] = initial configuration, a string of '0'/'1' characters
 * argv[2] = number of generations to simulate (>= 0)
 *
 * Prints one line per generation (generation 0 first), each a string
 * of '0'/'1' of the same width as the input.
 *
 * Prints "INVALID_INPUT" if argv[2] is missing, argv[1] is empty,
 * too wide for the internal buffer, contains a character other than
 * '0'/'1', or argv[2] is not a non-negative integer.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_WIDTH 60
#define MAX_GEN 200

/* Rule 110 lookup, indexed by (left<<2 | center<<1 | right). */
static const int RULE110[8] = { 0, 1, 1, 1, 0, 1, 1, 0 };

static char row[2][MAX_WIDTH];

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("INVALID_INPUT\n");
        return 0;
    }

    const char *input = argv[1];
    size_t width = strlen(input);

    if (width == 0 || width > MAX_WIDTH) {
        printf("INVALID_INPUT\n");
        return 0;
    }
    for (size_t i = 0; i < width; i++) {
        if (input[i] != '0' && input[i] != '1') {
            printf("INVALID_INPUT\n");
            return 0;
        }
    }

    char *end;
    long generations = strtol(argv[2], &end, 10);
    if (end == argv[2] || *end != '\0' || generations < 0) {
        printf("INVALID_INPUT\n");
        return 0;
    }
    if (generations > MAX_GEN) {
        generations = MAX_GEN;
    }

    for (size_t i = 0; i < width; i++) {
        row[0][i] = input[i];
    }

    int cur = 0;
    for (int gen = 0; gen <= (int)generations; gen++) {
        for (size_t i = 0; i < width; i++) {
            printf("%c", row[cur][i]);
        }
        printf("\n");

        if (gen == (int)generations) {
            break;
        }

        int next = 1 - cur;
        for (size_t i = 0; i < width; i++) {
            int left = (i == 0) ? 0 : (row[cur][i - 1] - '0');
            int center = row[cur][i] - '0';
            int right = (i == width - 1) ? 0 : (row[cur][i + 1] - '0');
            int idx = (left << 2) | (center << 1) | right;
            row[next][i] = (char)('0' + RULE110[idx]);
        }
        cur = next;
    }

    return 0;
}
