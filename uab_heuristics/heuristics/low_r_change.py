from ..core.base_heuristic import Heuristic
from ..utils import low_r_only

class LowRChange(Heuristic):
    """
    Heurisitic that detects change address by using the low R value from the signature
    """
    __complexity__ = "medium-low"
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert tx.future_txs != None, f"The tx {tx.txid} must contain future tx associated"

        low_r = low_r_only(tx)

        low_r_future_txs = [
            low_r_only(future_tx) if future_tx is not None else None
            for future_tx in tx.future_txs
        ]

        change = [addr for addr, low_r_future in zip(tx.outputs_addresses, low_r_future_txs) if low_r == low_r_future]
        #if we find one coincidence, we can extract the change
        if len(change) == 1:
            return {
                "result" : True,
                "address" : change
            }
        #we find either none or more than one coincidence, so we can not extract the change
        return  {
            "result" : False,
            "address" : []
        }