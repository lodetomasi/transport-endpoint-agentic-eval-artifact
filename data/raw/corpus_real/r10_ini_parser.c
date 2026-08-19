/*
 * r10_ini_parser.c
 *
 * REAL CODE, not written for this experiment. Everything between the
 * BEGIN/END verbatim markers below is copied, mechanically
 * concatenated from two upstream files (ini.h then ini.c), from Ben
 * Hoyt's "inih" repository (https://github.com/benhoyt/inih, New BSD
 * / BSD-3-Clause License, Copyright (C) 2009-2025 Ben Hoyt). All
 * INI_* configuration macros are left at their upstream default
 * values (no behavior was changed). See ../corpus_real/PROVENIENZA.md
 * for exact provenance.
 *
 * The only addition (clearly marked below) is a minimal main() that
 * reads an INI document from stdin, calls ini_parse_string() with a
 * handler that prints each "section.name=value" pair it receives (in
 * the order the parser calls the handler), and finally prints either
 * "OK" or "ERROR_LINE:<n>" depending on ini_parse_string()'s return
 * value, so the library can be exercised as a standalone CLI program.
 *
 * Usage: r10_ini_parser < file.ini
 */
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <assert.h>

/* ------------------------------------------------------------------ */
/* BEGIN verbatim third-party code: ini.h (inih, BSD-3-Clause)        */
/* ------------------------------------------------------------------ */

#ifndef INI_HANDLER_LINENO
#define INI_HANDLER_LINENO 0
#endif

#if INI_HANDLER_LINENO
typedef int (*ini_handler)(void* user, const char* section,
                           const char* name, const char* value,
                           int lineno);
#else
typedef int (*ini_handler)(void* user, const char* section,
                           const char* name, const char* value);
#endif

typedef char* (*ini_reader)(char* str, int num, void* stream);

int ini_parse(const char* filename, ini_handler handler, void* user);
int ini_parse_file(FILE* file, ini_handler handler, void* user);
int ini_parse_stream(ini_reader reader, void* stream, ini_handler handler,
                     void* user);
int ini_parse_string(const char* string, ini_handler handler, void* user);
int ini_parse_string_length(const char* string, size_t length, ini_handler handler, void* user);

#ifndef INI_ALLOW_MULTILINE
#define INI_ALLOW_MULTILINE 1
#endif

#ifndef INI_ALLOW_BOM
#define INI_ALLOW_BOM 1
#endif

#ifndef INI_START_COMMENT_PREFIXES
#define INI_START_COMMENT_PREFIXES ";#"
#endif

#ifndef INI_ALLOW_INLINE_COMMENTS
#define INI_ALLOW_INLINE_COMMENTS 1
#endif
#ifndef INI_INLINE_COMMENT_PREFIXES
#define INI_INLINE_COMMENT_PREFIXES ";"
#endif

#ifndef INI_USE_STACK
#define INI_USE_STACK 1
#endif

#ifndef INI_MAX_LINE
#define INI_MAX_LINE 200
#endif

#ifndef INI_ALLOW_REALLOC
#define INI_ALLOW_REALLOC 0
#endif

#ifndef INI_INITIAL_ALLOC
#define INI_INITIAL_ALLOC 200
#endif

#ifndef INI_STOP_ON_FIRST_ERROR
#define INI_STOP_ON_FIRST_ERROR 0
#endif

#ifndef INI_CALL_HANDLER_ON_NEW_SECTION
#define INI_CALL_HANDLER_ON_NEW_SECTION 0
#endif

#ifndef INI_ALLOW_NO_VALUE
#define INI_ALLOW_NO_VALUE 0
#endif

#ifndef INI_CUSTOM_ALLOCATOR
#define INI_CUSTOM_ALLOCATOR 0
#endif

/* ------------------------------------------------------------------ */
/* END verbatim third-party header content.                          */
/* BEGIN verbatim third-party code: ini.c (inih, BSD-3-Clause)        */
/* ------------------------------------------------------------------ */

#if !INI_USE_STACK
#if INI_CUSTOM_ALLOCATOR
void* ini_malloc(size_t size);
void ini_free(void* ptr);
void* ini_realloc(void* ptr, size_t size);
#else
#define ini_malloc malloc
#define ini_free free
#define ini_realloc realloc
#endif
#endif

