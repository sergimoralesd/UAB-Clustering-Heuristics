from .base import Heuristic

class FeeAbsoluteChange(Heuristic):
    """
    Heurisitic that detects change address by using the absolute payed by the tx
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        assert tx != None
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert tx.future_txs != None, f"The tx {tx.txid} must contain future tx associated"

        tx.import_previous_txs()

        for future_tx in tx.future_txs:
            if future_tx is not None:
                future_tx.import_previous_txs()

        #check the absolute fee of the spending txs, if we find correlation between them, it may imply is the same user
        absolute_fee_future_txs = [
            future_tx.absolute_fee if future_tx is not None else None
            for future_tx in tx.future_txs
        ]

        indexes = [i for i, order in enumerate(absolute_fee_future_txs) if order == tx.absolute_fee]
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