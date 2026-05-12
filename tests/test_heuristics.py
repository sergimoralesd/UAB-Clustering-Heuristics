from pathlib import Path

try:
    from rust_tx_core import Tx
except ImportError as e:
    print("Error")
    from uab_heuristics.core import Tx
from uab_heuristics.heuristics import *
from uab_heuristics.utils import get_collection_tx

BASE_DIR = Path(__file__).resolve().parent


def test_heuristic(txs, heuristic_cls, prev_tx=False, future_txs=False, currency=None, n=None):
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
            if prev_tx:
                tx_object.import_previous_txs()
            if future_txs:
                tx_object.import_future_txs(future_txids=tx["future_txs"])
            
            if n and currency:
                result_reused_addr_change = heuristic.apply(tx_object, n=n, currency=currency)
            elif n:
                result_reused_addr_change = heuristic.apply(tx_object, n=n)
            else:
                result_reused_addr_change = heuristic.apply(tx_object)
            if result_reused_addr_change['result'] == True:
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

    #for n in range(2, 8):
    #    print(f"-- N:{n} --")
    #    test_heuristic(txs, RoundedChange, n=n)

    #test_heuristic(txs, SmallerOutputChange)

    #test_heuristic(txs, OptimalChange)

    tx = {
        "tx_id" : "8eabad99fe4607a1f4a7e2979d34e0c8cad0a36e41d8e68061457fbc535bbfeb",
        "tx_raw" : "0100000002aea7dfe9cfbe2d28ac53dc8ac2f6ea77b6f2e0397de01277234ac6be6150a431080000006a473044022028bbc2a4e6ba6f0bbbcceb8e9629e5464031145ad13aa4b0dbb84321a429e0e802206c4981d412a1671ddc35dc5b0b70c4b2b7a43bd6641ebf22f7b6828643962c6401210255c741304a8cf6a4a64cd49f27db5cfee89eb671a5ae2661a4c5aa8f87afab2cffffffff93268f6a52bf8e521f47a8c574bc93798a11a7467447b7ddc70ee02a665ee2d9010000006a473044022005ab6e4cffa7fce1b6a193b170f84bdb16c3eadd120b1ad6efa88ca59f935d5d02207c40a5f6034a1b05aabadece6a47dfb70084d8ac0bb2bebb74a8c860372dffe8012102662eff4ced7133015a6fc1322aed949317756eb737b6857fd18778c8766bac33ffffffff0201672100000000001976a9145a4299fd379988a5f066aa35b3e7e54a0285d1ad88ac00a7e103000000001976a91425d31aa80e2a991034f4066f12900c4a6ce56c8988ac00000000",
        "future_txs" : ["9aa9e5917c29d739c8f8c7c8c1580fdc7a2b701dcb756eb3b80bdc84bab69977", "1e53ae0cc698954d1036b2491c2f193be115194a1a34bc194a841bf6504874c5"]
    }
    txs = [tx]
    test_heuristic(txs, InputOrderChange, future_txs=True)
    
    #test_heuristic(txs, OutputOrderChange, future_txs=True)

    #test_heuristic(txs, LocktimeChange, future_txs=True)

    #test_heuristic(txs, FeeAbsoluteChange, future_txs=True)

    #test_heuristic(txs, FeeRelativeChange, future_txs=True)

    #test_heuristic(txs, VersionChange, future_txs=True)

    #test_heuristic(txs, SignalRBFChange, future_txs=True)

    #test_heuristic(txs, ConsistentAddressTypeChange, future_txs=True)

    #test_heuristic(txs, ZeroConfirmationChange, future_txs=True) 
    
    #test_heuristic(txs, LowRChange, future_txs=True)  

    #test_heuristic(txs, MultiSignatureChange, future_txs=True)

    #test_heuristic(txs_coinjoin, EqualOutputCoinjoinChange)

    #test_heuristic(txs, OneTimeChange)
    
    #test_heuristic(txs, FutureAddressReuse)

    #test_heuristic(txs, SegwitConformChange, future_txs=True)
    
    currencies = ['USD', 'EUR', 'GBP', 'CAD', 'CHF', 'AUD', 'JPY']
    
    #for currency in currencies:
    #    print(f"-- Currency:{currency} --")
    #    for n in range(2, 8):
    #        print(f"-- N:{n} --")
    #        test_heuristic(txs, RoundedFiatChange, currency=currency, n=n)

    #test_heuristic(txs, UncompressPublicKeyChange, prev_tx=True, future_txs=True)

    #test_heuristic(txs, BackdatingChange, prev_tx=True, future_txs=True)