#define MAX_SECTION 50
#define MAX_NAME 50

typedef struct {
    const char* ptr;
    size_t num_left;
} ini_parse_string_ctx;

static char* ini_rstrip(char* s, char* end)
{
    while (end > s && isspace((unsigned char)(*--end)))
        *end = '\0';
    return s;
}

static char* ini_lskip(const char* s)
{
    while (*s && isspace((unsigned char)(*s)))
        s++;
    return (char*)s;
}

static char* ini_find_chars_or_comment(const char* s, const char* chars)
{
#if INI_ALLOW_INLINE_COMMENTS
    int was_space = 0;
    while (*s && (!chars || !strchr(chars, *s)) &&
           !(was_space && strchr(INI_INLINE_COMMENT_PREFIXES, *s))) {
        was_space = isspace((unsigned char)(*s));
        s++;
    }
#else
    while (*s && (!chars || !strchr(chars, *s))) {
        s++;
    }
#endif
    return (char*)s;
}

static char* ini_strncpy0(char* dest, const char* src, size_t size)
{
    size_t i;
    for (i = 0; i < size - 1 && src[i]; i++)
        dest[i] = src[i];
    dest[i] = '\0';
    return dest;
}

int ini_parse_stream(ini_reader reader, void* stream, ini_handler handler,
                     void* user)
{
#if INI_USE_STACK
    char line[INI_MAX_LINE];
    size_t max_line = INI_MAX_LINE;
#else
    char* line;
    size_t max_line = INI_INITIAL_ALLOC;
#endif
#if INI_ALLOW_REALLOC && !INI_USE_STACK
    char* new_line;
#endif
    char section[MAX_SECTION] = "";
#if INI_ALLOW_MULTILINE
    char prev_name[MAX_NAME] = "";
#endif

    size_t offset;
    char* start;
    char* end;
    char* name;
    char* value;
    int lineno = 0;
    int error = 0;
    char abyss[16];
    size_t abyss_len;

    assert(reader != NULL);
    assert(stream != NULL);
    assert(handler != NULL);

#if !INI_USE_STACK
    line = (char*)ini_malloc(INI_INITIAL_ALLOC);
    if (!line) {
        return -2;
    }
#endif

#if INI_HANDLER_LINENO
#define HANDLER(u, s, n, v) handler(u, s, n, v, lineno)
#else
#define HANDLER(u, s, n, v) handler(u, s, n, v)
#endif

    while (reader(line, (int)max_line, stream) != NULL) {
        offset = strlen(line);

#if INI_ALLOW_REALLOC && !INI_USE_STACK
        while (max_line < INI_MAX_LINE &&
               offset == max_line - 1 && line[offset - 1] != '\n') {
            max_line *= 2;
            if (max_line > INI_MAX_LINE)
                max_line = INI_MAX_LINE;
            new_line = ini_realloc(line, max_line);
            if (!new_line) {
                ini_free(line);
                return -2;
            }
            line = new_line;
            if (reader(line + offset, (int)(max_line - offset), stream) == NULL)
                break;
            offset += strlen(line + offset);
        }
#endif

        lineno++;

        if (offset == max_line - 1 && line[offset - 1] != '\n') {
            while (reader(abyss, sizeof(abyss), stream) != NULL) {
                if (!error)
                    error = lineno;
                abyss_len = strlen(abyss);
                if (abyss_len > 0 && abyss[abyss_len - 1] == '\n')
                    break;
            }
        }

        start = line;
#if INI_ALLOW_BOM
        if (lineno == 1 && (unsigned char)start[0] == 0xEF &&
                           (unsigned char)start[1] == 0xBB &&
                           (unsigned char)start[2] == 0xBF) {
            start += 3;
        }
#endif
        start = ini_rstrip(ini_lskip(start), line + offset);

        if (strchr(INI_START_COMMENT_PREFIXES, *start)) {
            /* Start-of-line comment */
        }
#if INI_ALLOW_MULTILINE
        else if (*prev_name && *start && start > line) {
#if INI_ALLOW_INLINE_COMMENTS
            end = ini_find_chars_or_comment(start, NULL);
            *end = '\0';
            ini_rstrip(start, end);
#endif
            if (!HANDLER(user, section, prev_name, start) && !error)
                error = lineno;
        }
#endif
        else if (*start == '[') {
            end = ini_find_chars_or_comment(start + 1, "]");
            if (*end == ']') {
                *end = '\0';
                ini_strncpy0(section, start + 1, sizeof(section));
#if INI_ALLOW_MULTILINE
                *prev_name = '\0';
#endif
#if INI_CALL_HANDLER_ON_NEW_SECTION
                if (!HANDLER(user, section, NULL, NULL) && !error)
                    error = lineno;
#endif
            }
            else if (!error) {
                error = lineno;
            }
        }
        else if (*start) {
            end = ini_find_chars_or_comment(start, "=:");
            if (*end == '=' || *end == ':') {
                *end = '\0';
                name = ini_rstrip(start, end);
                value = end + 1;
#if INI_ALLOW_INLINE_COMMENTS
                end = ini_find_chars_or_comment(value, NULL);
                *end = '\0';
#endif
                value = ini_lskip(value);
                ini_rstrip(value, end);

#if INI_ALLOW_MULTILINE
                ini_strncpy0(prev_name, name, sizeof(prev_name));
#endif
                if (!HANDLER(user, section, name, value) && !error)
                    error = lineno;
            }
            else {
#if INI_ALLOW_NO_VALUE
                *end = '\0';
                name = ini_rstrip(start, end);
                if (!HANDLER(user, section, name, NULL) && !error)
                    error = lineno;
#else
                if (!error)
                    error = lineno;
#endif
            }
        }

#if INI_STOP_ON_FIRST_ERROR
        if (error)
            break;
#endif
    }

#if !INI_USE_STACK
    ini_free(line);
#endif

    return error;
}

