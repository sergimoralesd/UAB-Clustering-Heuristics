# Input Order

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `InputOrderChange` |
| **Category** | Fingerprinting |
| **Complexity** | High |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | previous transactions (for inputs' values), future transactions (to search coincidences) and previous' future transactions (for inputs' values) |

## Description

Identifies the change output by exploiting the fact that wallets tend to generate consistent transactions. By checking the inputs' orders, we search for coincidences with the spending transactions, identifying the change output whenever we find exactly one match. The inputs can be ordered inside the transaction using different technics, ascending or descending using the amount of each one, following the [BIP69](github.com/bitcoin/bips/blob/master/bip-0069.mediawiki) or using historical information.

## Information Needed

This heuristic needs the inputs' values from the transaction itself, and from the spending ones. Meaning it needs the transaction, the ones where the inputs comes from, the future ones and the previous from each future. Besides that, it requires when the transactions appeared on the blockchain.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    actual_input_order = get_input_order(tx)
    future_input_order = []
    FOR future_tx in tx.future_tx:
        future_input_order.append(get_input_order(future_tx))   

    posible_change_addr = []
    FOR (index, future_order) in enumerate(future_input_order):
        IF actual_input_order == future_order -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions use a different input order, except the one that matches the inputs.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction matches the input order | No match |
| Every future transaction matches the input order | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice1 (1btc)
    - alice2 (2btc)
    - alice3 (3btc)

    Outputs
    - output_1 (5.5 btc)
    - output_2 (0.5 btc)

    Inputs' order = Ascending order

TX 2 (spends output_1):

    Inputs:
    - output_1 (5.5btc)
    - output_X (2.3btc)

    Outputs
    - output_3 (4.3 btc)
    - output_4 (3.5 btc)

    Inputs' order = Descending order

TX 3 (spends output_2):

    Inputs:
    - output_2 (0.5btc)
    - output_y (1btc)

    Outputs
    - output_5 (1.2 btc)
    - output_6 (0.3 btc)
    
    Inputs' order = Ascending order

Step-by-step algorithm:

1. Compute all the inputs' order of each future transactions: {Descending, Ascending}
2. Check for any coincidence with the actual transaction: (Ascending)
3. Return the address used in the transaction that matches the input order.

## Real Transaction Exemple

`547c6649c318d9238438f1acd26702c7e9e49e1dadd89fe50c8043426c943b52`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
