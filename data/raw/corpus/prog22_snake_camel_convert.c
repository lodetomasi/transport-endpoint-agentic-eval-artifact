/*
 * prog22_snake_camel_convert.c
 *
 * argv[1] = mode, one of "to_camel" or "to_snake".
 * argv[2] = identifier string to convert.
 *
 * to_camel: splits argv[2] on '_' characters and produces
 *   lowerCamelCase (first word lowercased as-is except its own first
 *   letter is lowercased, every following word capitalized, all
 *   underscores removed). Consecutive/leading/trailing underscores
 *   produce no extra capitalization events (they are just skipped).
 *
 * to_snake: inserts '_' before every uppercase letter that is not the
 *   first character of the string, then lowercases everything else.
 *   Existing underscores are preserved as-is.
 *
 * Prints the converted string, or "INVALID_MODE" if argv[1] is not
 * one of the two recognized modes, or "USAGE" if fewer than 2
 * arguments are given.
 */
#include <stdio.h>
#include <string.h>

#define MAX_LEN 1024

static char to_upper_ascii(char c) {
    if (c >= 'a' && c <= 'z') {
        return (char)(c - 'a' + 'A');
    }
    return c;
}

static char to_lower_ascii(char c) {
    if (c >= 'A' && c <= 'Z') {
        return (char)(c - 'A' + 'a');
    }
    return c;
}

static void convert_to_camel(const char *s, char *out) {
    size_t out_len = 0;
    int at_word_start = 0;
    int first_char_emitted = 0;

    for (size_t i = 0; s[i] != '\0' && out_len < MAX_LEN; i++) {
        if (s[i] == '_') {
            at_word_start = 1;
            continue;
        }
        char c = s[i];
        if (at_word_start && first_char_emitted) {
            c = to_upper_ascii(c);
        } else {
            c = to_lower_ascii(c);
        }
        out[out_len++] = c;
        at_word_start = 0;
        first_char_emitted = 1;
    }
    out[out_len] = '\0';
}

static void convert_to_snake(const char *s, char *out) {
    size_t out_len = 0;
    for (size_t i = 0; s[i] != '\0' && out_len < MAX_LEN - 1; i++) {
        char c = s[i];
        if (c >= 'A' && c <= 'Z') {
            if (i > 0 && out_len < MAX_LEN - 1) {
                out[out_len++] = '_';
            }
            c = to_lower_ascii(c);
        }
        if (out_len < MAX_LEN) {
            out[out_len++] = c;
        }
    }
    out[out_len] = '\0';
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("USAGE\n");
        return 0;
    }

    const char *mode = argv[1];
    const char *input = argv[2];
    static char out[MAX_LEN + 1];

    if (strcmp(mode, "to_camel") == 0) {
        convert_to_camel(input, out);
    } else if (strcmp(mode, "to_snake") == 0) {
        convert_to_snake(input, out);
    } else {
        printf("INVALID_MODE\n");
        return 0;
    }

    printf("%s\n", out);
    return 0;
}
