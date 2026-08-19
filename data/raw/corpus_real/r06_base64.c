/*
 * r06_base64.c
 *
 * REAL CODE, not written for this experiment. b64_encode(),
 * b64_decode(), b64_decode_ex(), b64_buf_malloc() and
 * b64_buf_realloc() below are copied verbatim (mechanically
 * concatenated from four upstream files: b64.h, buffer.c, encode.c,
 * decode.c) from littlstar/b64.c (https://github.com/littlstar/b64.c,
 * MIT License, copyright (c) 2014 Little Star Media, Inc.). See
 * ../corpus_real/PROVENIENZA.md for exact provenance.
 *
 * The only addition (clearly marked below) is a minimal main() that
 * dispatches to b64_encode() or b64_decode() based on argv[1], so the
 * library can be exercised as a standalone CLI program.
 *
 * Usage: r06_base64 encode <text>
 *        r06_base64 decode <base64text>
 * Prints the encoded/decoded result, or "USAGE" if the arguments
 * don't match one of the two forms above, or "DECODE_ERROR" if
 * decoding failed (out of memory in upstream b64_decode_ex(), which
 * cannot happen for the small inputs used here, kept only because it
 * is upstream's own error path).
 */
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* BEGIN verbatim third-party code: b64.h (littlstar/b64.c, MIT)      */
/* ------------------------------------------------------------------ */

typedef struct b64_buffer {
    char * ptr;
    size_t bufc;
} b64_buffer_t;

#ifndef b64_malloc
#  define b64_malloc(ptr) malloc(ptr)
#endif
#ifndef b64_realloc
#  define b64_realloc(ptr, size) realloc(ptr, size)
#endif

#ifndef B64_BUFFER_SIZE
#  define B64_BUFFER_SIZE		(1024 * 64) /* 64K */
#endif

int b64_buf_malloc(b64_buffer_t * buffer);
int b64_buf_realloc(b64_buffer_t * buffer, size_t size);

static const char b64_table[] = {
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
  'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
  'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
  'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f',
  'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
  'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
  'w', 'x', 'y', 'z', '0', '1', '2', '3',
  '4', '5', '6', '7', '8', '9', '+', '/'
};

char * b64_encode (const unsigned char *, size_t);
unsigned char * b64_decode (const char *, size_t);
unsigned char * b64_decode_ex (const char *, size_t, size_t *);

/* ------------------------------------------------------------------ */
/* END verbatim third-party header content.                          */
/* BEGIN verbatim third-party code: buffer.c (littlstar/b64.c, MIT)   */
/* ------------------------------------------------------------------ */

int b64_buf_malloc(b64_buffer_t * buf)
{
	buf->ptr = b64_malloc(B64_BUFFER_SIZE);
	if(!buf->ptr) return -1;

	buf->bufc = 1;

	return 0;
}

int b64_buf_realloc(b64_buffer_t* buf, size_t size)
{
	if (size > buf->bufc * B64_BUFFER_SIZE)
	{
		while (size > buf->bufc * B64_BUFFER_SIZE) buf->bufc++;
		buf->ptr = b64_realloc(buf->ptr, B64_BUFFER_SIZE * buf->bufc);
		if (!buf->ptr) return -1;
	}

	return 0;
}

/* ------------------------------------------------------------------ */
/* END verbatim third-party code: buffer.c                           */
/* BEGIN verbatim third-party code: encode.c (littlstar/b64.c, MIT)   */
/* ------------------------------------------------------------------ */

char *
b64_encode (const unsigned char *src, size_t len) {
  int i = 0;
  int j = 0;
  b64_buffer_t encbuf;
  size_t size = 0;
  unsigned char buf[4];
  unsigned char tmp[3];

  if(b64_buf_malloc(&encbuf) == -1) { return NULL; }

  while (len--) {
    tmp[i++] = *(src++);

    if (3 == i) {
      buf[0] = (tmp[0] & 0xfc) >> 2;
      buf[1] = ((tmp[0] & 0x03) << 4) + ((tmp[1] & 0xf0) >> 4);
      buf[2] = ((tmp[1] & 0x0f) << 2) + ((tmp[2] & 0xc0) >> 6);
      buf[3] = tmp[2] & 0x3f;

      if (b64_buf_realloc(&encbuf, size + 4) == -1) return NULL;

      for (i = 0; i < 4; ++i) {
        encbuf.ptr[size++] = b64_table[buf[i]];
      }

      i = 0;
    }
  }

  if (i > 0) {
    for (j = i; j < 3; ++j) {
      tmp[j] = '\0';
    }

    buf[0] = (tmp[0] & 0xfc) >> 2;
    buf[1] = ((tmp[0] & 0x03) << 4) + ((tmp[1] & 0xf0) >> 4);
    buf[2] = ((tmp[1] & 0x0f) << 2) + ((tmp[2] & 0xc0) >> 6);
    buf[3] = tmp[2] & 0x3f;

    for (j = 0; (j < i + 1); ++j) {
      if (b64_buf_realloc(&encbuf, size + 1) == -1) return NULL;

      encbuf.ptr[size++] = b64_table[buf[j]];
    }

    while ((i++ < 3)) {
      if (b64_buf_realloc(&encbuf, size + 1) == -1) return NULL;

      encbuf.ptr[size++] = '=';
    }
  }

  if (b64_buf_realloc(&encbuf, size + 1) == -1) return NULL;
  encbuf.ptr[size] = '\0';

  return encbuf.ptr;
}

