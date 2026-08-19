/*
 * r16_siphash.c
 *
 * REAL CODE, not written for this experiment. The siphash() function
 * below is copied verbatim from the official SipHash reference
 * implementation (https://github.com/veorq/SipHash, file siphash.c,
 * CC0 1.0 Universal / public domain, by Jean-Philippe Aumasson and
 * Daniel J. Bernstein, the designers of SipHash). This is
 * SipHash-2-4 (the default cROUNDS=2/dROUNDS=4 configuration). See
 * ../corpus_real/PROVENIENZA.md for exact provenance.
 *
 * The only addition (clearly marked below) is a minimal main() that
 * takes a 16-byte key given as 32 hex characters (argv[1]) and a
 * message (argv[2]), computes the 8-byte SipHash digest, and prints
 * it as lowercase hex, so the library can be exercised as a
 * standalone CLI program. There is no randomness: both key and
 * message come entirely from argv.
 *
 * Usage: r16_siphash <32-hex-char-key> <message>
 * Prints the 8-byte SipHash-2-4 digest in lowercase hex, or "USAGE"
 * if fewer than two arguments were given, or "BAD_KEY" if the key is
 * not exactly 32 hex characters.
 */
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <stddef.h>
#include <stdint.h>

/* ------------------------------------------------------------------ */
/* BEGIN verbatim third-party code: siphash.c (SipHash reference,    */
/* CC0 / public domain)                                                */
/* ------------------------------------------------------------------ */

/* default: SipHash-2-4 */
#ifndef cROUNDS
#define cROUNDS 2
#endif
#ifndef dROUNDS
#define dROUNDS 4
#endif

#define ROTL(x, b) (uint64_t)(((x) << (b)) | ((x) >> (64 - (b))))

#define U32TO8_LE(p, v)                                                        \
    (p)[0] = (uint8_t)((v));                                                   \
    (p)[1] = (uint8_t)((v) >> 8);                                              \
    (p)[2] = (uint8_t)((v) >> 16);                                             \
    (p)[3] = (uint8_t)((v) >> 24);

#define U64TO8_LE(p, v)                                                        \
    U32TO8_LE((p), (uint32_t)((v)));                                           \
    U32TO8_LE((p) + 4, (uint32_t)((v) >> 32));

#define U8TO64_LE(p)                                                           \
    (((uint64_t)((p)[0])) | ((uint64_t)((p)[1]) << 8) |                        \
     ((uint64_t)((p)[2]) << 16) | ((uint64_t)((p)[3]) << 24) |                 \
     ((uint64_t)((p)[4]) << 32) | ((uint64_t)((p)[5]) << 40) |                 \
     ((uint64_t)((p)[6]) << 48) | ((uint64_t)((p)[7]) << 56))

#define SIPROUND                                                               \
    do {                                                                       \
        v0 += v1;                                                              \
        v1 = ROTL(v1, 13);                                                     \
        v1 ^= v0;                                                              \
        v0 = ROTL(v0, 32);                                                     \
        v2 += v3;                                                              \
        v3 = ROTL(v3, 16);                                                     \
        v3 ^= v2;                                                              \
        v0 += v3;                                                              \
        v3 = ROTL(v3, 21);                                                     \
        v3 ^= v0;                                                              \
        v2 += v1;                                                              \
        v1 = ROTL(v1, 17);                                                     \
        v1 ^= v2;                                                              \
        v2 = ROTL(v2, 32);                                                     \
    } while (0)

