# Uncompress Public Key

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `UncompressPublicKeyChange` |
| **Category** | Fingerprinting |
| **Complexity** | Medium-High |
| **Accuracy** | TBD |
| **Requirements** | 2-output transaction |
| **Additional Information** | previous transactions (for inputs public keys, in some ocassions), future transactions (to search coincidences) and previous' future transactions (for inputs' public keys) |

## Description

Identifies the change output by exploiting that wallets tend to generate consistent transactions. By checking if the transactions are using the compress or uncompressed public keys. This behaviour is different in some wallets, making it easier to detect the change.

## Information Needed

This heurisitic needs scriptSig from the transaction itself, and from the future transactions, in some cases it needs the scriptPubKey.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    uncompress_behaviour = has_uncompressed_pub_key()
    future_uncompress_behaviour = []
    FOR future_tx in tx.future_tx:
        future_segwit_behaviour.append(has_uncompressed_pub_key(future_tx))   

    posible_change_addr = []
    FOR (index, future_uncompress) in enumerate(future_uncompress_behaviour):
        IF uncompress_behaviour == future_uncompress -> posible_change_addr.append(tx.outputs[i])
    IF len(posible_change_addr) != 1 -> RETURN None
    ELSE -> RETURN posible_change_addr

## When It Works

- All future transactions following different public key behaviour, except one.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Neither future transaction follows the same public key behaviour from the inputs | No match |
| Every future transaction follows the public key behaviour | Both outputs match -> ambiguous |

## Exemple

TX 1:

    Inputs:
    - alice1 (3 btc)

    Outputs
    - output_1 (1.5 btc)
    - output_2 (1.5 btc)

    Uncompress Public Keys = True

TX 2 (spends output_1):

    Inputs:
    - output_1 (1.5 btc)

    Outputs
    - output_3 (1.0 btc)
    - output_4 (0.5 btc)

    Uncompress Public Keys = True

TX 3 (spends output_2):

    Inputs:
    - output_2 (1.5 btc)

    Outputs
    - output_5 (0.75 btc)
    - output_6 (0.75 btc)
    
    Uncompress Public Keys = False

Step-by-step algorithm:

1. Compute the if the public keys are compressed or not: {True, False}
2. Check for any coincidence with the actual transaction: (True)
3. Return the address used in the transaction that follows the same behaviour.

## Real Transaction Exemple

`2efd3285081e77c40125fb479b3b0b685ed6299d747a6e28a2c92899425bff7e`

## References

- [Wallet Fingerprints: Detection & Analysis](https://ishaana.com/blog/wallet_fingerprinting/) — Ishaana Misra, 2023
