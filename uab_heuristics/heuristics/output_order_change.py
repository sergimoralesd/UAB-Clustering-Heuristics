from .base import Heuristic
from ..utils import get_output_order

class OutputOrderChange(Heuristic):
    """
    Heurisitic that detects change address by using the input order of the tx and the tx spending the outputs
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        assert tx != None
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert tx.future_txs != None, f"The tx {tx.txid} must contain future tx associated"

        inputs_order = get_output_order(tx)

        #check the output order of the spending tx, if we find correlation between them, it may imply is the same user
        outputs_order = [
            get_output_order(future_tx) if future_tx is not None else None
            for future_tx in tx.future_txs
        ]

        indexes = [i for i, order in enumerate(outputs_order) if order == inputs_order]
        #if we find one coincidence, we can extract the change
        if len(indexes) == 1:
            return {
                "result" : True,
                "address" : [tx.output_addresses[indexes[0]]]
            }
        #ee find either none or more than one coincidence, so we can not extract the change
        return  {
            "result" : False,
            "address" : []
        }