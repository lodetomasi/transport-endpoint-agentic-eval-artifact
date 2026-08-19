/*
 * prog04_expr_parser.c
 *
 * Recursive-descent evaluator for simple infix integer arithmetic
 * expressions with +, -, *, /, unary minus, and parentheses.
 * Reads a single line from stdin (no argv input).
 *
 * Output:
 *   the integer result, or
 *   "DIV_ZERO"    if a division by zero occurs
 *   "PARSE_ERROR" if the input is not a well-formed expression
 */
#include <stdio.h>
#include <string.h>

static const char *pos;
static int error_flag; /* 0 = ok, 1 = parse error, 2 = div by zero */

static void skip_spaces(void) {
    while (*pos == ' ') {
        pos++;
    }
}

static long parse_expr(void);

static long parse_factor(void) {
    skip_spaces();
    if (*pos == '-') {
        pos++;
        return -parse_factor();
    }
    if (*pos == '(') {
        pos++;
        long v = parse_expr();
        skip_spaces();
        if (*pos != ')') {
            error_flag = 1;
            return 0;
        }
        pos++;
        return v;
    }
    if (*pos >= '0' && *pos <= '9') {
        long v = 0;
        while (*pos >= '0' && *pos <= '9') {
            v = v * 10 + (*pos - '0');
            pos++;
        }
        return v;
    }
    error_flag = 1;
    return 0;
}

static long parse_term(void) {
    long v = parse_factor();
    skip_spaces();
    while (*pos == '*' || *pos == '/') {
        char op = *pos;
        pos++;
        long rhs = parse_factor();
        if (op == '*') {
            v = v * rhs;
        } else {
            if (rhs == 0) {
                error_flag = 2;
                return 0;
            }
            v = v / rhs;
        }
        skip_spaces();
    }
    return v;
}

static long parse_expr(void) {
    long v = parse_term();
    skip_spaces();
    while (*pos == '+' || *pos == '-') {
        char op = *pos;
        pos++;
        long rhs = parse_term();
        if (op == '+') {
            v = v + rhs;
        } else {
            v = v - rhs;
        }
        skip_spaces();
    }
    return v;
}

int main(void) {
    static char line[1024];
    if (!fgets(line, sizeof(line), stdin)) {
        printf("PARSE_ERROR\n");
        return 0;
    }
    size_t len = strlen(line);
    while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) {
        line[len - 1] = '\0';
        len--;
    }

    pos = line;
    error_flag = 0;
    long result = parse_expr();
    skip_spaces();

    if (error_flag == 2) {
        printf("DIV_ZERO\n");
    } else if (error_flag == 1 || *pos != '\0') {
        printf("PARSE_ERROR\n");
    } else {
        printf("%ld\n", result);
    }

    return 0;
}
