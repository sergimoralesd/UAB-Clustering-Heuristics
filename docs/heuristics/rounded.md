# Rounded

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `RoundedChange` |
| **Category** | Value-based |
| **Complexity** | None |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | - |

## Description

Identifies the change output by exploiting the user behaviour. By checking the outputs' amount, we search for rounded payments because usually the change tend to be the non-rounded one.

## Information Needed

This heuristic needs the outputs' values from the transaction itself.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    precision = 10 ** (8 - n)

    posible_change_addr = []
    FOR output in tx.outputs:
        IF output.value % precision != 0 -> posible_change_addr.append(output)
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All outputs are rounded, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither output amount is rounded | No match |
| Every output amount is rounded | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice1 (3 btc)

    Outputs
    - output_1 (2.5 btc)
    - output_2 (0.45 btc)

    Fee = 0.05 btc

Step-by-step algorithm:

1. Compute the precision parameter.
2. Check every output amount.
3. Return the one that matches the precision parameter.

## Real Transaction Exemple

`6fd57e497c974c895ffc342cb2d6924b58f22ea792187c0a9ab7b286b435e58f` for a n=4

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
