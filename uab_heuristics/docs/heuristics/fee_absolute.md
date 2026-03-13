# Fee Absolute

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `FeeAbsoluteChange` |
| **Category** | Fingerprinting |
| **Complexity** | Medium-High |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | previous transactions (for inputs' values), future transactions (to search coincidences) and previous' future transactions (for inputs' values) |

## Description

Identifies the change output by exploiting the fact that wallets tend to generate consistent transactions. By checking the absolute fee paid by the user, we can find coincidences with the spending transactions, identifying the change output.

## Information Needed

This heurisitic needs the inputs' and outputs' values from the transaction itself, and from the spending ones. Meaning it needs the transaction, the ones where the inputs comes from, the future ones and the previous from each future.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    absolute_fees_future = []
    FOR future_tx in tx.future_tx:
        absolute_fees_future.append(future_tx.absolute_fee)   

    posible_change_addr = []
    FOR (index, future_fee) in enumerate(absolute_fees_future):
        IF tx.absolute_fee == future_fee -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions use a different absolute fee, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction matches the absolute fee | No match |
| Every future transaction matches the absolute fee | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice (3btc)

    Outputs
    - output_1 (1.4 btc)
    - output_2 (1.4 btc)

    Absolute fee = 0.2 btc
TX 2 (spends output_1):

    Inputs:
    - output_1 (1.4btc)

    Outputs
    - output_3 (0.2 btc)
    - output_4 (1 btc)
    Absolute fee = 0.2 btc

TX 3 (spends output_2):

    Inputs:
    - output_2 (1.4btc)

    Outputs
    - output_5 (0.2 btc)
    - output_6 (0.8 btc)
    Absolute fee = 0.4 btc

Step-by-step algorithm:

1. Compute all the absolute fees of every future transactions: {0.2, 0.4}
2. Check for any coincidence with the actual transaction: (0.2)
3. Return the address used in the transaction that matches the fee.

## Real Transaction Exemple

`6fd57e497c974c895ffc342cb2d6924b58f22ea792187c0a9ab7b286b435e58f`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
