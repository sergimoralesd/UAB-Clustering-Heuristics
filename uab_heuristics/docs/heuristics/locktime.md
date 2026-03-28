# Locktime

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `LocktimeChange` |
| **Category** | Fingerprinting |
| **Complexity** | Medium-Low |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | future transactions (to search coincidences) |

## Description

Identifies the change output by exploiting the fact that wallets tend to generate consistent transactions. By checking the "locktime" field and searching for coincidences with the spending transactions, this heurisitic is able to determine the change output.

## Information Needed

This heuristic needs the "locktime" field located in the transactions. So it needs the actual and every future transaction.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    locktime_future = []
    FOR future_tx in tx.future_tx:
        locktime_future.append(future_tx.locktime)   

    posible_change_addr = []
    FOR (index, future_locktime) in enumerate(locktime_future):
        IF tx.locktime == future_locktime -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions use a different version value, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction matches the locktime field fee | No match |
| Every future transaction matches the locktime field | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice (3 btc)

    Outputs
    - output_1 (1.5 btc)
    - output_2 (1.5 btc)

    Locktime = 0

TX 2 (spends output_1):

    Inputs:
    - output_1 (1.5 btc)

    Outputs
    - output_3 (0.5 btc)
    - output_4 (1 btc)

    Locktime = 500000

TX 3 (spends output_2):

    Inputs:
    - output_2 (1.5btc)

    Outputs
    - output_5 (0.75 btc)
    - output_6 (0.75 btc)

    Locktime = 0

Step-by-step algorithm:

1. Compute the version values of each future transactions: {0, 500000}
2. Check for any coincidence with the actual transaction: (0)
3. Return the address used in the transaction that matches the version fee.

## Real Transaction Exemple

`6fd57e497c974c895ffc342cb2d6924b58f22ea792187c0a9ab7b286b435e58f`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
