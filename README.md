# UAB---Clustering-Heuristics
This repository provides tools for clustering addresses in Bitcoin It includes address normalization and multiple clustering strategies to group records that refer to the same entity.

## Optional Rust Tx backend

The `Tx` object can run from a Rust extension for better performance while keeping heuristics in Python.

### 1) Build and install the Rust module

```bash
cd /rust_tx_core
pip install maturin
maturin develop --release
```

### 2) Run heuristics normally

No code changes are required in heuristics. Importing `Tx` from `uab_heuristics.core` will use Rust when the module is installed, and fallback to Python otherwise.

### Notes

- The Rust module currently targets Bitcoin mainnet scripts.
- If you uninstall the module, the Python `Tx` implementation is used automatically.
