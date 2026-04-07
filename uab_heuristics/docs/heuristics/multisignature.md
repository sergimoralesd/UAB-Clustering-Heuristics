# MultiSignature

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `MultiSignatureChange` |
| **Category** | Fingerprinting |
| **Complexity** | Medium-Low |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | future transactions (to search coincidences) |

## Description

Identifies the change output by exploiting the fact that wallets tend to generate consistent transactions. By checking the multisignature scheme, we search for coincidences with the spending transactions, identifying the change output whenever we find exactly one match. These schemes are not common and wide spread between the wallets, so the few that implement them tend to use the scheme.

## Information Needed

This heurisitic needs the scripSig field from the transaction itself, and from the spending ones.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    multisig_type = get_multisig_type(tx)
    future_multisig_type = []
    FOR future_tx in tx.future_tx:
        future_multisig_type.append(get_multisig_type(future_tx))   

    posible_change_addr = []
    FOR (index, future_multisig) in enumerate(future_multisig_type):
        IF multisig_type == future_multisig -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions use a different multisignature scheme, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction matches the multisignature scheme | No match |
| Every future transaction matches the multisignature scheme | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice1 (3 btc)

    Outputs
    - output_1 (1.9 btc)
    - output_2 (1.1 btc)

    Multisignature scheme = 2-3

TX 2 (spends output_1):

    Inputs:
    - output_1 (1.9 btc)

    Outputs
    - output_3 (1.4 btc)
    - output_4 (0.5 btc)

    Multisignature scheme = None

TX 3 (spends output_2):

    Inputs:
    - output_2 (1.1 btc)

    Outputs
    - output_5 (0.7 btc)
    - output_6 (0.4 btc)
    
    Multisignature scheme = 2-3

Step-by-step algorithm:

1. Compute all the low_r of each future transactions: {None, 2-3}
2. Check for any coincidence with the actual transaction: (2-3)
3. Return the address used in the transaction that matches the output order.

## Real Transaction Exemple

`1085ee6d2b65eb2cbd322e4afd0a43342bb943dd27a4ad6eddfdc6a7102b6b3c`

## References

- [Resurrecting Address Clustering in Bitcoin](https://arxiv.org/abs/2107.05749) — Möser & Narayanan, 2022
