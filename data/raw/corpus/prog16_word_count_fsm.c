/*
 * prog16_word_count_fsm.c
 *
 * Reads all of stdin and counts characters, words, and lines using a
 * two-state finite state machine (OUTSIDE_WORD / INSIDE_WORD). Byte
 * classification is done through classify_char() with a switch.
 *
 * Conventions (matching POSIX `wc`):
 *   - "chars"  = every byte read from stdin.
 *   - "lines"  = number of '\n' bytes seen. A final unterminated line
 *                (no trailing newline) is NOT counted.
 *   - "words"  = maximal runs of non-whitespace bytes.
 * Whitespace is space, tab, newline, carriage return, vertical tab,
 * and form feed.
 *
 * Output: "LINES=<n> WORDS=<n> CHARS=<n>\n"
 */
#include <stdio.h>

enum char_class { CC_NEWLINE, CC_SPACE, CC_OTHER };
enum wc_state { ST_OUTSIDE, ST_INSIDE };

static enum char_class classify_char(int c) {
    switch (c) {
        case '\n':
            return CC_NEWLINE;
        case ' ':
        case '\t':
        case '\r':
        case '\v':
        case '\f':
            return CC_SPACE;
        default:
            return CC_OTHER;
    }
}

int main(void) {
    long chars = 0;
    long words = 0;
    long lines = 0;
    enum wc_state st = ST_OUTSIDE;
    int c;

    while ((c = getchar()) != EOF) {
        chars++;
        enum char_class cls = classify_char(c);

        if (cls == CC_NEWLINE) {
            lines++;
        }

        switch (st) {
            case ST_OUTSIDE:
                if (cls == CC_OTHER) {
                    words++;
                    st = ST_INSIDE;
                }
                break;
            case ST_INSIDE:
                if (cls != CC_OTHER) {
                    st = ST_OUTSIDE;
                }
                break;
        }
    }

    printf("LINES=%ld WORDS=%ld CHARS=%ld\n", lines, words, chars);
    return 0;
}
