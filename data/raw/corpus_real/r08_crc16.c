/*
 * r08_crc16.c
 *
 * REAL CODE, not written for this experiment. crc_16(),
 * update_crc_16() and init_crc16_tab() below are copied verbatim
 * from Lammert Bies's "libcrc" repository
 * (https://github.com/lammertb/libcrc, file src/crc16.c, MIT
 * License). The CRC_POLY_16 and CRC_START_16 constants are copied
 * verbatim from the same project's include/checksum.h. See
 * ../corpus_real/PROVENIENZA.md for exact provenance.
 *
 * The only addition (clearly marked below) is a minimal main() that
 * feeds argv[1] (treated as a raw byte string) to crc_16() and prints
 * the result as a decimal number, so the library can be exercised as
 * a standalone CLI program.
 *
 * Usage: r08_crc16 <string>
 * Prints the CRC-16 (polynomial 0xA001, "IBM"/Modbus-style table but
 * standard CRC-16 start value) checksum of <string> as a decimal
 * integer in [0, 65535], or "USAGE" if no argument was given.
 */
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* BEGIN verbatim third-party code: checksum.h constants (libcrc,     */
/* MIT)                                                                */
/* ------------------------------------------------------------------ */

#define CRC_POLY_16  0xA001
#define CRC_START_16 0x0000

/* ------------------------------------------------------------------ */
/* END verbatim third-party header constants.                        */
/* BEGIN verbatim third-party code: crc16.c (libcrc, MIT)             */
/* ------------------------------------------------------------------ */

static void             init_crc16_tab( void );

static bool             crc_tab16_init          = false;
static uint16_t         crc_tab16[256];

uint16_t crc_16( const unsigned char *input_str, size_t num_bytes ) {

	uint16_t crc;
	const unsigned char *ptr;
	size_t a;

	if ( ! crc_tab16_init ) init_crc16_tab();

	crc = CRC_START_16;
	ptr = input_str;

	if ( ptr != NULL ) for (a=0; a<num_bytes; a++) {

		crc = (crc >> 8) ^ crc_tab16[ (crc ^ (uint16_t) *ptr++) & 0x00FF ];
	}

	return crc;

}  /* crc_16 */

uint16_t update_crc_16( uint16_t crc, unsigned char c ) {

	if ( ! crc_tab16_init ) init_crc16_tab();

	return (crc >> 8) ^ crc_tab16[ (crc ^ (uint16_t) c) & 0x00FF ];

}  /* update_crc_16 */

static void init_crc16_tab( void ) {

	uint16_t i;
	uint16_t j;
	uint16_t crc;
	uint16_t c;

	for (i=0; i<256; i++) {

		crc = 0;
		c   = i;

		for (j=0; j<8; j++) {

			if ( (crc ^ c) & 0x0001 ) crc = ( crc >> 1 ) ^ CRC_POLY_16;
			else                      crc =   crc >> 1;

			c = c >> 1;
		}

		crc_tab16[i] = crc;
	}

	crc_tab16_init = true;

}  /* init_crc16_tab */

/* ------------------------------------------------------------------ */
/* END verbatim third-party code.                                    */
/* BEGIN our addition: minimal CLI wrapper (not part of upstream).   */
/* ------------------------------------------------------------------ */

int main(int argc, char **argv)
{
	if (argc < 2) {
		printf("USAGE\n");
		return 0;
	}

	uint16_t crc = crc_16((const unsigned char *)argv[1], strlen(argv[1]));
	printf("%u\n", (unsigned int)crc);

	return 0;
}
