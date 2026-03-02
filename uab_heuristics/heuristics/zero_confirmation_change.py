from .base import Heuristic
from ..utils import get_block_height_from_txid

class ZeroConfirmationChange(Heuristic):
    """
    Heurisitic that detects change address by checking the waited time to spend the outputs, if it is less than 6 blocks(avoid double spend), may imply the user is spending change
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert tx.future_txs != None, f"The tx {tx.txid} must contain future tx associated"
        
        actual_block_height = get_block_height_from_txid(tx.txid)

        #check the block height of the spending txs, if we find any in less than 6 blocks, it may imply is the same user spending the change
        block_heights_future_txs = [
            get_block_height_from_txid(future_tx.txid) if future_tx is not None else None
            for future_tx in tx.future_txs
        ]
        
        indexes = [i for i, future_block_height in enumerate(block_heights_future_txs) if future_block_height != None and future_block_height - actual_block_height < 6]
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