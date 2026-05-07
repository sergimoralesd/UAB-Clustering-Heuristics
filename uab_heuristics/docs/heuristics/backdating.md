# Backdating

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `BackdatingChange` |
| **Category** | Fingerprinting |
| **Complexity** | High |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | previous transactions (for locktime field), future transactions (to search coincidences) and previous' future transactions (for locktime field) |

## Description

Identifies the change output by exploiting that wallets tend to generate consistent transactions. By checking if the transactions are setting the locktime in a way that is chronologically imposible. This behaviour is only posible in BitcoinCore, making it easier to detect the change.

## Information Needed

This heurisitic needs locktime from the transaction itself, from the previous ones, from the future transactions and from the future previous. Besides, it needs the block height where the transactions were added.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    backdating_behaviour = is_backdating()
    future_backdating_behaviour = []
    FOR future_tx in tx.future_tx:
        future_backdating_behaviour.append(is_backdating(future_tx))   

    posible_change_addr = []
    FOR (index, future_backdating) in enumerate(future_backdating_behaviour):
        IF backdating_behaviour == future_backdating -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions are following a backdating policy, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction follows the same backdating behaviour from the inputs | No match |
| Every future transaction follows the same backdating policy | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice1 (3 btc)

    Outputs
    - output_1 (1.5 btc)
    - output_2 (1.5 btc)

    Backdating = True

TX 2 (spends output_1):

    Inputs:
    - output_1 (1.5 btc)

    Outputs
    - output_3 (1.0 btc)
    - output_4 (0.5 btc)

    Backdating = True

TX 3 (spends output_2):

    Inputs:
    - output_2 (1.5 btc)

    Outputs
    - output_5 (0.75 btc)
    - output_6 (0.75 btc)
    
    Backdating = False

Step-by-step algorithm:

1. Compute the if the transactions are backdating or not: {True, False}
2. Check for any coincidence with the actual transaction: (True)
3. Return the address used in the transaction that follows the same behaviour.

## Real Transaction Exemple

``

## References

- [GitHub Bitcoin Core](https://github.com/bitcoin/bitcoin/issues/26527) — 0xB10C, 2022
