# UAB Clustering Heuristics for Bitcoin

A comprehensive framework for applying advanced clustering heuristics and address normalization to the Bitcoin blockchain. This toolkit enables researchers and analysts to group addresses that likely refer to the same entity using various strategies, such as change-address detection, input/output behaviors, and other transaction graph heuristics.

## Features

- **Multiple Clustering Strategies:** Includes heuristics for reused addresses, optimal change, round numbers, fee logic, and more.
- **Address Normalization:** Standardizes Bitcoin addresses for easier comparison.
- **Multiple Data Sources:** Integrates with local Bitcoin RPC nodes and [BlockSci](https://github.com/citp/BlockSci) for querying blockchain data.
- **Optional Rust Backend:** A high-performance transaction (`Tx`) backend implemented in Rust for significantly faster parsing and evaluation.

---

## Prerequisites

- **Python 3.8+**
- A synced **Bitcoin Core Node** (with RPC enabled) OR **BlockSci** configured locally.
- *(Optional)* **Rust and Cargo** (if you plan to compile the faster Rust extension).

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/UAB---Clustering-Heuristics.git
cd UAB---Clustering-Heuristics
```

### 2. Install Python dependencies

Create a virtual environment and install the required packages:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

The data adapters require specific variables to connect to a Bitcoin node or BlockSci.
Copy the example environment file and edit it with your credentials:

```bash
cp .env.example .env
```

### Optional: Build the Rust Backend

For severe data analysis, we highly recommend utilizing the Rust backend for parsing transactions. This keeps the heuristics written in accessible Python while offloading the heavy `Tx` object processing to Rust.

**1. Navigate to the Rust module directory:**

```bash
cd uab_heuristics/core/rust
```

**2. Build and install with Maturin:**

```bash
pip install maturin
maturin develop --release
```

Note: No code changes are required in your Python scripts. If the Rust module is successfully installed, from uab_heuristics.core import Tx will automatically use it. If the module is missing or uninstalled, the library smoothly falls back to the native Python implementation.

## How to Run

You can run individual heuristics by importing the target strategy and applying it to a parsed transaction.

Here is a quick example using the `OptimalChange` heuristic:

```python
from uab_heuristics.core import Tx
from uab_heuristics.heuristics import OptimalChange

# Initialize the heuristic
heuristic = OptimalChange()

# Load a transaction via ID (requires your .env to be configured)
tx_id = "8eabad99fe4607a1f4a7e2979d34e0c8cad0a36e41d8e68061457fbc535bbfeb"
transaction = Tx.from_txid(tx_id)

# Apply the heuristic
result = heuristic.apply(transaction)

if result['result']:
    print(f"Change address detected: {result['address']}")
else:
    print("No change address found with this heuristic.")
```

## Examples & Documentation

- **Examples**: Check out the examples/ directory for complete, runnable scripts demonstrating different clustering workflows, processing txids in bulk, and comparing heuristic results.
- **Documentation**: For deep dives into how specific heuristics behave (e.g., Multisig, CoinJoin, Locktime), read through the markdown files located in the docs/ folder.

## Important Notes

- **Network Constraints**: The Rust extension and heuristics have currently been built and targeted toward Bitcoin mainnet scripts.
- **API Rate Limits**: If you are hitting public/external APIs rather than your local RPC, note that batching too many requests rapidly may lead to timeout or HTTP 429 (FetchError). Use local bitcoin-rpc or BlockSci for heavy processing.
