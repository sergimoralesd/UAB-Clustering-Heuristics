from ..core.base_heuristic import Heuristic

class UncompressPublicKeyChange(Heuristic):
    """
    Heurisitic that detects change address by checking if the public keys are compress or uncompress.
    """
    __complexity__ = "medium-high"
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        if tx is None:
            raise ValueError("Specify a transaction")
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert tx.future_txs != None, f"The tx {tx.txid} must contain future tx associated"

        tx.import_previous_txs()

        for future_tx in tx.future_txs:
            if future_tx is not None:
                future_tx.import_previous_txs()

        has_uncompressed_public_keys = tx.has_uncompressed_public_keys
        
        uncompressed_public_keys_future_txs = [
            future_tx.has_uncompressed_public_keys if future_tx is not None else None
            for future_tx in tx.future_txs
        ]

        change = [addr for addr, future_tx in zip(tx.outputs_addresses, uncompressed_public_keys_future_txs) if future_tx == has_uncompressed_public_keys]
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