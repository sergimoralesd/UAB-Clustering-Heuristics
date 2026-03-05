from pathlib import Path

from uab_heuristics.core import Tx
from uab_heuristics.heuristics import *
from uab_heuristics.utils import get_collection_tx

BASE_DIR = Path(__file__).resolve().parent


def test_heuristic(txs, heuristic_cls, prev_tx=False, future_txs=False):
    print("#" * 50)
    if isinstance(heuristic_cls, type):
        heuristic = heuristic_cls()
    else:
        heuristic = heuristic_cls
    print(f"Starting test with heuristic: {heuristic.name}")

    for tx in txs:
        tx_id = tx["tx_id"]
        tx_raw = tx["tx_raw"]
        try:
            print(f"Applying heuristic to tx: \n{tx_id}")
            tx_object = Tx.from_raw(tx_raw)
            if future_txs:
                tx_object.import_future_txs(tx["future_txs"])
                
            #print(f"Input addrecess: \n{tx_object.inputs_addresses}")
            #print(f"Output addrecess: \n{tx_object.outputs_addresses}")
            result_reused_addr_change = heuristic.apply(tx_object)
            print(f"Result from heurisitc: \n{result_reused_addr_change}")
        except Exception as e:
            print(e)
        print("-"*50)
    print("#" * 50)

if __name__ == "__main__":

    filename = BASE_DIR / "data" / "tx_collection.json"
    txs = get_collection_tx(filename, ["change_address"])
    txs_coinjoin = get_collection_tx(filename, ["coinjoin"])

    #test_heuristic(txs, ReusedAddressChange)
    
    #test_heuristic(txs, AddressTypeChange)

    for n in range(2, 8):
        print(f"-- N:{n} --")
        rounded_change = RoundedChange(n)
        test_heuristic(txs, rounded_change)

    test_heuristic(txs, SmallerChange)

    test_heuristic(txs, OptimalChange)

    test_heuristic(txs, InputOrderChange, future_txs=True)
    
    test_heuristic(txs, OutputOrderChange, future_txs=True)

    test_heuristic(txs, LocktimeChange, future_txs=True)

    test_heuristic(txs, FeeAbsoluteChange, future_txs=True)

    test_heuristic(txs, FeeRelativeChange, future_txs=True)

    test_heuristic(txs, VersionChange, future_txs=True)

    test_heuristic(txs, SignalRBFChange, future_txs=True)

    test_heuristic(txs, ConsistentAddressTypeChange, future_txs=True)

    test_heuristic(txs, ZeroConfirmationChange, future_txs=True) 
    
    test_heuristic(txs, LowRChange, future_txs=True)  

    test_heuristic(txs, MultiSignatureChange, future_txs=True)

    test_heuristic(txs_coinjoin, EqualOutputCoinjoinChange)
