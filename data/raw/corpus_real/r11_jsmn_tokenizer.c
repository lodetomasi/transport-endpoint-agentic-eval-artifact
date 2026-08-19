/*
 * r11_jsmn_tokenizer.c
 *
 * REAL CODE, not written for this experiment. Everything between the
 * BEGIN/END verbatim markers below is copied verbatim from Serge
 * Zaitsev's "jsmn" minimalistic JSON tokenizer
 * (https://github.com/zserge/jsmn, file jsmn.h, MIT License,
 * Copyright (c) 2010 Serge Zaitsev). jsmn.h is designed upstream to
 * be #include'd directly into a single translation unit (its
 * implementation is guarded by `#ifndef JSMN_HEADER`, which we do not
 * define), so pasting its content here instead of using a separate
 * header file required no logic change.
 *
 * ADAPTATION (documented, not silent): jsmn.h contains two upstream
 * compile-time options we do not enable and therefore omitted here
 * to keep the file shorter: the `#ifdef JSMN_PARENT_LINKS` branches
 * (an optional `parent` field/back-links, off by default) and the
 * `#ifdef JSMN_STRICT` branches (a stricter grammar mode, also off by
 * default). Both are dead code paths under jsmn's own default build
 * (neither macro is defined), so omitting them changes nothing about
 * this program's behavior; we did not omit any code that upstream's
 * own default configuration would execute. See
 * ../corpus_real/PROVENIENZA.md for exact provenance.
 *
 * The only addition (clearly marked below) is a minimal main() that
 * reads a JSON document from stdin, tokenizes it with a fixed-size
 * token array, and prints one line per token as
 * "<index>:<TYPE>:<text>", or "PARSE_ERROR:<code>" if tokenizing
 * failed (code is jsmn's own JSMN_ERROR_* constant), so the library
 * can be exercised as a standalone CLI program.
 *
 * Usage: r11_jsmn_tokenizer < file.json
 */
#include <stdio.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* BEGIN verbatim third-party code: jsmn.h (jsmn, MIT)                */
/* ------------------------------------------------------------------ */

#include <stddef.h>

typedef enum {
  JSMN_UNDEFINED = 0,
  JSMN_OBJECT = 1 << 0,
  JSMN_ARRAY = 1 << 1,
  JSMN_STRING = 1 << 2,
  JSMN_PRIMITIVE = 1 << 3
} jsmntype_t;

enum jsmnerr {
  /* Not enough tokens were provided */
  JSMN_ERROR_NOMEM = -1,
  /* Invalid character inside JSON string */
  JSMN_ERROR_INVAL = -2,
  /* The string is not a full JSON packet, more bytes expected */
  JSMN_ERROR_PART = -3
};

typedef struct jsmntok {
  jsmntype_t type;
  int start;
  int end;
  int size;
} jsmntok_t;

typedef struct jsmn_parser {
  unsigned int pos;     /* offset in the JSON string */
  unsigned int toknext; /* next token to allocate */
  int toksuper;         /* superior token node, e.g. parent object or array */
} jsmn_parser;

extern void jsmn_init(jsmn_parser *parser);
extern int jsmn_parse(jsmn_parser *parser, const char *js, const size_t len,
                        jsmntok_t *tokens, const unsigned int num_tokens);

static jsmntok_t *jsmn_alloc_token(jsmn_parser *parser, jsmntok_t *tokens,
                                   const size_t num_tokens) {
  jsmntok_t *tok;
  if (parser->toknext >= num_tokens) {
    return NULL;
  }
  tok = &tokens[parser->toknext++];
  tok->start = tok->end = -1;
  tok->size = 0;
  return tok;
}

static void jsmn_fill_token(jsmntok_t *token, const jsmntype_t type,
                            const int start, const int end) {
  token->type = type;
  token->start = start;
  token->end = end;
  token->size = 0;
}

