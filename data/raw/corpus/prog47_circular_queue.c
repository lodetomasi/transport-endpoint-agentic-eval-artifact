/*
 * prog47_circular_queue.c
 *
 * Simulates a fixed-capacity circular queue driven by a sequence of
 * commands given as argv tokens:
 *   "Ex"  enqueue integer x (token starts with 'E', rest is the number)
 *   "D"   dequeue
 *   "F"   peek at the front element
 * Any other token is treated as an invalid command.
 *
 * One result line is printed per command:
 *   "ENQ x"   / "FULL"     for enqueue
 *   "DEQ x"   / "EMPTY"    for dequeue
 *   "FRONT x" / "EMPTY"    for peek
 *   "ERR"                  for an unrecognized command
 * If there are no commands at all, prints "NOOP".
 */
#include <stdio.h>
#include <stdlib.h>

#define CAPACITY 5

static long items[CAPACITY];
static int head;
static int count;

static int enqueue(long v) {
    if (count >= CAPACITY) {
        return 0;
    }
    int tail = (head + count) % CAPACITY;
    items[tail] = v;
    count++;
    return 1;
}

static int dequeue(long *out) {
    if (count <= 0) {
        return 0;
    }
    *out = items[head];
    head = (head + 1) % CAPACITY;
    count--;
    return 1;
}

static int peek_front(long *out) {
    if (count <= 0) {
        return 0;
    }
    *out = items[head];
    return 1;
}

int main(int argc, char **argv) {
    head = 0;
    count = 0;

    if (argc <= 1) {
        printf("NOOP\n");
        return 0;
    }

    for (int i = 1; i < argc; i++) {
        const char *tok = argv[i];

        if (tok[0] == 'E') {
            char *end;
            long v = strtol(tok + 1, &end, 10);
            if (end == tok + 1 || *end != '\0') {
                printf("ERR\n");
                continue;
            }
            if (enqueue(v)) {
                printf("ENQ %ld\n", v);
            } else {
                printf("FULL\n");
            }
        } else if (tok[0] == 'D' && tok[1] == '\0') {
            long v;
            if (dequeue(&v)) {
                printf("DEQ %ld\n", v);
            } else {
                printf("EMPTY\n");
            }
        } else if (tok[0] == 'F' && tok[1] == '\0') {
            long v;
            if (peek_front(&v)) {
                printf("FRONT %ld\n", v);
            } else {
                printf("EMPTY\n");
            }
        } else {
            printf("ERR\n");
        }
    }

    return 0;
}
