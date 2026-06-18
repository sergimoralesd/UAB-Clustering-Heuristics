#!/usr/bin/env python3
"""
Heuristics over a tx_log.csv produced by the orchestrator.

Modes:
  fingerprint  (default) Extract every wallet fingerprinting feature
               (see uab_heuristics.fingerprinting) and print a per-wallet
               summary. Fast, no future_txs needed.
  change       Apply the change-detection heuristics
               (uab_heuristics.heuristics) to each transaction.

Usage:
    python run_heuristics.py --input tx_log.csv --output results.csv --mode fingerprint
    python run_heuristics.py --input tx_log.csv --output results.csv --mode change
"""

import argparse
import csv
import os

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

import bitcointx
bitcointx.select_chain_params("bitcoin")

from bitcointx.core import b2x, CTransaction

from uab_heuristics.core.tx import Tx
from uab_heuristics.utils import get_raw_tx_from_id
from uab_heuristics.fingerprinting import extract_features, ALL_FEATURES


# ──────────────────────────────────────────────────────────────────────────────
#  TX cache + prev_tx resolution
# ──────────────────────────────────────────────────────────────────────────────

def build_tx_cache(input_csv: str) -> dict:
    """Parse every raw_tx in the CSV into a txid -> Tx cache."""
    cache = {}
    print("Building TX cache...", end=" ", flush=True)
    with open(input_csv, newline="") as f:
        for row in csv.DictReader(f):
            try:
                tx = Tx.from_raw(row["raw_tx"])
                cache[tx.txid] = tx
            except Exception:
                pass
    print(f"{len(cache)} txs.")
    return cache


def resolve_prev_txs(tx: Tx, cache: dict) -> bool:
    """
    Resolve a tx's previous transactions from the local cache, falling back to
    RPC for inputs not present in the CSV (e.g. faucet funding txs).
    Returns True if all previous txs were resolved.
    """
    prev_txids = [b2x(vin.prevout.hash[::-1]) for vin in tx._tx.vin]
    prev_txs = []
    for txid in prev_txids:
        if txid in cache:
            prev_txs.append(cache[txid])
        else:
            try:
                raw = get_raw_tx_from_id(txid)
                prev_txs.append(Tx(base_tx=CTransaction.deserialize(raw)) if raw else None)
            except Exception:
                prev_txs.append(None)

    if any(p is None for p in prev_txs):
        return False
    tx._previous_txs = prev_txs
    return True


# ──────────────────────────────────────────────────────────────────────────────
#  Fingerprint mode
# ──────────────────────────────────────────────────────────────────────────────

def run_fingerprint(input_csv: str, output_csv: str):
    tx_cache = build_tx_cache(input_csv)
    fieldnames = ["wallet_sw", "txid", "change_index_gt"] + ALL_FEATURES
    ok = err = 0

    with open(input_csv, newline="") as f_in, \
         open(output_csv, "w", newline="") as f_out:

        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in csv.DictReader(f_in):
            txid    = row["txid"]
            wallet  = row["wallet_sw"]
            chg_raw = row.get("change_index")
            chg_idx = int(chg_raw.split("|")[0]) if chg_raw and chg_raw not in ("-1", "", "None") else -1

            try:
                tx = Tx.from_raw(row["raw_tx"])
                has_prev = resolve_prev_txs(tx, tx_cache)
                feats = extract_features(tx, chg_idx, has_prev)
                out = {"wallet_sw": wallet, "txid": txid, "change_index_gt": chg_raw}
                out.update(feats)
                writer.writerow(out)
                ok += 1
            except Exception:
                err += 1

    print(f"Fingerprint done — {ok} ok, {err} errors → {output_csv}")
    summarize(output_csv)