int ini_parse_file(FILE* file, ini_handler handler, void* user)
{
    return ini_parse_stream((ini_reader)fgets, file, handler, user);
}

int ini_parse(const char* filename, ini_handler handler, void* user)
{
    FILE* file;
    int error;

    file = fopen(filename, "r");
    if (!file)
        return -1;
    error = ini_parse_file(file, handler, user);
    fclose(file);
    return error;
}

static char* ini_reader_string(char* str, int num, void* stream) {
    ini_parse_string_ctx* ctx = (ini_parse_string_ctx*)stream;
    const char* ctx_ptr = ctx->ptr;
    size_t ctx_num_left = ctx->num_left;
    char* strp = str;
    char c;

    if (ctx_num_left == 0 || num < 2)
        return NULL;

    while (num > 1 && ctx_num_left != 0) {
        c = *ctx_ptr++;
        ctx_num_left--;
        *strp++ = c;
        if (c == '\n')
            break;
        num--;
    }

    *strp = '\0';
    ctx->ptr = ctx_ptr;
    ctx->num_left = ctx_num_left;
    return str;
}

int ini_parse_string(const char* string, ini_handler handler, void* user) {
    return ini_parse_string_length(string, strlen(string), handler, user);
}

int ini_parse_string_length(const char* string, size_t length,
                            ini_handler handler, void* user) {
    ini_parse_string_ctx ctx;

    ctx.ptr = string;
    ctx.num_left = length;
    return ini_parse_stream((ini_reader)ini_reader_string, &ctx, handler,
                            user);
}

/* ------------------------------------------------------------------ */
/* END verbatim third-party code.                                    */
/* BEGIN our addition: minimal CLI wrapper (not part of upstream).   */
/* ------------------------------------------------------------------ */

#define MAX_INPUT 8192

static int print_pair(void *user, const char *section, const char *name,
                       const char *value)
{
	(void)user;
	if (section[0] == '\0') {
		printf("GLOBAL.%s=%s\n", name, value);
	} else {
		printf("%s.%s=%s\n", section, name, value);
	}
	return 1; /* nonzero: no error */
}

int main(void)
{
	static char input[MAX_INPUT];
	size_t len = fread(input, 1, MAX_INPUT - 1, stdin);
	input[len] = '\0';

	int result = ini_parse_string(input, print_pair, NULL);

	if (result == 0) {
		printf("OK\n");
	} else {
		printf("ERROR_LINE:%d\n", result);
	}

	return 0;
}
