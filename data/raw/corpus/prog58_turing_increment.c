/*
 * prog58_turing_increment.c
 *
 * A tiny Turing machine on a limited tape that increments a binary
 * number by one. The tape holds argv[1] (a string of '0'/'1'
 * characters) left-justified, followed by blanks.
 *
 * States (explicit finite-state machine):
 *   SCAN_RIGHT: move right over digits until a blank is found, then
 *               step onto the last digit and switch to CARRY.
 *   CARRY:      moving left, flip 1->0 and continue left (borrow the
 *               carry); on the first 0, flip it to 1 and halt
 *               successfully. If the carry runs off the left edge of
 *               the written digits (all digits were '1'), there is
 *               no room to grow the tape, so the machine reports
 *               overflow instead of halting normally.
 *
 * Prints "result=<bits> steps=<n>" on success, "OVERFLOW" if the
 * carry cannot be absorbed, or "INVALID_INPUT" if argv[1] is
 * missing, empty, too long for the tape, or contains a character
 * other than '0'/'1'.
 */
#include <stdio.h>
#include <string.h>

#define TAPE_LEN 32

static char tape[TAPE_LEN];

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("INVALID_INPUT\n");
        return 0;
    }

    const char *input = argv[1];
    size_t len = strlen(input);

    if (len == 0 || len > TAPE_LEN - 1) {
        printf("INVALID_INPUT\n");
        return 0;
    }
    for (size_t i = 0; i < len; i++) {
        if (input[i] != '0' && input[i] != '1') {
            printf("INVALID_INPUT\n");
            return 0;
        }
    }

    for (int i = 0; i < TAPE_LEN; i++) {
        tape[i] = '_';
    }
    for (size_t i = 0; i < len; i++) {
        tape[i] = input[i];
    }

    int steps = 0;
    int pos = 0;

    /* SCAN_RIGHT: move right over the digits until the blank. */
    while (tape[pos] == '0' || tape[pos] == '1') {
        pos++;
        steps++;
    }
    pos--; /* step onto the last digit; safe since len >= 1 */
    steps++;

    /* CARRY: move left, flipping bits, until a 0 becomes 1 or we
       run out of room. */
    int overflow = 0;
    while (1) {
        steps++;
        if (tape[pos] == '0') {
            tape[pos] = '1';
            break;
        }
        /* tape[pos] == '1' */
        tape[pos] = '0';
        if (pos == 0) {
            overflow = 1;
            break;
        }
        pos--;
    }

    if (overflow) {
        printf("OVERFLOW\n");
        return 0;
    }

    printf("result=");
    for (size_t i = 0; i < len; i++) {
        printf("%c", tape[i]);
    }
    printf(" steps=%d\n", steps);

    return 0;
}