static int jsmn_parse_primitive(jsmn_parser *parser, const char *js,
                                const size_t len, jsmntok_t *tokens,
                                const size_t num_tokens) {
  jsmntok_t *token;
  int start;

  start = parser->pos;

  for (; parser->pos < len && js[parser->pos] != '\0'; parser->pos++) {
    switch (js[parser->pos]) {
    /* In strict mode primitive must be followed by "," or "}" or "]" */
    case ':':
    case '\t':
    case '\r':
    case '\n':
    case ' ':
    case ',':
    case ']':
    case '}':
      goto found;
    default:
                   /* to quiet a warning from gcc*/
      break;
    }
    if (js[parser->pos] < 32 || js[parser->pos] >= 127) {
      parser->pos = start;
      return JSMN_ERROR_INVAL;
    }
  }

found:
  if (tokens == NULL) {
    parser->pos--;
    return 0;
  }
  token = jsmn_alloc_token(parser, tokens, num_tokens);
  if (token == NULL) {
    parser->pos = start;
    return JSMN_ERROR_NOMEM;
  }
  jsmn_fill_token(token, JSMN_PRIMITIVE, start, parser->pos);
  parser->pos--;
  return 0;
}

static int jsmn_parse_string(jsmn_parser *parser, const char *js,
                             const size_t len, jsmntok_t *tokens,
                             const size_t num_tokens) {
  jsmntok_t *token;

  int start = parser->pos;

  /* Skip starting quote */
  parser->pos++;

  for (; parser->pos < len && js[parser->pos] != '\0'; parser->pos++) {
    char c = js[parser->pos];

    /* Quote: end of string */
    if (c == '\"') {
      if (tokens == NULL) {
        return 0;
      }
      token = jsmn_alloc_token(parser, tokens, num_tokens);
      if (token == NULL) {
        parser->pos = start;
        return JSMN_ERROR_NOMEM;
      }
      jsmn_fill_token(token, JSMN_STRING, start + 1, parser->pos);
      return 0;
    }

    /* Backslash: Quoted symbol expected */
    if (c == '\\' && parser->pos + 1 < len) {
      int i;
      parser->pos++;
      switch (js[parser->pos]) {
      /* Allowed escaped symbols */
      case '\"':
      case '/':
      case '\\':
      case 'b':
      case 'f':
      case 'r':
      case 'n':
      case 't':
        break;
      /* Allows escaped symbol \uXXXX */
      case 'u':
        parser->pos++;
        for (i = 0; i < 4 && parser->pos < len && js[parser->pos] != '\0';
             i++) {
          /* If it isn't a hex character we have an error */
          if (!((js[parser->pos] >= 48 && js[parser->pos] <= 57) ||   /* 0-9 */
                (js[parser->pos] >= 65 && js[parser->pos] <= 70) ||   /* A-F */
                (js[parser->pos] >= 97 && js[parser->pos] <= 102))) { /* a-f */
            parser->pos = start;
            return JSMN_ERROR_INVAL;
          }
          parser->pos++;
        }
        parser->pos--;
        break;
      /* Unexpected symbol */
      default:
        parser->pos = start;
        return JSMN_ERROR_INVAL;
      }
    }
  }
  parser->pos = start;
  return JSMN_ERROR_PART;
}

