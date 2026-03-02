from .base import Heuristic
from ..utils import anti_fee_sniping

class LocktimeChange(Heuristic):
    """
    Heurisitic that detects change address by using the locktime field, checking if the speding tx have the same configuration
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert tx.future_txs != None, f"The tx {tx.txid} must contain future tx associated"

        locktime_configuration = anti_fee_sniping(tx)
        locktime_spending_configuration = [
            anti_fee_sniping(future_tx) if future_tx is not None else None 
            for future_tx in tx.future_txs
            ]

        indexes = [i for i, locktime in enumerate(locktime_spending_configuration) if locktime == locktime_configuration]
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