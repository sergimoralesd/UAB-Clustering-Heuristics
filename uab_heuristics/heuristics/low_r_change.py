from .base import Heuristic
from ..utils import low_r_only

class LowRChange(Heuristic):
    """
    Heurisitic that detects change address by using the low R value from the signature
    """
    __complexity__ = "none" #to be determined
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

        indexes = [i for i, low_r_future in enumerate(low_r_future_txs) if low_r == low_r_future]
        #if we find one coincidence, we can extract the change
        if len(indexes) == 1:
            return {
                "result" : True,
                "address" : [tx.output_addresses[indexes[0]]]
            }
        #we find either none or more than one coincidence, so we can not extract the change
        return  {
            "result" : False,
            "address" : []
        }