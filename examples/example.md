# Execution Example

This document explains how to run each heuristic category.

## Category 1 — "None" Input Data Requirements

These only need the raw transaction hex. No network calls, no extra imports.

```python
from uab_heuristics.core import Tx
from uab_heuristics.heuristics import (
    SmallerOutputChange,
    RoundedChange
)

tx = Tx.from_raw("0100000001...")   # your raw hex here

results = SmallerOutputChange.apply(tx)
print(f"SmallerOutputChange: {result}")

for n in range(2, 8):
    result = RoundedChange.apply(tx, n=n)
    print(f"RoundedChange n={n}: {result}")
```

## Category 2 — "Low" Input Data Requirements

These need the transactions where the **inputs were generated** of the current transaction. Call `import_previous_txs()` before applying any heuristic in this group.

```python
from uab_heuristics.core import Tx
from uab_heuristics.heuristics import (
    ReusedAddressChange,
)

tx = Tx.from_raw("0100000001...")   # your raw hex here
tx.import_previous_txs()

results = ReusedAddressChange.apply(tx)
print(f"ReusedAddressChange: {result}")

```

This is an example to understant how it works, the heuristics itself applies the `import_previous_txs` whenever needed.

## Category 3 — "Medium-Low" Input Data Requirements

These need the transactions that **spend the outputs** of the current transaction. Call `import_future_txs()` before applying any heuristic in this group.

```python
from uab_heuristics.core import Tx
from uab_heuristics.heuristics import (
    LocktimeChange,
)

tx = Tx.from_raw("0100000001...")   # your raw hex here
future_txs = ["9aa9e5917c29...", "1e53ae0cc698..."] #future txs if exists

tx.import_future_txs(future_txids=futures_txs)

results = LocktimeChange.apply(tx)
print(f"LocktimeChange: {result}")
```

The future have to be obtained before applying the heurisitcs because they do not have capabilities to search for this information.

## Category 4 — "Medium-High" Input Data Requirements

These need the transactions that **generated the inputs, spend the outputs and generated the inputs of each future transactions** of the current transaction. Call `import_previous_txs()`, `import_future_txs()`and for each future, `import_previous_txs()` before applying any heuristic in this group.

```python
from uab_heuristics.core import Tx
from uab_heuristics.heuristics import (
    FeeAbsoluteChange,
)

tx = Tx.from_raw("0100000001...")   # your raw hex here
tx.import_previous_txs()
future_txs = ["9aa9e5917c29...", "1e53ae0cc698..."] #future txs if exists

tx.import_future_txs(future_txids=futures_txs)

for future_tx in tx.future_txs:
    if future_tx is not None:
        future_tx.import_previous_txs()


results = FeeAbsoluteChange.apply(tx)
print(f"FeeAbsoluteChange: {result}")
```

Again, the import of the previous transactions, either for the actual transaction and for the future ones, will be done automatically by the heuristic.

## Category 5 — "High" Input Data Requirements

These heuristics apart from the previous information, information available outside.

```python
from uab_heuristics.core import Tx
from uab_heuristics.heuristics import (
    BackdatingChange,
)

tx = Tx.from_raw("0100000001...")   # your raw hex here
tx.import_previous_txs()
future_txs = ["9aa9e5917c29...", "1e53ae0cc698..."] #future txs if exists

tx.import_future_txs(future_txids=futures_txs)

for future_tx in tx.future_txs:
    if future_tx is not None:
        future_tx.import_previous_txs()


results = BackdatingChange.apply(tx)
print(f"FeeAbsoluteChange: {result}")
```

In this case, the code is exactly as before, this heuristic internally needs the block height where the transaction was mined
