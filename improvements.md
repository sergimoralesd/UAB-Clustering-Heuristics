# Repository Improvements for UAB---Clustering-Heuristics

This document outlines the required architectural, coding, and documentation fixes needed to make the project "GitHub-ready" and professional before publishing.

## 1. Project Structure & Packaging

- [ ] **Move non-package directories out of the module**: Move `tests/`, `docs/`, and `examples/` from inside `uab_heuristics/` to the root directory. This prevents them from being installed into users' Python environments when they install your package.
- [ ] **Create a `pyproject.toml` or `setup.py`**: Add a python packaging file at the root level to define the package data and dependencies (e.g., `bitcointx`, `python-dotenv`, `maturin`, `blocksci`).
- [ ] **Create a `requirements.txt`**: List all required pip dependencies for local development.
- [ ] **Delete root `__init__.py`**: Remove the empty `__init__.py` in the root repository folder, as the root folder itself should not be a Python package.

### Recommended Final Directory Structure:
```
Root/
 ├─ uab_heuristics/    (Core package, keep __init__.py here)
 ├─ tests/             (Moved from uab_heuristics/tests)
 ├─ docs/              (Moved from uab_heuristics/docs)
 ├─ examples/          (Moved from uab_heuristics/examples)
 ├─ pyproject.toml     (New)
 ├─ requirements.txt   (New)
 ├─ .env.example       (New)
 ├─ README.md
 ├─ LICENSE
 └─ .gitignore
```
## 2. Code Quality & Best Practices

Remove assert for validation: In your heuristics files (e.g., backdating_change.py, address_type_change.py), you are using assert tx != None. Asserts are completely ignored if Python is run in optimized mode (-O). Replace them with proper exception handling:
Fix Type Hints: In tx.py, update base_tx: CTransaction = None to base_tx: Optional[CTransaction] = None (requiring from typing import Optional) or base_tx: CTransaction | None = None to satisfy static type checkers.
Correct Spelling Mistakes: Fix the typo Heurisitic in the docstrings of almost all heuristic classes across the heuristics directory.

## 3. Documentation (README & Setup)
Fix Rust path in README.md: Change the installation command cd /rust_tx_core in the README to the correct relative path: cd uab_heuristics/core/rust.
Add .env.example: Scripts like bitcoin_rpc.py and blocksci.py crash without environment variables (BTC_RPC_USER, BTC_RPC_PASSWORD, BTC_RPC_URL, BLOCKSCI_PATH). Provide a .env.example template at the root so users know what configuration is needed.
 Document Environment Variables: Add a "Configuration" section to the README.md explaining how to set up the .env file and what the variables are used for.

## 4. Testing Framework
Convert manual tests to automated tests: test_heuristics.py is currently a manual script using print() statements and commented-out execution blocks. Rewrite these using standard testing frameworks like pytest or unittest.
Add assertions to tests: Instead of visually checking CLI output, the tests must assert that your heuristics return the correct dictionary shapes and boolean results for known mock transactions.

## 5. Readme
Create a good readme file explaining how it works, installation, examples limitations...