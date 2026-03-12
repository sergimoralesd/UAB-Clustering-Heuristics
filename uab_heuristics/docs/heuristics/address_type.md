# Address Type

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `AddressTypeChange` |
| **Category** | Address-Based |
| **Complexity** | Medium-Low |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | previous transactions (for input address types) |

## Description

Identifies the change output by comparing the address types of the inputs and outputs. Bitcoin wallets typically use a single address type. When a transaction has two outputs with different address types, the one matching the input type is likely the change.

## Information Needed

This heurisitic need the inputs and outputs addresses types. Meaning it needs the transaction itself and the ones where the inputs comes from.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change output:

    input_types = { get_address_type(i) for i in tx.inputs }
    output_types = { get_address_type(o) for o in tx.outputs }

    IF len(output_types) != 2  → RETURN None
    IF input_type NOT IN output_types → RETURN None

    FOR output IN tx.outputs:
        IF get_address_type(output) == input_type → change  = output

    RETURN change

## When It Works

- The sender and recipient use **different** address types (e.g., sender uses P2WPKH, recipient uses P2TR).
- All inputs come from the same address type.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Both outputs share the same type as the inputs | Both match → ambiguous |
| Neither output matches the input type | No match |
| Inputs have mixed address types | Multiple types could match multiple outputs |
| Recipient coincidentally uses the same type | Both outputs match → ambiguous |

## Exemple

## Transaction Exemple

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
