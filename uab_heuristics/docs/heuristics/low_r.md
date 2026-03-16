# Low R

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `LowRChange` |
| **Category** | Fingerprinting |
| **Complexity** | Medium-Low |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | future transactions (to search coincidences) |

## Description

Identifies the change output by exploiting the fact that wallets tend to generate consistent transactions. By checking the signature, we search for coincidences with the spending transactions, identifying the change output whenever we find exactly one match. The "r" value in a ECDSA signature can be on the higher or lower half of the range, needing one extra byte in the first case. Some wallets generate signatures for the transactions trying to find a "low r" value to save a byte.

## Information Needed

This heurisitic needs the scripSig field from the transaction itself, and from the spending ones.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    actual_low_r = get_low_r(tx)
    future_low_r = []
    FOR future_tx in tx.future_tx:
        fuutre_low_r.append(get_low_r(future_tx))   

    posible_change_addr = []
    FOR (index, future_r) in enumerate(fuutre_output_order):
        IF actual_low_r == future_r -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions use a different low_r policy, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction matches the low_r policy | No match |
| Every future transaction matches the low_r policy | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice1 (1 btc)

    Outputs
    - output_1 (0.9 btc)
    - output_2 (0.1 btc)

    Low_r policy = True

TX 2 (spends output_1):

    Inputs:
    - output_1 (0.9 btc)

    Outputs
    - output_3 (0.4 btc)
    - output_4 (0.5 btc)

   Low_r policy = False

TX 3 (spends output_2):

    Inputs:
    - output_2 (0.1 btc)

    Outputs
    - output_5 (0.07 btc)
    - output_6 (0.03 btc)
    
    Low_r policy = True

Step-by-step algorithm:

1. Compute all the low_r of each future transactions: {False, True}
2. Check for any coincidence with the actual transaction: (True)
3. Return the address used in the transaction that matches the output order.

## Real Transaction Exemple

`2efd3285081e77c40125fb479b3b0b685ed6299d747a6e28a2c92899425bff7e`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
