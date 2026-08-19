/*
 * prog20_anagram_checker.c
 *
 * Checks whether argv[1] and argv[2] are anagrams of each other.
 * Normalization before comparison: ASCII letters are lowercased,
 * spaces are ignored, every other byte (digits, punctuation, ...) is
 * counted as-is.
 *
 * Prints "ANAGRAM" or "NOT_ANAGRAM". If either argument is missing,
 * prints "USAGE". If either argument exceeds MAX_LEN bytes, prints
 * "TOO_LONG".
 */
#include <stdio.h>
#include <string.h>

#define MAX_LEN 1024

static char to_lower_ascii(char c) {
    if (c >= 'A' && c <= 'Z') {
        return (char)(c - 'A' + 'a');
    }
    return c;
}

static void count_bytes(const char *s, int counts[256]) {
    for (size_t i = 0; s[i] != '\0'; i++) {
        if (s[i] == ' ') {
            continue;
        }
        unsigned char c = (unsigned char)to_lower_ascii(s[i]);
        counts[c]++;
    }
}

static int lengths_ok(const char *a, const char *b) {
    return strlen(a) <= MAX_LEN && strlen(b) <= MAX_LEN;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("USAGE\n");
        return 0;
    }

    if (!lengths_ok(argv[1], argv[2])) {
        printf("TOO_LONG\n");
        return 0;
    }

    int counts_a[256] = {0};
    int counts_b[256] = {0};

    count_bytes(argv[1], counts_a);
    count_bytes(argv[2], counts_b);

    int is_anagram = 1;
    for (int i = 0; i < 256; i++) {
        if (counts_a[i] != counts_b[i]) {
            is_anagram = 0;
            break;
        }
    }

    printf("%s\n", is_anagram ? "ANAGRAM" : "NOT_ANAGRAM");
    return 0;
}
