# Zero Confirmation

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `ZeroConfirmationChange` |
| **Category** | Fingerprinting |
| **Complexity** | Medium-Low |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | future transactions (to search coincidences) |

## Description

Identifies the change output by exploiting users behaviours. By checking when the outputs where spent, we can identify the change addresses. It is higly recommended to not accept a payment until is being on the blockchain for at least 6 blocks, to avoid a double-spend. If any output is used before this 6 blocks range, we assume that the user controls also the address because he is trusting there is not a double-spend.  

## Information Needed

This heurisitic needs the block height where the transactions were included.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    actual_block_height = get_block_height_from_txid(tx)
    future_block_height = []
    FOR future_tx in tx.future_tx:
        future_block_height.append(get_block_height_from_txid(future_tx))   

    posible_change_addr = []
    FOR (index, future_height) in enumerate(future_block_height):
        IF actual_block_height == future_height -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions are spent waiting this 6 blocks time window, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction waits the recommended time window | No match |
| Every future transaction waits the time range | Both outputs match -> ambiguous |
| The outputs are still unspend | No match |

## Exemple

TX 1:

    Inputs:
    - alice1 (3 btc)

    Outputs
    - output_1 (1.5 btc)
    - output_2 (1.5 btc)

    Actual block height = 20

TX 2 (spends output_1):

    Inputs:
    - output_1 (1.5 btc)

    Outputs
    - output_3 (1.0 btc)
    - output_4 (0.5 btc)

   Actual block height = 30

TX 3 (spends output_2):

    Inputs:
    - output_2 (1.5 btc)

    Outputs
    - output_5 (0.75 btc)
    - output_6 (0.75 btc)
    
    Actual block height = 21

Step-by-step algorithm:

1. Compute where every future transaction was mined: {30, 21}
2. Check for any coincidence with the actual transaction: (20)
3. Return the address used in the transaction that matches does not follow the 6 block policy.

## Real Transaction Exemple

`a3efbb34f186ef710b7d0248d933d5330457a395e356cd99bb6f3dc9d1e2737e`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
