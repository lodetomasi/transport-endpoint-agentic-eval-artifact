/*
 * r19_openbsd_strtonum.c
 *
 * REAL CODE, not written for this experiment. The strtonum()
 * function below is copied verbatim from the OpenBSD source tree
 * (https://github.com/openbsd/src, file
 * lib/libc/stdlib/strtonum.c, revision 1.8, Copyright (c) 2004 Ted
 * Unangst and Todd Miller, ISC-style permissive license -- "Permission
 * to use, copy, modify, and distribute this software for any purpose
 * with or without fee is hereby granted..."). strtonum() is the
 * OpenBSD libc function every OpenBSD program is encouraged to use
 * instead of atoi()/strtol() for safely parsing a bounded integer
 * from user input; it has since been adopted by several other BSDs
 * and by musl and other libcs as a portable helper. See
 * ../corpus_real/PROVENIENZA.md for exact provenance.
 *
 * ADAPTATION (documented, not silent): the line `DEF_WEAK(strtonum);`
 * at the end of the upstream file is an OpenBSD libc-internal macro
 * (defined in their own `<sys/cdefs.h>` variant) used to mark the
 * symbol as weak for their libc.so's own internal linking needs. That
 * macro is not defined outside an OpenBSD libc build, so it was
 * dropped; no other line was changed.
 *
 * The only other addition (clearly marked below) is a minimal main()
 * that calls strtonum() on argv[1] with the bounds given by argv[2]
 * (min) and argv[3] (max), printing the parsed value or the error
 * string ("invalid" / "too small" / "too large"), so the function can
 * be exercised as a standalone CLI program.
 *
 * Usage: r19_openbsd_strtonum <numstr> <minval> <maxval>
 * Prints the parsed number, or "ERROR:<errstr>" if strtonum() itself
 * rejected the input (errstr is one of "invalid", "too small", "too
 * large" -- upstream's own three error strings), or "USAGE" if fewer
 * than three arguments were given.
 */
#include <stdio.h>
#include <stdlib.h>

/* ------------------------------------------------------------------ */
/* BEGIN verbatim third-party code: strtonum.c (OpenBSD libc,         */
/* ISC-style permissive license)                                       */
/* ------------------------------------------------------------------ */

#include <errno.h>
#include <limits.h>

#define	INVALID		1
#define	TOOSMALL	2
#define	TOOLARGE	3

long long
strtonum(const char *numstr, long long minval, long long maxval,
    const char **errstrp)
{
	long long ll = 0;
	int error = 0;
	char *ep;
	struct errval {
		const char *errstr;
		int err;
	} ev[4] = {
		{ NULL,		0 },
		{ "invalid",	EINVAL },
		{ "too small",	ERANGE },
		{ "too large",	ERANGE },
	};

	ev[0].err = errno;
	errno = 0;
	if (minval > maxval) {
		error = INVALID;
	} else {
		ll = strtoll(numstr, &ep, 10);
		if (numstr == ep || *ep != '\0')
			error = INVALID;
		else if ((ll == LLONG_MIN && errno == ERANGE) || ll < minval)
			error = TOOSMALL;
		else if ((ll == LLONG_MAX && errno == ERANGE) || ll > maxval)
			error = TOOLARGE;
	}
	if (errstrp != NULL)
		*errstrp = ev[error].errstr;
	errno = ev[error].err;
	if (error)
		ll = 0;

	return (ll);
}

/* ------------------------------------------------------------------ */
/* END verbatim third-party code.                                    */
/* BEGIN our addition: minimal CLI wrapper (not part of upstream).   */
/* ------------------------------------------------------------------ */

int main(int argc, char **argv)
{
	if (argc < 4) {
		printf("USAGE\n");
		return 0;
	}

	long long minval = strtoll(argv[2], NULL, 10);
	long long maxval = strtoll(argv[3], NULL, 10);
	const char *errstr = NULL;

	long long result = strtonum(argv[1], minval, maxval, &errstr);

	if (errstr != NULL) {
		printf("ERROR:%s\n", errstr);
		return 0;
	}

	printf("%lld\n", result);

	return 0;
}
