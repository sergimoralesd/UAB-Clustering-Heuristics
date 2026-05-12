# Future Address Reuse

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `FutureAddressReuse` |
| **Category** | Address-based |
| **Complexity** | High |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | historical information of address usage |

## Description

Identifies the change output by exploiting that wallets behaviour. By checking if any output address has been used in the future, we can determine the change address. Wallets tent to generate completly fresh change addresses. So if any output is reused in some future transactions, we can determine which is the change address.

## Information Needed

This heurisitic needs the transactions where the output addresses are used in the future.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    actual_block_height = get_block_by_tx(tx)

    out_txs = []
    total_blocks_txs
    FOR out in tx.outputs:
        out_txs.append(get_txs_by_addr(out.addr))
        block_txs = []
        FOR out_tx in out_txs:
            block_txs.append(get_block_by_tx(out_tx))
        total_blocks_txs.append(sort(block_txs))
    
    addr_with_future = []
    FOR (i, block_txs) in enumerate(total_blocks_txs):
        FOR block_tx in block_txs:
            IF actual_block_height < block_tx -> addr_with_future.append(tx.outputs[tx.output[i]])
            break
    FOR out in tx.outputs:
        IF out.addr not in addr_with_future -> posible_change_addr.append(out.addr)
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All outputs addresses are used in future transactions, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither outputs addresses are used in the future | Both outputs match -> ambiguous |
| Every outputs addresses have been used in the future | No match |

## Exemple

TX 1:

    Inputs:
    - alice1 (3 btc)

    Outputs
    - (reused)output_1 (1.5 btc)
    - (no reused)output_2 (1.5 btc)

Step-by-step algorithm:

1. Compute the transactions where the output addresses are reused in the future
2. Return the address never used again in the future.

## Real Transaction Exemple

`2efd3285081e77c40125fb479b3b0b685ed6299d747a6e28a2c92899425bff7e`

## References

- [Heuristic-Based Address Clustering in Bitcoin](https://www.researchgate.net/publication/347083664_Heuristic-Based_Address_Clustering_in_Bitcoin) — Zhang, Wang & Luo, 2020
