/*
 * prog11_crc8.c
 *
 * Computes an 8-bit CRC over the bytes of argv[1] (treated as a raw
 * byte string), using polynomial 0x07, initial value 0x00, MSB-first,
 * no final XOR. Prints the result as two uppercase hex digits.
 *
 * If argv[1] is missing, prints "NO_INPUT". If argv[1] is empty,
 * prints the CRC of the empty message ("00"). Messages longer than
 * MAX_LEN bytes are rejected with "TOO_LONG" rather than truncated,
 * so the reported checksum always covers the whole input the caller
 * intended.
 */
#include <stdio.h>
#include <string.h>

#define CRC8_POLY 0x07
#define MAX_LEN 256

static unsigned char crc8(const unsigned char *data, size_t len) {
    unsigned char crc = 0x00;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (unsigned char)((crc << 1) ^ CRC8_POLY);
            } else {
                crc = (unsigned char)(crc << 1);
            }
        }
    }
    return crc;
}

static int count_set_bits(unsigned char v) {
    int count = 0;
    while (v != 0) {
        count += (v & 1);
        v = (unsigned char)(v >> 1);
    }
    return count;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("NO_INPUT\n");
        return 0;
    }

    size_t len = strlen(argv[1]);
    if (len > MAX_LEN) {
        printf("TOO_LONG\n");
        return 0;
    }

    const unsigned char *data = (const unsigned char *)argv[1];
    unsigned char result = crc8(data, len);

    /* Diagnostic only, does not affect the stdout checksum contract. */
    if (count_set_bits(result) == 8) {
        fprintf(stderr, "note: checksum has all bits set\n");
    }

    printf("%02X\n", result);

    return 0;
}
