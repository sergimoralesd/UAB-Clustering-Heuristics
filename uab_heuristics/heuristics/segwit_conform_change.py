from ..core.base_heuristic import Heuristic

class SegwitConformChange(Heuristic):
    """
    Heurisitic that detects change address by checking if the tx is segwit serialized
    """
    __complexity__ = "medium-high"
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(self, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert tx.future_txs != None, f"The tx {tx.txid} must contain future tx associated"

        tx.import_previous_txs()
        
        for future_tx in tx.future_txs:
            if future_tx is not None:
                future_tx.import_previous_txs()

        actual_segwit_conform = tx.is_segwit_conform
        future_segwit_conform = [
            future_tx.is_segwit_conform if future_tx is not None else None 
            for future_tx in tx.future_txs
        ]

        change = [addr for addr, future_segwit in zip(tx.outputs_addresses, future_segwit_conform) if actual_segwit_conform == future_segwit]
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