/*
 * prog12_csv_tokenizer.c
 *
 * Tokenizes a single CSV line read from stdin into fields, honoring
 * RFC4180-style double-quoted fields (commas inside quotes are not
 * delimiters, "" inside a quoted field means a literal quote).
 *
 * Prints one line per field as "<index>:<value>". If stdin has no
 * line at all, prints "NO_INPUT".
 */
#include <stdio.h>
#include <string.h>

#define MAX_LINE 2048
#define MAX_FIELD 512
#define MAX_FIELDS 64

int main(void) {
    static char line[MAX_LINE];

    if (!fgets(line, sizeof(line), stdin)) {
        printf("NO_INPUT\n");
        return 0;
    }

    size_t len = strlen(line);
    while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) {
        line[len - 1] = '\0';
        len--;
    }

    static char fields[MAX_FIELDS][MAX_FIELD];
    int field_count = 0;
    int field_pos = 0;
    int in_quotes = 0;
    size_t i = 0;

    while (i <= len) {
        char c = (i < len) ? line[i] : '\0';

        if (in_quotes) {
            if (c == '"') {
                if (i + 1 < len && line[i + 1] == '"') {
                    if (field_pos < MAX_FIELD - 1) {
                        fields[field_count][field_pos++] = '"';
                    }
                    i++; /* skip the escaped quote pair */
                } else {
                    in_quotes = 0;
                }
            } else if (c == '\0') {
                /* unterminated quote at end of line: treat as closed */
                in_quotes = 0;
            } else {
                if (field_pos < MAX_FIELD - 1) {
                    fields[field_count][field_pos++] = c;
                }
            }
        } else {
            if (c == '"' && field_pos == 0) {
                in_quotes = 1;
            } else if (c == ',' || c == '\0') {
                fields[field_count][field_pos] = '\0';
                if (field_count < MAX_FIELDS - 1) {
                    field_count++;
                }
                field_pos = 0;
            } else {
                if (field_pos < MAX_FIELD - 1) {
                    fields[field_count][field_pos++] = c;
                }
            }
        }
        i++;
    }

    for (int f = 0; f < field_count; f++) {
        printf("%d:%s\n", f, fields[f]);
    }

    return 0;
}