/*
    Computes a SipHash value
    *in: pointer to input data (read-only)
    inlen: input data length in bytes (any size_t value)
    *k: pointer to the key data (read-only), must be 16 bytes
    *out: pointer to output data (write-only), outlen bytes must be allocated
    outlen: length of the output in bytes, must be 8 or 16
*/
int siphash(const void *in, const size_t inlen, const void *k, uint8_t *out,
            const size_t outlen) {

    const unsigned char *ni = (const unsigned char *)in;
    const unsigned char *kk = (const unsigned char *)k;

    assert((outlen == 8) || (outlen == 16));
    uint64_t v0 = UINT64_C(0x736f6d6570736575);
    uint64_t v1 = UINT64_C(0x646f72616e646f6d);
    uint64_t v2 = UINT64_C(0x6c7967656e657261);
    uint64_t v3 = UINT64_C(0x7465646279746573);
    uint64_t k0 = U8TO64_LE(kk);
    uint64_t k1 = U8TO64_LE(kk + 8);
    uint64_t m;
    int i;
    const unsigned char *end = ni + inlen - (inlen % sizeof(uint64_t));
    const int left = inlen & 7;
    uint64_t b = ((uint64_t)inlen) << 56;
    v3 ^= k1;
    v2 ^= k0;
    v1 ^= k1;
    v0 ^= k0;

    if (outlen == 16)
        v1 ^= 0xee;

    for (; ni != end; ni += 8) {
        m = U8TO64_LE(ni);
        v3 ^= m;

        for (i = 0; i < cROUNDS; ++i)
            SIPROUND;

        v0 ^= m;
    }

    switch (left) {
    case 7:
        b |= ((uint64_t)ni[6]) << 48;
        /* FALLTHRU */
    case 6:
        b |= ((uint64_t)ni[5]) << 40;
        /* FALLTHRU */
    case 5:
        b |= ((uint64_t)ni[4]) << 32;
        /* FALLTHRU */
    case 4:
        b |= ((uint64_t)ni[3]) << 24;
        /* FALLTHRU */
    case 3:
        b |= ((uint64_t)ni[2]) << 16;
        /* FALLTHRU */
    case 2:
        b |= ((uint64_t)ni[1]) << 8;
        /* FALLTHRU */
    case 1:
        b |= ((uint64_t)ni[0]);
        break;
    case 0:
        break;
    }

    v3 ^= b;

    for (i = 0; i < cROUNDS; ++i)
        SIPROUND;

    v0 ^= b;

    if (outlen == 16)
        v2 ^= 0xee;
    else
        v2 ^= 0xff;

    for (i = 0; i < dROUNDS; ++i)
        SIPROUND;

    b = v0 ^ v1 ^ v2 ^ v3;
    U64TO8_LE(out, b);

    if (outlen == 8)
        return 0;

    v1 ^= 0xdd;

    for (i = 0; i < dROUNDS; ++i)
        SIPROUND;

    b = v0 ^ v1 ^ v2 ^ v3;
    U64TO8_LE(out + 8, b);

    return 0;
}

/* ------------------------------------------------------------------ */
/* END verbatim third-party code.                                    */
/* BEGIN our addition: minimal CLI wrapper (not part of upstream).   */
/* ------------------------------------------------------------------ */

static int hex_nibble(char c)
{
	if (c >= '0' && c <= '9') return c - '0';
	if (c >= 'a' && c <= 'f') return c - 'a' + 10;
	if (c >= 'A' && c <= 'F') return c - 'A' + 10;
	return -1;
}

int main(int argc, char **argv)
{
	if (argc < 3) {
		printf("USAGE\n");
		return 0;
	}

	const char *hexkey = argv[1];
	const char *message = argv[2];

	if (strlen(hexkey) != 32) {
		printf("BAD_KEY\n");
		return 0;
	}

	uint8_t key[16];
	for (int i = 0; i < 16; i++) {
		int hi = hex_nibble(hexkey[2 * i]);
		int lo = hex_nibble(hexkey[2 * i + 1]);
		if (hi < 0 || lo < 0) {
			printf("BAD_KEY\n");
			return 0;
		}
		key[i] = (uint8_t)((hi << 4) | lo);
	}

	uint8_t digest[8];
	siphash(message, strlen(message), key, digest, sizeof(digest));

	for (int i = 0; i < 8; i++) {
		printf("%02x", digest[i]);
	}
	printf("\n");

	return 0;
}
