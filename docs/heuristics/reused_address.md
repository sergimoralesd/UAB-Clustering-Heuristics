# Reuse Address

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `ReusedAddressChange` |
| **Category** | Address-Based |
| **Complexity** | Low |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | previous transaction (to obtain the input address type) |

## Description

Identifies the change output by exploiting the fact that users tend to reuse the addresses. By checking the ouputs' addresses, we search for coincidences with the inputs, identifying the change output whenever we find a match.

## Information Needed

This heuristic needs the inputs and outputs addresses from the transaction itself.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    posible_change_addr = []
    FOR output in tx.outputs:
        IF tx.input.addr == output.addr -> posible_change_addr.append(output.addr)
    
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- An input is reused as an output

## When It Fails

| Scenario | Reason |
| --- | --- |
| Any input is used as an ouput | No match |
| Every input is used as an output | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice1 (1btc)

    Outputs
    - output_1 (0.6 btc)
    - alice1 (0.4 btc)

Step-by-step algorithm:

1. Check if any input address is reused in outputs and return it.

## Real Transaction Exemple

`547c6649c318d9238438f1acd26702c7e9e49e1dadd89fe50c8043426c943b52`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
