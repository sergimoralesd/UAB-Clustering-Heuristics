# Malformed Conjoin

## Basic Information

| Field | Value |
| --- | --- |
| **Class** | `MalformedCoinjoinChange` |
| **Category** | Value-based |
| **Complexity** | Low |
| **Accuracy** | TBD |
| **Requirements** | >1-output transaction |
| **Additional Information** | previous transactions (for inputs' values) |

## Description

Identifies the change output by exploiting the not-equal-valued outputs in a coinjoin. In a CoinJoin, multiple users combine their inputs and create equal-valued outputs to break transaction traceability. However, since each participant's input rarely matches the payment denomination exactly, the leftover value is returned as a change output with a non-equal amount. This heuristic computes the expected change for each input and matches it to an output.

## Information Needed

This heuristic needs the inputs' and outputs' values. Meaning it needs the transaction itself and the ones where the inputs comes from.

## Detailed Algorithm

Below we can find the detailed algorithm to try to identify the change outputs:

    amount_outputs_value = get_frequency(tx.outputs.value)
    denomination = max(amount_outputs_value)

    IF len(denomination) != 1 -> RETURN None

    change_addr = []

    FOR (input_addr, input_value) in tx.inputs:
        candidates = []
        posible_change = value - denomination.value

        FOR (output_addr, output_amount) in tx.outputs:
            IF posible_change - tx.fee <= output_amount <= posible_change: -> candidates.append(output_addr)
        
        IF len(candidates) > 1: -> RETURN None # multiple outputs could be change for this input
        IF len(candidates) == 0: -> continue # this input has no detectable change
        IF candidates in change_addr -> RETURN None # two inputs claim the same change output

        change_addr.append((input_addr, candidates))
    
    IF len(change_addr) > 0 -> RETURN change_addr
    ELSE -> RETURN None

## When It Works

- The CoinJoin uses a clear output value (single denomination).
- Each participant's input value is larger than the denomination, producing a unique change amount.
- Change amounts are distinct enough that each input maps unambiguously to exactly one change output.

## When It Fails

| Scenario | Reason |
| --- | --- |
| Multiple output values share the same highest frequency | Cannot determine the payment denomination |
| An input's expected change amount matches multiple outputs | Ambiguous mapping |
| Two inputs map to the same change output | Conflict in assignment |
| An input value equals the denomination exactly | No change produced for that input -> skipped (not a failure, but no result for that input) |
| Participants intentionally create change outputs that match the denomination | Change outputs blend in with payment outputs, making them undetectable |
| Fee estimation is inaccurate | The range `[possible_change - fee, possible_change]` may miss or over-match outputs |

## Exemple

    Inputs:

    - alice (5btc)
    - bob (3btc)

    Outputs

    - output_1 (1 btc)
    - output_2 (1 btc)
    - output_3 (4 btc)
    - output_4 (2 btc)

Step-by-step algorithm:

1. Compute the output frequency: {1: 2, 4: 1, 2: 1}
2. Chose denomination by selecting the most frequent output: denomination = 1
3. alice_posible_change: 5 - 1 = 4 -> "output_3"
4. bob_posible_change: 2 - 1 = 3 -> "output_4"

## Real Transaction Exemple

`c38aac9910f327700e0f199972eed8ea7c6b1920e965f9cb48a92973e7325046`

## References

- [Privacy - Equal-output CoinJoin](https://en.bitcoin.it/wiki/Privacy#Equal-output_CoinJoin) — Bitcoin Wiki
