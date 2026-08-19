/*
 * prog19_palindrome_checker.c
 *
 * Checks whether argv[1] is a palindrome after normalization: only
 * ASCII letters and digits are kept, letters are lowercased, every
 * other byte is dropped.
 *
 * Prints "PALINDROME" or "NOT_PALINDROME". A missing argument, or an
 * argument that normalizes to the empty string, is treated as a
 * palindrome (the empty string reads the same forwards and
 * backwards). An argument longer than MAX_LEN bytes (before
 * normalization) is rejected as "TOO_LONG" rather than silently
 * truncated.
 */
#include <stdio.h>
#include <string.h>

#define MAX_LEN 1024

static int is_alnum_ascii(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
           (c >= '0' && c <= '9');
}

static char to_lower_ascii(char c) {
    if (c >= 'A' && c <= 'Z') {
        return (char)(c - 'A' + 'a');
    }
    return c;
}

static void normalize(const char *s, char *out, size_t *out_len) {
    size_t len = strlen(s);
    size_t n = 0;
    for (size_t i = 0; i < len; i++) {
        if (is_alnum_ascii(s[i])) {
            out[n++] = to_lower_ascii(s[i]);
        }
    }
    out[n] = '\0';
    *out_len = n;
}

static int is_palindrome(const char *norm, size_t norm_len) {
    for (size_t i = 0, j = norm_len; i < j; i++) {
        j--;
        if (norm[i] != norm[j]) {
            return 0;
        }
    }
    return 1;
}

int main(int argc, char **argv) {
    static char norm[MAX_LEN + 1];
    size_t norm_len = 0;

    if (argc >= 2) {
        if (strlen(argv[1]) > MAX_LEN) {
            printf("TOO_LONG\n");
            return 0;
        }
        normalize(argv[1], norm, &norm_len);
    } else {
        norm[0] = '\0';
    }

    int is_pal = is_palindrome(norm, norm_len);

    printf("%s\n", is_pal ? "PALINDROME" : "NOT_PALINDROME");
    return 0;
}
