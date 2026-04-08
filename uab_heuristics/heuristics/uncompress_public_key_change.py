from ..core.base_heuristic import Heuristic
from ..utils import has_uncompress_public_keys

class UncompressPublicKeyChange(Heuristic):
    """
    Heurisitic that detects change address by checking if the public keys are compress or uncompress.
    """
    __complexity__ = "medium-high"
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert tx.future_txs != None, f"The tx {tx.txid} must contain future tx associated"

        tx.import_previous_txs()

        for future_tx in tx.future_txs:
            if future_tx is not None:
                future_tx.import_previous_txs()

        has_uncompressed_public_keys = has_uncompress_public_keys(tx)

        #check the if the the spending txs are marked by RBF, if we find correlation between them, it may imply is the same user
        uncompressed_public_keys_future_txs = [
            has_uncompress_public_keys(future_tx) if future_tx is not None else None
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