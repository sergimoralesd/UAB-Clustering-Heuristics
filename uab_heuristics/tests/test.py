from ..core import Tx
from ..heuristics import *
import sqlite3
import re
import orjson
import json
import time

SQL_DB_FILE = "data/change_gt.db"
TXID_RE = re.compile(r'[0-9a-f]{64}')
RES_FILE = "data/results.json"
# select a bunch of txid from sql
# create the tx
# load the previous
# load future
# load future previous

def test_heuristics(tx, final_results):
    heuristic_list = [ReusedAddressChange, AddressTypeChange, RoundedChange,
                       SmallerOutputChange, OptimalChange, InputOrderChange,
                       OutputOrderChange, LocktimeChange, FeeAbsoluteChange,
                       FeeRelativeChange, VersionChange, SignalRBFChange,
                       ConsistentAddressTypeChange, ZeroConfirmationChange,
                       LowRChange, EqualOutputCoinjoinChange, MultiSignatureChange,
                       OneTimeChange, FutureAddressReuse, SegwitConformChange,
                       RoundedFiatChange]
    for heuristic in heuristic_list:
        final_results.setdefault(heuristic.name, {})
        try:    
            #print(f"Starting test with heuristic: {heuristic.name}")
            if heuristic is RoundedChange:
                for n in range(2, 8):
                    final_results[heuristic.name].setdefault(n, {})
                    result = heuristic.apply(tx=tx, n=n)
                    final_results[heuristic.name][n][tx.txid] = result

            elif heuristic is RoundedFiatChange:
                currencies = ['USD', 'EUR', 'GBP', 'CAD', 'CHF', 'AUD', 'JPY']
                for currency in currencies:
                    final_results[heuristic.name].setdefault(currency, {})
                    for n in range(2, 8):
                        final_results[heuristic.name][currency].setdefault(n, {})
                        result = heuristic.apply(tx=tx, n=n, currency=currency)
                        final_results[heuristic.name][currency][n][tx.txid] = result
            else:
                result = heuristic.apply(tx=tx)
                final_results[heuristic.name][tx.txid] = result

        except Exception as e:
            final_results[heuristic.name][tx.txid] = {"error" : str(e)}
            continue

    return final_results
    

def main():
    conn = sqlite3.connect(SQL_DB_FILE)
    cursor = conn.execute(
        "SELECT txid, previous_txids, future_txids FROM results WHERE error IS NULL LIMIT 1000"
    )
    final_results = {}

    for main_txid, prev_json, fut_json in cursor:
        initial_time = time.time()
        print(f"Txid: {main_txid}")
        main_tx = Tx.from_txid(main_txid)
        future_txs = []
        for entry in orjson.loads(fut_json):
            future_tx = Tx.from_txid(entry["txid"])
            future_tx.import_previous_txs()
            future_txs.append(future_tx)

        main_tx.import_previous_txs()
        main_tx.import_future_txs(future_txs=future_txs)
    
        final_results = test_heuristics(main_tx, final_results)
        print(f"Elapsed time: {time.time() - initial_time}")
    
    with open(RES_FILE, "w") as f:
        f.write(json.dumps(final_results, indent=4))
    
if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"Total:{time.time()-t0}")