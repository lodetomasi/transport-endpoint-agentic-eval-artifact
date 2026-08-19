/*
 * r05_arcfour.c
 *
 * REAL CODE, not written for this experiment. The arcfour_key_setup()
 * and arcfour_generate_stream() functions below are copied verbatim
 * from Brad Conte's "crypto-algorithms" repository
 * (https://github.com/B-Con/crypto-algorithms, files
 * arcfour.c/arcfour.h, released into the public domain per the
 * repository README). ARCFOUR is the unencumbered-name variant of
 * the RC4 stream cipher. See ../corpus_real/PROVENIENZA.md for exact
 * provenance.
 *
 * The only addition (clearly marked below) is a minimal main() that
 * takes a key (argv[1]) and a plaintext (argv[2]), keys the cipher,
 * encrypts the plaintext, and prints the resulting keystream-XORed
 * ciphertext as lowercase hex (the raw bytes may not be printable).
 * There is no randomness: the "key" is supplied entirely by argv,
 * exactly like upstream's own test harness does.
 *
 * Usage: r05_arcfour <key> <plaintext>
 * Prints ciphertext in lowercase hex, or "USAGE" if fewer than two
 * arguments were given, or "EMPTY_KEY" if <key> is the empty string.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* BEGIN verbatim third-party code: arcfour.h (Brad Conte,            */
/* crypto-algorithms, public domain)                                  */
/* ------------------------------------------------------------------ */

typedef unsigned char BYTE;             /* 8-bit byte */

void arcfour_key_setup(BYTE state[], const BYTE key[], int len);
void arcfour_generate_stream(BYTE state[], BYTE out[], size_t len);

/* ------------------------------------------------------------------ */
/* END verbatim third-party header content.                          */
/* BEGIN verbatim third-party code: arcfour.c (Brad Conte,            */
/* crypto-algorithms, public domain)                                  */
/* ------------------------------------------------------------------ */

void arcfour_key_setup(BYTE state[], const BYTE key[], int len)
{
	int i, j;
	BYTE t;

	for (i = 0; i < 256; ++i)
		state[i] = i;
	for (i = 0, j = 0; i < 256; ++i) {
		j = (j + state[i] + key[i % len]) % 256;
		t = state[i];
		state[i] = state[j];
		state[j] = t;
	}
}

/* This does not hold state between calls. It always generates the
   stream starting from the first output byte. */
void arcfour_generate_stream(BYTE state[], BYTE out[], size_t len)
{
	int i, j;
	size_t idx;
	BYTE t;

	for (idx = 0, i = 0, j = 0; idx < len; ++idx)  {
		i = (i + 1) % 256;
		j = (j + state[i]) % 256;
		t = state[i];
		state[i] = state[j];
		state[j] = t;
		out[idx] = state[(state[i] + state[j]) % 256];
	}
}

/* ------------------------------------------------------------------ */
/* END verbatim third-party code.                                    */
/* BEGIN our addition: minimal CLI wrapper (not part of upstream).   */
/* ------------------------------------------------------------------ */

#define MAX_TEXT 512

int main(int argc, char **argv)
{
	if (argc < 3) {
		printf("USAGE\n");
		return 0;
	}

	const char *key = argv[1];
	const char *plaintext = argv[2];
	size_t key_len = strlen(key);
	size_t text_len = strlen(plaintext);

	if (key_len == 0) {
		printf("EMPTY_KEY\n");
		return 0;
	}

	if (text_len > MAX_TEXT) {
		text_len = MAX_TEXT;
	}

	BYTE state[256];
	static BYTE keystream[MAX_TEXT];

	arcfour_key_setup(state, (const BYTE *)key, (int)key_len);
	arcfour_generate_stream(state, keystream, text_len);

	for (size_t i = 0; i < text_len; i++) {
		BYTE cipher_byte = (BYTE)plaintext[i] ^ keystream[i];
		printf("%02x", cipher_byte);
	}
	printf("\n");

	return 0;
}
