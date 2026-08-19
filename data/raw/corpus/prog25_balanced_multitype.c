/*
 * prog25_balanced_multitype.c
 *
 * Checks whether argv[1] has balanced brackets across three bracket
 * types: (), [], {}. Every closing bracket must match the most
 * recently opened bracket of the same type (standard stack-based
 * matching); any other character is ignored. A stack overflow (more
 * than MAX_STACK unmatched opens) is treated as "UNBALANCED".
 *
 * Prints "BALANCED" or "UNBALANCED".
 */
#include <stdio.h>
#include <string.h>

#define MAX_STACK 512

static char matching_open(char close) {
    switch (close) {
        case ')':
            return '(';
        case ']':
            return '[';
        case '}':
            return '{';
        default:
            return '\0';
    }
}

static int is_open(char c) {
    return c == '(' || c == '[' || c == '{';
}

static int is_close(char c) {
    return c == ')' || c == ']' || c == '}';
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("BALANCED\n");
        return 0;
    }

    const char *s = argv[1];
    size_t len = strlen(s);

    static char stack[MAX_STACK];
    int top = 0; /* number of items on the stack */
    int ok = 1;

    for (size_t i = 0; i < len; i++) {
        char c = s[i];
        if (is_open(c)) {
            if (top >= MAX_STACK) {
                ok = 0;
                break;
            }
            stack[top++] = c;
        } else if (is_close(c)) {
            if (top == 0 || stack[top - 1] != matching_open(c)) {
                ok = 0;
                break;
            }
            top--;
        }
        /* other characters are ignored */
    }

    if (top != 0) {
        ok = 0;
    }

    printf("%s\n", ok ? "BALANCED" : "UNBALANCED");
    return 0;
}
