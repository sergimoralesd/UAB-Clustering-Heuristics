from pathlib import Path

from uab_heuristics.core import Tx
from uab_heuristics.heuristics import *
from uab_heuristics.utils import get_collection_tx

BASE_DIR = Path(__file__).resolve().parent


def test_heuristic(txs, heuristic_cls):
    print("#" * 50)
    heuristic = heuristic_cls()
    print(f"Starting test with heuristic: {heuristic.name}")

    for tx_id, tx_raw in txs:
        try:
            print(f"Applying heuristic to tx: \n{tx_id}")
            tx = Tx.from_raw(tx_raw)
            print(f"Input addrecess: \n{tx.input_addresses}")
            print(f"Output addrecess: \n{tx.output_addresses}")
            result_reused_addr_change = heuristic.apply(tx)
            print(f"Result from heurisitc: \n{result_reused_addr_change}")
        except Exception as e:
            print(e)
    print("#" * 50)

if __name__ == "__main__":

    filename = BASE_DIR / "data" / "tx_collection.json"
    txs = get_collection_tx(filename, ["change_address", "multi_input"])

    test_heuristic(txs, ReusedAddressChange)
    test_heuristic(txs, AddressTypeChange)

    
    