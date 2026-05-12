# Output Order

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `OutputOrderChange` |
| **Category** | Fingerprinting |
| **Complexity** | Medium-Low |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | future transactions (to search coincidences) |

## Description

Identifies the change output by exploiting the fact that wallets tend to generate consistent transactions. By checking the ouputs' orders, we search for coincidences with the spending transactions, identifying the change output whenever we find exactly one match. The outputs can be ordered using different technics, ascending or descending using the amount of each one or following the [BIP69](github.com/bitcoin/bips/blob/master/bip-0069.mediawiki).

## Information Needed

This heurisitic needs the outputs' values from the transaction itself, and from the spending ones.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    actual_output_order = get_output_order(tx)
    future_output_order = []
    FOR future_tx in tx.future_tx:
        future_output_order.append(get_output_order(future_tx))   

    posible_change_addr = []
    FOR (index, future_order) in enumerate(future_output_order):
        IF actual_output_order == future_order -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions use a different output order, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction matches the output order | No match |
| Every future transaction matches the output order | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice1 (1btc)
    - alice2 (2btc)

    Outputs
    - output_1 (2.5 btc)
    - output_2 (0.5 btc)

    Outputs' order = Descending order

TX 2 (spends output_1):

    Inputs:
    - output_1 (2.5btc)
    - output_X (2.3btc)

    Outputs
    - output_3 (3.3 btc)
    - output_4 (1.5 btc)
    Inputs' order = Descending order

TX 3 (spends output_2):

    Inputs:
    - output_2 (0.5btc)
    - output_y (1btc)

    Outputs
    - output_5 (0.4 btc)
    - output_6 (1.1 btc)
    Inputs' order = Ascending order

Step-by-step algorithm:

1. Compute all the inputs' order of each future transactions: {Descending, Ascending}
2. Check for any coincidence with the actual transaction: (Descending)
3. Return the address used in the transaction that matches the output order.

## Real Transaction Exemple

`2efd3285081e77c40125fb479b3b0b685ed6299d747a6e28a2c92899425bff7e`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