/* ------------------------------------------------------------------ */
/* END verbatim third-party code: encode.c                           */
/* BEGIN verbatim third-party code: decode.c (littlstar/b64.c, MIT)   */
/* ------------------------------------------------------------------ */

unsigned char *
b64_decode (const char *src, size_t len) {
  return b64_decode_ex(src, len, NULL);
}

unsigned char *
b64_decode_ex (const char *src, size_t len, size_t *decsize) {
  int i = 0;
  int j = 0;
  int l = 0;
  size_t size = 0;
  b64_buffer_t decbuf;
  unsigned char buf[3];
  unsigned char tmp[4];

  if (b64_buf_malloc(&decbuf) == -1) { return NULL; }

  while (len--) {
    if ('=' == src[j]) { break; }
    if (!(isalnum((unsigned char)src[j]) || '+' == src[j] || '/' == src[j])) { break; }

    tmp[i++] = src[j++];

    if (4 == i) {
      for (i = 0; i < 4; ++i) {
        for (l = 0; l < 64; ++l) {
          if (tmp[i] == b64_table[l]) {
            tmp[i] = l;
            break;
          }
        }
      }

      buf[0] = (tmp[0] << 2) + ((tmp[1] & 0x30) >> 4);
      buf[1] = ((tmp[1] & 0xf) << 4) + ((tmp[2] & 0x3c) >> 2);
      buf[2] = ((tmp[2] & 0x3) << 6) + tmp[3];

      if (b64_buf_realloc(&decbuf, size + 3) == -1)  return NULL;
      for (i = 0; i < 3; ++i) {
        ((unsigned char*)decbuf.ptr)[size++] = buf[i];
      }

      i = 0;
    }
  }

  if (i > 0) {
    for (j = i; j < 4; ++j) {
      tmp[j] = '\0';
    }

    for (j = 0; j < 4; ++j) {
        for (l = 0; l < 64; ++l) {
          if (tmp[j] == b64_table[l]) {
            tmp[j] = l;
            break;
          }
        }
    }

    buf[0] = (tmp[0] << 2) + ((tmp[1] & 0x30) >> 4);
    buf[1] = ((tmp[1] & 0xf) << 4) + ((tmp[2] & 0x3c) >> 2);
    buf[2] = ((tmp[2] & 0x3) << 6) + tmp[3];

    if (b64_buf_realloc(&decbuf, size + (i - 1)) == -1)  return NULL;
    for (j = 0; (j < i - 1); ++j) {
      ((unsigned char*)decbuf.ptr)[size++] = buf[j];
    }
  }

  if (b64_buf_realloc(&decbuf, size + 1) == -1)  return NULL;
  ((unsigned char*)decbuf.ptr)[size] = '\0';

  if (decsize != NULL) {
    *decsize = size;
  }

  return (unsigned char*) decbuf.ptr;
}

/* ------------------------------------------------------------------ */
/* END verbatim third-party code.                                    */
/* BEGIN our addition: minimal CLI wrapper (not part of upstream).   */
/* ------------------------------------------------------------------ */

int main(int argc, char **argv)
{
	if (argc < 3) {
		printf("USAGE\n");
		return 0;
	}

	if (strcmp(argv[1], "encode") == 0) {
		char *out = b64_encode((const unsigned char *)argv[2], strlen(argv[2]));
		if (!out) {
			printf("DECODE_ERROR\n");
			return 0;
		}
		printf("%s\n", out);
		free(out);
		return 0;
	}

	if (strcmp(argv[1], "decode") == 0) {
		size_t decoded_len = 0;
		unsigned char *out = b64_decode_ex(argv[2], strlen(argv[2]), &decoded_len);
		if (!out) {
			printf("DECODE_ERROR\n");
			return 0;
		}
		fwrite(out, 1, decoded_len, stdout);
		printf("\n");
		free(out);
		return 0;
	}

	printf("USAGE\n");
	return 0;
}
