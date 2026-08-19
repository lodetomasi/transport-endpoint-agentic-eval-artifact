/*
 * prog57_elevator_fsm.c
 *
 * Explicit finite-state-machine simulation of a single elevator
 * serving floors MIN_FLOOR..MAX_FLOOR. The elevator starts idle at
 * floor 0. Each argv token is a requested floor, processed in order.
 *
 * For each request the elevator moves one floor at a time toward the
 * target, printing a transition line per floor moved, then arrives
 * and opens/closes its doors:
 *   "MOVE_UP f->f+1"   / "MOVE_DOWN f->f-1"
 *   "ARRIVE f"
 *   "DOORS_OPEN"
 *   "DOORS_CLOSE"
 * A request already equal to the current floor produces only
 * ARRIVE/DOORS_OPEN/DOORS_CLOSE (no movement lines). A request
 * outside the valid floor range prints "INVALID_FLOOR" and is
 * skipped without changing state.
 *
 * After all requests, prints "FINAL_FLOOR=<f>".
 */
#include <stdio.h>
#include <stdlib.h>

#define MIN_FLOOR 0
#define MAX_FLOOR 9

typedef enum { ST_IDLE, ST_MOVING_UP, ST_MOVING_DOWN, ST_DOORS_OPEN } state_t;

int main(int argc, char **argv) {
    int floor = 0;
    state_t state = ST_IDLE;

    for (int i = 1; i < argc; i++) {
        long target = strtol(argv[i], NULL, 10);
        if (target < MIN_FLOOR || target > MAX_FLOOR) {
            printf("INVALID_FLOOR\n");
            continue;
        }

        if (target > floor) {
            state = ST_MOVING_UP;
        } else if (target < floor) {
            state = ST_MOVING_DOWN;
        }

        while (floor != (int)target) {
            if (state == ST_MOVING_UP) {
                printf("MOVE_UP %d->%d\n", floor, floor + 1);
                floor++;
            } else {
                printf("MOVE_DOWN %d->%d\n", floor, floor - 1);
                floor--;
            }
        }

        state = ST_DOORS_OPEN;
        printf("ARRIVE %d\n", floor);
        printf("DOORS_OPEN\n");
        printf("DOORS_CLOSE\n");
        state = ST_IDLE;
    }

    printf("FINAL_FLOOR=%d\n", floor);
    return 0;
}
