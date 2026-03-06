# Source: Heuristic-Based_Address_Clustering_in_Bitcoin
from .base import Heuristic
from ..utils import get_txs_by_address, get_block_height_from_txid 

class FutureAddressReuse(Heuristic):
    """
    Heurisitic that detects change address by checking if any output is the first time it appears and is never used again and the rest of them are reused later on
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined


    def apply(self, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"

        total_blocks_heights = []
        for out_addr in tx.outputs_addresses:
            all_txs_from_address = get_txs_by_address(out_addr)
            blocks_heights = []
            for tx_from_addr in all_txs_from_address:
                #to avoid computing the same tx we are using evaluating
                if tx_from_addr["txid"] != tx.txid:
                    blocks_heights.append(tx_from_addr["status"]["block_height"])
            total_blocks_heights.append(sorted(blocks_heights))

        #if we dont find any tx, means it is never used before and after.
        change = [out_addr for out_addr, blocks_heights in zip(tx.outputs_addresses, total_blocks_heights) if len(blocks_heights) == 0]
            
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