/*
 * r04_rot13.c
 *
 * REAL CODE, not written for this experiment. The rot13() function
 * below is copied verbatim from Brad Conte's "crypto-algorithms"
 * repository (https://github.com/B-Con/crypto-algorithms, files
 * rot-13.c/rot-13.h, released into the public domain per the
 * repository README). See ../corpus_real/PROVENIENZA.md for exact
 * provenance.
 *
 * The only addition (clearly marked below) is a minimal main() that
 * copies argv[1] into a mutable buffer, calls rot13() in place, and
 * prints the result, so the library can be exercised as a standalone
 * CLI program.
 *
 * Usage: r04_rot13 <string>
 * Prints the ROT-13 transform of <string> (max 255 chars, longer
 * input is rejected as "TOO_LONG"), or "USAGE" if no argument was
 * given. Non-alphabetic characters are passed through unchanged.
 */
#include <stdio.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* BEGIN verbatim third-party code: rot-13.c (Brad Conte,             */
/* crypto-algorithms, public domain)                                  */
/* ------------------------------------------------------------------ */

void rot13(char str[])
{
   int case_type, idx, len;

   for (idx = 0, len = strlen(str); idx < len; idx++) {
      /* Only process alphabetic characters. */
      if (str[idx] < 'A' || (str[idx] > 'Z' && str[idx] < 'a') || str[idx] > 'z')
         continue;
      /* Determine if the char is upper or lower case. */
      if (str[idx] >= 'a')
         case_type = 'a';
      else
         case_type = 'A';
      /* Rotate the char's value, ensuring it doesn't accidentally "fall off" the end. */
      str[idx] = (str[idx] + 13) % (case_type + 26);
      if (str[idx] < 26)
         str[idx] += case_type;
   }
}

/* ------------------------------------------------------------------ */
/* END verbatim third-party code.                                    */
/* BEGIN our addition: minimal CLI wrapper (not part of upstream).   */
/* ------------------------------------------------------------------ */

#define MAX_LEN 255

int main(int argc, char **argv)
{
	if (argc < 2) {
		printf("USAGE\n");
		return 0;
	}

	if (strlen(argv[1]) > MAX_LEN) {
		printf("TOO_LONG\n");
		return 0;
	}

	static char buf[MAX_LEN + 1];
	strcpy(buf, argv[1]);
	rot13(buf);
	printf("%s\n", buf);

	return 0;
}
