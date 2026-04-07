# SmallerOuput

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `SmallerOutputChange` |
| **Category** | Value-based |
| **Complexity** | None |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | - |

## Description

Identifies the change output by exploiting users behaviour. By checking the output values, we can assume that the change address will be the smaller one.

## Information Needed

This heuristic needs the amount value of the outputs, meaning it only needs the actual transaction.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    min_value = tx.output[0].value
    if tx.output[0].value < tx.output[1].value:
        RETURN tx.output[0]
    elif tx.output[1].value < tx.output[0].value:
        RETURN tx.output[1]
    else:
        RETURN None

## When It Works

- One output value is smaller than the other.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Both outputs have the same amount | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice (3 btc)

    Outputs
    - output_1 (2.5 btc)
    - output_2 (0.5 btc)

Step-by-step algorithm:

1. Compute the smaller output value.
2. Return the corresponding output.

## Real Transaction Exemple

`d55b96a874cd68603cd5567701f69f981bdf813ea8b4c5aaa6ccf01fa0031bc7`

## References

- 
