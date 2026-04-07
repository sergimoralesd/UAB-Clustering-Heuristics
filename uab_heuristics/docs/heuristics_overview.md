# Heuristic Overview

This document summarizes basic information of each heuristic implemented in this project.

---

## Categories Overview

| Category | Heuristics |
| --- | --- |
| **Address-based** | [Reused Address](./heuristics/reused_address.md), [Address Type](./heuristics/address_type.md), [Consistent Address Type](./heuristics/consistent_address_type.md), [One Time](./heuristics/one_time.md), [Future Address Reuse](./heuristics/future_address_reuse.md) |
| **Value-based** | [Smaller Output](./heuristics/smaller_output.md), [Rounded](./heuristics/rounded.md), [Rounded Fiat](./heuristics/rounded_fiat.md), [Optimal](./heuristics/optimal.md), [Equal Output Coinjoin](./heuristics/equal_output_coinjoin.md) |
| **Wallet fingerprint** | [Fee Absolute](./heuristics/fee_absolute.md), [Fee Relative](./heuristics/fee_relative.md), [Input Order](./heuristics/input_order.md), [Output Order](./heuristics/output_order.md), [Locktime](./heuristics/locktime.md), [Version](./heuristics/version.md), [Signal RBF](./heuristics/signal_rbf.md), [LowR](./heuristics/low_r.md), [Multi Signature](./heuristics/multisignature.md), [Segwit Conform](./heuristics/segwit_conform.md), [Uncompress Public Key](./heuristics/uncompress_public_key.md), [Zero Confirmation](./heuristics/zero_confirmation.md) |

---

## Complexity Overview

In the table belowe we can observe the complexity levels of each heuristic. This distinction is made taking into account the quantity of information needed to execute the heurisitc. The categories are: low, medium-low, medium, medium-high and high. Where "low" complexity heurisitcs require the transaction we are evaluating itself, and "high" complexity needs all the information available in the blockchain.

Here we are going to use the terminology "actual transaction", "previous transactions" and "future transactions". The first one, refers to the transaction we are currently evaluating, The second one, refers to the transactions where the inputs were created (`prev_txid` field). The third one, refers to the transactions where the outputs are used as inputs.

| Complexity | None | Low | Medium-Low | Medium | Medium-High | High |
| :--- | :---: | :---: | :---: | :---: | :---: | ---: |
| Information required | Actual | Actual + Previous | Actual + Future | Actual + Previous + Future | Actual + Previous + Future + Previous' Future | Whole blockchain |

## Accuracy Overview

In the --- below is shown the accuracy of every heuristic, this is computed from a [ground truth][1]. The values goes from "0" to "1", using up to two decimals.

## Citations

[1]: <https://arxiv.org/abs/2107.05749> "Resurrecting Address Clustering in Bitcoin"