int jsmn_parse(jsmn_parser *parser, const char *js, const size_t len,
                        jsmntok_t *tokens, const unsigned int num_tokens) {
  int r;
  int i;
  jsmntok_t *token;
  int count = parser->toknext;

  for (; parser->pos < len && js[parser->pos] != '\0'; parser->pos++) {
    char c;
    jsmntype_t type;

    c = js[parser->pos];
    switch (c) {
    case '{':
    case '[':
      count++;
      if (tokens == NULL) {
        break;
      }
      token = jsmn_alloc_token(parser, tokens, num_tokens);
      if (token == NULL) {
        return JSMN_ERROR_NOMEM;
      }
      if (parser->toksuper != -1) {
        jsmntok_t *t = &tokens[parser->toksuper];
        t->size++;
      }
      token->type = (c == '{' ? JSMN_OBJECT : JSMN_ARRAY);
      token->start = parser->pos;
      parser->toksuper = parser->toknext - 1;
      break;
    case '}':
    case ']':
      if (tokens == NULL) {
        break;
      }
      type = (c == '}' ? JSMN_OBJECT : JSMN_ARRAY);
      for (i = parser->toknext - 1; i >= 0; i--) {
        token = &tokens[i];
        if (token->start != -1 && token->end == -1) {
          if (token->type != type) {
            return JSMN_ERROR_INVAL;
          }
          parser->toksuper = -1;
          token->end = parser->pos + 1;
          break;
        }
      }
      /* Error if unmatched closing bracket */
      if (i == -1) {
        return JSMN_ERROR_INVAL;
      }
      for (; i >= 0; i--) {
        token = &tokens[i];
        if (token->start != -1 && token->end == -1) {
          parser->toksuper = i;
          break;
        }
      }
      break;
    case '\"':
      r = jsmn_parse_string(parser, js, len, tokens, num_tokens);
      if (r < 0) {
        return r;
      }
      count++;
      if (parser->toksuper != -1 && tokens != NULL) {
        tokens[parser->toksuper].size++;
      }
      break;
    case '\t':
    case '\r':
    case '\n':
    case ' ':
      break;
    case ':':
      parser->toksuper = parser->toknext - 1;
      break;
    case ',':
      if (tokens != NULL && parser->toksuper != -1 &&
          tokens[parser->toksuper].type != JSMN_ARRAY &&
          tokens[parser->toksuper].type != JSMN_OBJECT) {
        for (i = parser->toknext - 1; i >= 0; i--) {
          if (tokens[i].type == JSMN_ARRAY || tokens[i].type == JSMN_OBJECT) {
            if (tokens[i].start != -1 && tokens[i].end == -1) {
              parser->toksuper = i;
              break;
            }
          }
        }
      }
      break;
    /* In non-strict mode every unquoted value is a primitive */
    default:
      r = jsmn_parse_primitive(parser, js, len, tokens, num_tokens);
      if (r < 0) {
        return r;
      }
      count++;
      if (parser->toksuper != -1 && tokens != NULL) {
        tokens[parser->toksuper].size++;
      }
      break;
    }
  }

  if (tokens != NULL) {
    for (i = parser->toknext - 1; i >= 0; i--) {
      /* Unmatched opened object or array */
      if (tokens[i].start != -1 && tokens[i].end == -1) {
        return JSMN_ERROR_PART;
      }
    }
  }

  return count;
}

void jsmn_init(jsmn_parser *parser) {
  parser->pos = 0;
  parser->toknext = 0;
  parser->toksuper = -1;
}

/* ------------------------------------------------------------------ */
/* END verbatim third-party code.                                    */
/* BEGIN our addition: minimal CLI wrapper (not part of upstream).   */
/* ------------------------------------------------------------------ */

#define MAX_INPUT 4096
#define MAX_TOKENS 256

static const char *type_name(jsmntype_t t)
{
	switch (t) {
	case JSMN_OBJECT:    return "OBJECT";
	case JSMN_ARRAY:     return "ARRAY";
	case JSMN_STRING:    return "STRING";
	case JSMN_PRIMITIVE: return "PRIMITIVE";
	default:             return "UNDEFINED";
	}
}

int main(void)
{
	static char input[MAX_INPUT];
	size_t len = fread(input, 1, MAX_INPUT - 1, stdin);
	input[len] = '\0';

	jsmn_parser parser;
	static jsmntok_t tokens[MAX_TOKENS];

	jsmn_init(&parser);
	int r = jsmn_parse(&parser, input, len, tokens, MAX_TOKENS);

	if (r < 0) {
		printf("PARSE_ERROR:%d\n", r);
		return 0;
	}

	for (int i = 0; i < r; i++) {
		int tok_len = tokens[i].end - tokens[i].start;
		printf("%d:%s:%.*s\n", i, type_name(tokens[i].type), tok_len,
		       input + tokens[i].start);
	}

	return 0;
}
