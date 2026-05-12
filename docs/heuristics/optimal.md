# Optimal

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `OptimalChange` |
| **Category** | Value-based |
| **Complexity** | Low |
| **Accuracy** | TBD |
| **Requirements** | >1-input and 2-output transaction |
| **Additional Information** | previous transaction (to obtain the input values) |

## Description

Identifies the change output by exploiting the fact that wallets tend to create as smaller transactions as posible. By checking that all inputs are necessary, we can identify the address change. The wallets always avoid including unnecessary inputs in the transaction, because the user will have to pay more fees. So if we find any transaction that could be done using less inputs, we can conclude that there is not a change address between the outputs.

## Information Needed

This heurisitic needs the inputs and outputs values from the transaction itself.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    potential_change_value = min(tx.outputs_values)
    potential_change_addr = []
    FOR out in tx.outputs:
        IF out.value == potential_change_value -> potential_change_addr.append(out.addr)
    IF len(potential_change_value) > 1 -> RETURN None
    FOR in in tx.inputs:
        IF potential_change_value > in.value -> RETURN None
    RETURN potential_change_value
    

## When It Works

- All the inputs are necessary for the payment.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Exists an unnecessary input | No match |
| Both outputs amounts have the same value | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice1 (2 btc)
    - alice2 (3 btc)

    Outputs
    - output_1 (4 btc)
    - output_2 (1 btc)

Step-by-step algorithm:

1. Compute the posible change value: (1 btc)
2. Check if any input is lower than the potencial change
3. Return the address output of the change

## Real Transaction Exemple

`2efd3285081e77c40125fb479b3b0b685ed6299d747a6e28a2c92899425bff7e`

## References

- [Privacy - Unnecessary Input Heuristic](https://en.bitcoin.it/wiki/Privacy#Unnecessary_input_heuristic) — Bitcoin Wiki
