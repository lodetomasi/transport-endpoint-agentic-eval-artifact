/*
 * prog60_inventory_sim.c
 *
 * Inventory / cash-register simulation over a fixed catalogue of
 * SKUs with hardcoded unit prices and starting stock. Transactions
 * are given as argv triples "OP sku qty":
 *   "S" sku qty   sell qty units of sku (fails if not enough stock)
 *   "R" sku qty   restock qty units of sku
 * Any trailing incomplete triple (fewer than 3 tokens left) is
 * ignored.
 *
 * One line is printed per processed transaction:
 *   "SELL sku=<s> qty=<q> revenue+=<amount>"
 *   "INSUFFICIENT_STOCK sku=<s>"
 *   "RESTOCK sku=<s> qty=<q>"
 *   "INVALID_SKU"
 *   "INVALID_OP"
 * After all transactions, prints:
 *   "FINAL stock=<s0,s1,s2,s3,s4> revenue=<total>"
 */
#include <stdio.h>
#include <stdlib.h>

#define NUM_SKUS 5

static const long price[NUM_SKUS] = { 10, 20, 5, 50, 100 };
static long stock[NUM_SKUS] = { 100, 50, 200, 10, 5 };

static int valid_sku(long v) {
    return v >= 0 && v < NUM_SKUS;
}

int main(int argc, char **argv) {
    long revenue = 0;
    int i = 1;

    while (argc - i >= 3) {
        const char *op = argv[i];
        long sku = strtol(argv[i + 1], NULL, 10);
        long qty = strtol(argv[i + 2], NULL, 10);
        i += 3;

        if (op[0] == 'S' && op[1] == '\0') {
            if (!valid_sku(sku)) {
                printf("INVALID_SKU\n");
                continue;
            }
            if (qty < 0 || qty > stock[sku]) {
                printf("INSUFFICIENT_STOCK sku=%ld\n", sku);
                continue;
            }
            stock[sku] -= qty;
            long amount = qty * price[sku];
            revenue += amount;
            printf("SELL sku=%ld qty=%ld revenue+=%ld\n", sku, qty, amount);
        } else if (op[0] == 'R' && op[1] == '\0') {
            if (!valid_sku(sku)) {
                printf("INVALID_SKU\n");
                continue;
            }
            if (qty < 0) {
                printf("INVALID_SKU\n");
                continue;
            }
            stock[sku] += qty;
            printf("RESTOCK sku=%ld qty=%ld\n", sku, qty);
        } else {
            printf("INVALID_OP\n");
        }
    }

    printf("FINAL stock=");
    for (int s = 0; s < NUM_SKUS; s++) {
        if (s > 0) {
            printf(",");
        }
        printf("%ld", stock[s]);
    }
    printf(" revenue=%ld\n", revenue);

    return 0;
}
