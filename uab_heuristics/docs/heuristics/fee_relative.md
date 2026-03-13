# Fee Relative

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `FeeRelativeChange` |
| **Category** | Fingerprinting |
| **Complexity** | Medium-High |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | previous transactions (for inputs' values), future transactions (to search coincidences) and previous' future transactions (for inputs' values) |

## Description

Identifies the change output by exploiting the fact that wallets tend to generate consistent transactions. By checking the relative fee paid by the user, we search for coincidences with the spending transactions, identifying the change output.

## Information Needed

This heurisitic needs the inputs' and outputs' values from the transaction itself, and from the spending ones. Meaning it needs the transaction, the ones where the inputs comes from, the future ones and the previous from each future.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    relative_fees_future = []
    FOR future_tx in tx.future_tx:
        relative_fees_future.append(future_tx.relative_fee)   

    posible_change_addr = []
    FOR (index, future_fee) in enumerate(relative_fees_future):
        IF tx.relative_fee == future_fee -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions use a different relative fee, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction matches the relative fee | No match |
| Every future transaction matches the relative fee | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice (3btc)

    Outputs
    - output_1 (1.4 btc)
    - output_2 (1.4 btc)

    Relative fee = 0.01 btc/vB

TX 2 (spends output_1):

    Inputs:
    - output_1 (1.4btc)

    Outputs
    - output_3 (0.2 btc)
    - output_4 (1 btc)
    Absolute fee = 0.01 btc/vB

TX 3 (spends output_2):

    Inputs:
    - output_2 (1.4btc)

    Outputs
    - output_5 (0.2 btc)
    - output_6 (0.8 btc)
    Absolute fee = 0.08 btc/vB

Step-by-step algorithm:

1. Compute all the relative fees of each future transactions: {0.01, 0.08}
2. Check for any coincidence with the actual transaction: (0.01)
3. Return the address used in the transaction that matches the relative fee.

## Real Transaction Exemple

`547c6649c318d9238438f1acd26702c7e9e49e1dadd89fe50c8043426c943b52`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
