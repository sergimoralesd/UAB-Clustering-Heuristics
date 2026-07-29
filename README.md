# UAB Clustering Heuristics — Rust Implementation

A Rust library that implements Bitcoin **change-address heuristics**: rules used to guess which output of a transaction is "change" being sent back to the spender, as opposed to a genuine payment to a third party.

## Main points

- **Core `Tx` type** (`src/tx.rs`): wraps a `bitcoin::Transaction` and adds the extra context heuristics need — previous transactions (where inputs came from), future transactions (where outputs were later spent), block height, and RBF replacement transactions. It can be built from a raw hex transaction, a txid (fetched from the network), or a JSON transaction, and exposes helpers like `inputs_addresses()`, `outputs_types()`, `absolute_fee()`, `relative_fee()`, `is_segwit()`, and `signals_rbf()`.
- **`Heuristic` trait** (`src/heuristics/mod.rs`): a common interface every heuristic implements — `name()`, `input_data_requirements()`, and `apply(&Tx) -> Result<Vec<bool>, AppError>`, returning one boolean per output indicating whether that output could be the change output. Each heuristic declares how much contextual data it needs (`None` up to `HighNonIndexed`), and `check_requirements()` verifies that data was actually imported into the `Tx` before running.
- **24 heuristics implemented** under `src/heuristics/`, grouped (per `docs/heuristics_overview.md`) into:
  - **Address-based**: reused address (past/present/future), address type, consistent address type, one-time address.
  - **Value-based**: smaller output, rounded amount, rounded fiat value, optimal change, malformed CoinJoin.
  - **Wallet-fingerprinting**: backdating, absolute/relative fee, input order, output order, locktime, version, signal RBF / RBF, low-R signatures, multisignature, SegWit conformance, uncompressed public keys, low confirmation value.
- **External data helpers** (`src/heuristics/api.rs`): `get_txs_by_address` and `get_historical_price`, which pull transaction and historical price data from the mempool.space API.
- **Python bindings** (`src/python_package/`, built with PyO3): exposes a `PyTx` class and a `PyClass` wrapper per heuristic (e.g. `AddressTypeChange`, `OptimalChange`, `RoundedChange` with a configurable precision parameter, `RoundedFiatChange` with precision + currency) so the same logic can be driven from Python.
- **Error handling** (`src/types.rs`): a unified `AppError` enum wraps transaction, heuristic, API, and test-specific errors with descriptive messages.
- **Tests**: unit tests inside most heuristic files plus an integration suite in `change_heuristics/tests/test_heuristics.rs` backed by real transaction data in `change_heuristics/tests/data/`.
- **Docs**: `docs/heuristics_overview.md` and `docs/heuristics/` describe each heuristic and the "input data requirement" complexity levels (how much blockchain context — actual/previous/future transactions, or the whole chain — each heuristic needs).
- **License**: GNU GPLv3.

## Dependencies

**Rust crate** (`change_heuristics/Cargo.toml`, edition 2024):
- [`serde`](https://crates.io/crates/serde) / [`serde_json`](https://crates.io/crates/serde_json) — (de)serialization
- [`bitcoin`](https://crates.io/crates/bitcoin) (v0.29, `serde` feature) — Bitcoin transaction/address types
- [`reqwest`](https://crates.io/crates/reqwest) (blocking + json) — HTTP calls to the mempool.space API
- [`pyo3`](https://crates.io/crates/pyo3) (v0.29, `extension-module` feature) — Python bindings
- [`hex`](https://crates.io/crates/hex) — hex encoding/decoding

The crate builds as both a `cdylib` (Python extension module, name `change_heuristics`) and an `rlib` (usable as a normal Rust dependency).

**Python side** (`requirements.txt`, for building/using the Python package):
- `maturin` — builds the PyO3 extension into an installable Python wheel

**Toolchain requirements**: a recent stable Rust toolchain (edition 2024 support), Python 3.8+, and `pip`.

## How to run

### 1. Clone the branch

```bash
git clone --branch rust_implementation https://github.com/sergimoralesd/UAB-Clustering-Heuristics.git
cd UAB-Clustering-Heuristics
```

### 2. Rust: build and test the library

```bash
cd change_heuristics
cargo build
cargo test
```

`cargo test` runs both the per-heuristic unit tests and the integration tests in `tests/test_heuristics.rs`, which read fixture data from `tests/data/`.

### 3. Python: build and use the bindings

From the repository root, install the Python build dependencies:

```bash
pip install -r requirements.txt
```

Then, from the `change_heuristics/` directory, build the extension module with `maturin` and install it into your active virtual environment:

```bash
cd change_heuristics
maturin develop
```

Once built, the module can be imported directly in Python:

```python
import change_heuristics as ch

tx = ch.PyTx("0100...raw hex...", network="bitcoin")  # network defaults to "bitcoin"
print(tx.txid(), tx.inputs_addresses(), tx.outputs_types())

heuristic = ch.AddressTypeChange()
print(heuristic.apply(tx))  # one bool per output: possible change or not
```

Some heuristics need extra context imported onto the `Tx` before they can run (check `input_data_requirements()` on the heuristic, cross-referenced with `docs/heuristics_overview.md`):

```python
tx.import_previous_txs([prev_tx_1, prev_tx_2])   # list of PyTx
tx.import_future_txs([fut_tx_1])                 # list of PyTx
tx.import_block_height(820000)
tx.import_replacement_tx("...raw hex of replacement tx...")
```

### 4. Optional: live blockchain / price data and node config

- `get_txs_by_address` and `get_historical_price` (Rust side) fetch data from the public `mempool.space` API and need no extra setup, but do require network access.

## Repository layout

```
.
├── change_heuristics/
│   ├── Cargo.toml / Cargo.lock
│   ├── src/
│   │   ├── lib.rs                # crate root
│   │   ├── tx.rs                 # Tx struct: parsing, context, derived properties
│   │   ├── types.rs              # error types, InputDataRequirements, JSON tx schema
│   │   ├── heuristics/           # Heuristic trait + 22 implementations + mempool.space API helpers
│   │   └── python_package/       # PyO3 bindings (PyTx + one class per heuristic)
│   └── tests/                    # integration tests + fixture data
├── docs/
│   ├── heuristics_overview.md    # categories + input-data-requirement complexity levels
│   └── heuristics/               # one doc per heuristic
├── requirements.txt               # Python build/runtime deps
├── .env.example                   # optional RPC / BlockSci config template
└── LICENSE                        # GPLv3
```