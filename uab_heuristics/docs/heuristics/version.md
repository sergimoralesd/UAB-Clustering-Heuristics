# Version

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `VersionChange` |
| **Category** | Fingerprinting |
| **Complexity** | Medium |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | future transactions (to search coincidences) |

## Description

Identifies the change output by exploiting the fact that wallets tend to generate consistent transactions. By checking the "version" field and looking for coincidences with the spending transactions, this heurisitic is able to determine the change output.

## Information Needed

This heuristic needs the "version" field located in the transactions. So it needs the actual and every future transaction.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    version_future = []
    FOR future_tx in tx.future_tx:
        version_future.append(future_tx.version)   

    posible_change_addr = []
    FOR (index, future_version) in enumerate(version_future):
        IF tx.version == future_version -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions use a different version value, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction matches the version field fee | No match |
| Every future transaction matches the version field | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice (3 btc)

    Outputs
    - output_1 (1.5 btc)
    - output_2 (1.5 btc)

    Version = 2

TX 2 (spends output_1):

    Inputs:
    - output_1 (1.5 btc)

    Outputs
    - output_3 (0.5 btc)
    - output_4 (1 btc)

    Version = 2

TX 3 (spends output_2):

    Inputs:
    - output_2 (1.5btc)

    Outputs
    - output_5 (0.75 btc)
    - output_6 (0.75 btc)

    Version = 1

Step-by-step algorithm:

1. Compute the version values of each future transactions: {2, 1}
2. Check for any coincidence with the actual transaction: (2)
3. Return the address used in the transaction that matches the version fee.

## Real Transaction Exemple

`547c6649c318d9238438f1acd26702c7e9e49e1dadd89fe50c8043426c943b52`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
