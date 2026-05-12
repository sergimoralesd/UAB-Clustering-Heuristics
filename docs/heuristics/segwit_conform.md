# Segwit Conform

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `SegwitConformChange` |
| **Category** | Fingerprinting |
| **Complexity** | Medium-High |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | previous transactions (for inputs' addreces), future transactions (to search coincidences) and previous' future transactions (for inputs' values) |

## Description

Identifies the change output by exploiting that wallets tend to generate consistent transactions. By checking if the transactions are Sewgit serialized or not, we can identify the change addresses. This Segwit behaviour is different in some wallets, making it easier to detect the change.  

## Information Needed

This heurisitic needs inputs' addresses from the transaction itself, and from the future transactions.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    segwit_behaviour = get_segwit_behaviour(tx)
    future_segwit_behaviour = []
    FOR future_tx in tx.future_tx:
        future_segwit_behaviour.append(get_segwit_behaviour(future_tx))   

    posible_change_addr = []
    FOR (index, future_segwit) in enumerate(future_segwit_behaviour):
        IF segwit_behaviour == future_segwit -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions following different segwit behaviour, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction follows the segwit behaviour from the inputs | No match |
| Every future transaction follows the segwit behaviour | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice1 (3 btc)

    Outputs
    - output_1 (1.5 btc)
    - output_2 (1.5 btc)

    Segwit behaviour = True

TX 2 (spends output_1):

    Inputs:
    - output_1 (1.5 btc)

    Outputs
    - output_3 (1.0 btc)
    - output_4 (0.5 btc)

    Segwit behaviour = True

TX 3 (spends output_2):

    Inputs:
    - output_2 (1.5 btc)

    Outputs
    - output_5 (0.75 btc)
    - output_6 (0.75 btc)
    
    Segwit behaviour = False

Step-by-step algorithm:

1. Compute the segwit behaviour of future transactions: {True, False}
2. Check for any coincidence with the actual transaction: (True)
3. Return the address used in the transaction that follows the same behaviour.

## Real Transaction Exemple

`d55b96a874cd68603cd5567701f69f981bdf813ea8b4c5aaa6ccf01fa0031bc7`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