def summarize(output_csv: str):
    with open(output_csv, newline="") as f:
        rows = list(csv.DictReader(f))

    wallets = sorted({r["wallet_sw"] for r in rows})
    header = f"\n{'Signal':<30}  {'Value':<22}"
    for w in wallets:
        header += f"  {w[:20]:>20}"
    print(header)
    print("-" * (55 + 22 * len(wallets)))

    bool_sigs = ["signals_rbf", "low_r_only", "is_segwit", "input_order_bip69",
                 "nonstandard_sighash", "unusual_outputs", "dust_on_outputs",
                 "dust_on_inputs", "address_reuse", "multi_type_inputs", "compressed_keys"]
    int_sigs  = ["version", "anti_fee_sniping", "output_order", "change_type_matched_inputs"]
    enum_sigs = ["fee_rate_precision", "input_order", "output_structure", "output_types", "input_types"]

    def pct(rows, key, val):
        valid = [r for r in rows if r.get(key) not in ("None", "", None)]
        if not valid:
            return "N/A"
        m = sum(1 for r in valid if str(r[key]) == str(val))
        return f"{m/len(valid)*100:.1f}%"

    for sig in bool_sigs:
        line = f"  {sig:<28}  {'True':<22}"
        for w in wallets:
            wr = [r for r in rows if r["wallet_sw"] == w]
            line += f"  {pct(wr, sig, 'True'):>20}"
        print(line)

    for sig in int_sigs:
        all_vals = sorted({r[sig] for r in rows if r.get(sig) not in ("None", "", None)})
        for val in all_vals:
            line = f"  {sig:<28}  {str(val):<22}"
            for w in wallets:
                wr = [r for r in rows if r["wallet_sw"] == w]
                line += f"  {pct(wr, sig, val):>20}"
            print(line)

    for sig in enum_sigs:
        all_vals = sorted({r[sig] for r in rows if r.get(sig) not in ("None", "", None)})
        for val in all_vals[:10]:  # cap to avoid value explosion
            line = f"  {sig:<28}  {str(val)[:22]:<22}"
            for w in wallets:
                wr = [r for r in rows if r["wallet_sw"] == w]
                line += f"  {pct(wr, sig, val):>20}"
            print(line)

    print()


# ──────────────────────────────────────────────────────────────────────────────
#  Change detection mode
# ──────────────────────────────────────────────────────────────────────────────

CHANGE_HEURISTICS = [
    ("SmallerOutputChange",         "uab_heuristics.heuristics.smaller_output_change",  "SmallerOutputChange"),
    ("RoundedChange",               "uab_heuristics.heuristics.rounded_change",          "RoundedChange"),
    ("AddressTypeChange",           "uab_heuristics.heuristics.address_type_change",     "AddressTypeChange"),
    ("ReusedAddressChange",         "uab_heuristics.heuristics.reused_address_change",   "ReusedAddressChange"),
    ("OptimalChange",               "uab_heuristics.heuristics.optimal_change",          "OptimalChange"),
    ("ConsistentAddressTypeChange", "uab_heuristics.heuristics.consistent_address_type_change", "ConsistentAddressTypeChange"),
    ("EqualOutputCoinjoinChange",   "uab_heuristics.heuristics.equal_output_coinjoin_change",   "EqualOutputCoinjoinChange"),
]


def run_change(input_csv: str, output_csv: str):
    import importlib
    heuristics = []
    for name, mod_path, cls_name in CHANGE_HEURISTICS:
        mod = importlib.import_module(mod_path)
        heuristics.append((name, getattr(mod, cls_name)))

    tx_cache = build_tx_cache(input_csv)
    h_names  = [name for name, _ in heuristics]
    fieldnames = ["wallet_sw", "txid", "change_index_gt"]
    for name in h_names:
        fieldnames += [f"{name}_result", f"{name}_address"]

    with open(input_csv, newline="") as f_in, \
         open(output_csv, "w", newline="") as f_out:

        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for i, row in enumerate(csv.DictReader(f_in)):
            txid   = row["txid"]
            wallet = row["wallet_sw"]
            chg    = row["change_index"]
            out    = {"wallet_sw": wallet, "txid": txid, "change_index_gt": chg}

            try:
                tx = Tx.from_raw(row["raw_tx"])
                ok = resolve_prev_txs(tx, tx_cache)
                if not ok:
                    raise ValueError("Could not resolve all prev txs")
            except Exception as e:
                for name in h_names:
                    out[f"{name}_result"] = "ERR"
                    out[f"{name}_address"] = str(e)[:60]
                writer.writerow(out)
                continue

            for name, cls in heuristics:
                try:
                    r = cls.apply(tx)
                    out[f"{name}_result"]  = r.get("result", False)
                    out[f"{name}_address"] = "|".join(r.get("address") or [])
                except AssertionError:
                    out[f"{name}_result"]  = None
                    out[f"{name}_address"] = "SKIP"
                except Exception as e:
                    out[f"{name}_result"]  = None
                    out[f"{name}_address"] = f"ERR:{type(e).__name__}"

            writer.writerow(out)
            if (i + 1) % 500 == 0:
                print(f"  {i+1} txs...", flush=True)

    print(f"Change mode done → {output_csv}")


# ──────────────────────────────────────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input",  "-i", default="tx_log.csv")
    p.add_argument("--output", "-o", default="results.csv")
    p.add_argument("--mode",   "-m", default="fingerprint",
                   choices=["fingerprint", "change"],
                   help="fingerprint = wallet fingerprinting features (fast)\n"
                        "change      = change-detection heuristics")
    args = p.parse_args()

    if args.mode == "fingerprint":
        run_fingerprint(args.input, args.output)
    else:
        run_change(args.input, args.output)


if __name__ == "__main__":
    main()
