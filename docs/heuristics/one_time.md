# One Time

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `OneTimeChange` |
| **Category** | Address-based |
| **Complexity** | High |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | historical information of address usage |

## Description

Identifies the change output by exploiting that wallets behaviour. By checking if any output address has been used in the past, we can determine the change address. Wallets tent to generate, every time a transaction requires a change, a completly new one.

## Information Needed

This heuristic needs the transactions where the output addresses were used.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    actual_block_height = get_block_by_tx(tx)

    out_txs = []
    total_blocks_txs = []
    FOR out in tx.outputs:
        out_txs.append(get_txs_by_addr(out.addr))
        block_txs = []
        FOR out_tx in out_txs:
            block_txs.append(get_block_by_tx(out_tx))
        total_blocks_txs.append(sort(block_txs))
    
    posible_change_addr = []
    FOR (i, block_txs) in enumerate(total_blocks_txs):
        IF actual_block_height < blocks_txs[0] -> posible_change_addr.append(tx.outputs[tx.output[i]])

    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All outputs addresses are already been used in the past, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither outputs addresses have been used in the past | Both outputs match -> ambiguous |
| Every outputs addresses have been used in the past | No match |

## Exemple

TX 1:

    Inputs:
    - alice1 (3 btc)

    Outputs
    - (reused)output_1 (1.5 btc)
    - (fresh)output_2 (1.5 btc)

Step-by-step algorithm:

1. Compute the transactions where the output addresses were used
2. Return the address never used before.

## Real Transaction Exemple

`4d8eabfc8e6c266fb0ccd815d37dd69246da634df0effd5a5c922e4ec37880f6`

## References

- [Heuristic-Based Address Clustering in Bitcoin](https://www.researchgate.net/publication/347083664_Heuristic-Based_Address_Clustering_in_Bitcoin) — Zhang, Wang & Luo, 2020
