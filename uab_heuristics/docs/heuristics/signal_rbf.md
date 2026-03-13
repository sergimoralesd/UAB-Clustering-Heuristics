# SignalRBF

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `SignalRBFChange` |
| **Category** | Fingerprinting |
| **Complexity** | Medium |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | future transactions (to search coincidences) |

## Description

Identifies the change output by exploiting the fact that wallets tend to generate consistent transactions. By checking the "sequence" field, we can determine if the transaction is marked to allow the RBF-policy. By  looking for coincidences with the spending transactions this heurisitic is able to determine the change output.

## Information Needed

This heuristic needs the "sequence" field located in the transactions. So it needs the actual and every future transaction.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    rbf_future = []
    FOR future_tx in tx.future_tx:
        rbf_future.append(marked_as_rbf(future_tx))   

    posible_change_addr = []
    FOR (index, future_rbf) in enumerate(rbf_future):
        IF marked_as_rbf(tx) == future_rbf -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions follow the same policy, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction matches the rbf policy | No match |
| Every future transaction matches the rbf policy | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice (3 btc)

    Outputs
    - output_1 (1.5 btc)
    - output_2 (1.5 btc)

    RBF-policy = True

TX 2 (spends output_1):

    Inputs:
    - output_1 (1.5 btc)

    Outputs
    - output_3 (0.5 btc)
    - output_4 (1 btc)

    RBF-policy = True

TX 3 (spends output_2):

    Inputs:
    - output_2 (1.5btc)

    Outputs
    - output_5 (0.75 btc)
    - output_6 (0.75 btc)

    RBF-policy = False

Step-by-step algorithm:

1. Compute the version values of each future transactions: {True, False}
2. Check for any coincidence with the actual transaction: (True)
3. Return the address used in the transaction that matches the version fee.

## Real Transaction Exemple

`547c6649c318d9238438f1acd26702c7e9e49e1dadd89fe50c8043426c943b52`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
