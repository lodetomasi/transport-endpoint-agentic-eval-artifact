/*
 * prog46_postfix_stack.c
 *
 * Stack-based evaluator for postfix (RPN) integer expressions.
 * Each argv token is either an integer literal or one of + - * /.
 *
 * Prints the single remaining integer on the stack after processing
 * all tokens, or "ERROR" if the expression is malformed (stack
 * underflow, leftover operands, division by zero, or an unrecognized
 * token).
 */
#include <stdio.h>
#include <stdlib.h>

#define MAX_STACK 64

static long stack[MAX_STACK];
static int top; /* number of elements currently on the stack */

static int push(long v) {
    if (top >= MAX_STACK) {
        return 0;
    }
    stack[top++] = v;
    return 1;
}

static int pop(long *out) {
    if (top <= 0) {
        return 0;
    }
    *out = stack[--top];
    return 1;
}

static int is_operator(const char *tok) {
    return (tok[0] == '+' || tok[0] == '-' || tok[0] == '*' || tok[0] == '/')
        && tok[1] == '\0';
}

static int parse_number(const char *tok, long *out) {
    char *end;
    long v = strtol(tok, &end, 10);
    if (end == tok || *end != '\0') {
        return 0;
    }
    *out = v;
    return 1;
}

int main(int argc, char **argv) {
    int n = argc - 1;
    top = 0;

    if (n <= 0) {
        printf("ERROR\n");
        return 0;
    }
    if (n > MAX_STACK) {
        n = MAX_STACK;
    }

    for (int i = 0; i < n; i++) {
        const char *tok = argv[i + 1];

        if (is_operator(tok)) {
            long b, a;
            if (!pop(&b) || !pop(&a)) {
                printf("ERROR\n");
                return 0;
            }
            long r;
            switch (tok[0]) {
                case '+': r = a + b; break;
                case '-': r = a - b; break;
                case '*': r = a * b; break;
                default:
                    if (b == 0) {
                        printf("ERROR\n");
                        return 0;
                    }
                    r = a / b;
                    break;
            }
            if (!push(r)) {
                printf("ERROR\n");
                return 0;
            }
        } else {
            long v;
            if (!parse_number(tok, &v) || !push(v)) {
                printf("ERROR\n");
                return 0;
            }
        }
    }

    if (top != 1) {
        printf("ERROR\n");
        return 0;
    }

    printf("%ld\n", stack[0]);
    return 0;
}
