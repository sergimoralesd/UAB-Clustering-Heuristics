# Rounded Fiat

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `RoundedFiatChange` |
| **Category** | Value-based |
| **Complexity** | High |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | historial information of the exchange rate |

## Description

Identifies the change output by exploiting the user behaviour. By checking the outputs' amount, we search for rounded payments in fiat currencies because usually the change tend to be the non-rounded one.

## Information Needed

This heurisitic needs the outputs' values from the transaction itself and the historial information of the exchange rate.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    precision = 10 ** (8 - n)

    posible_change_addr = []
    FOR output in tx.outputs:
        IF get_amount_fiat(output.value) % precision == 0 -> posible_change_addr.append(output)
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All outputs are rounded payments, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither output amount is rounded | No match |
| Every output amount is rounded | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice1 (1.8 btc) -> 50€

    Outputs
    - output_1 (0.9 btc) -> 25€
    - output_2 (0.75 btc) -> 20.83€

    Fee = 0.15 btc

Step-by-step algorithm:

1. Compute the precision parameter.
2. Compute the conversion of every output amount in any fiat currency.
3. Return the one that matches the precision parameter.

## Real Transaction Exemple

`2efd3285081e77c40125fb479b3b0b685ed6299d747a6e28a2c92899425bff7e` for a n=2 and currency=JPY

## References

- None
