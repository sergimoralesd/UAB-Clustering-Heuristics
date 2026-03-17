from ..core.base_heuristic import Heuristic
from ..utils import get_txs_by_address, get_block_from_txid 

class OneTimeChange(Heuristic):
    """
    Heurisitic that detects change address by checking if any output is the first time it appears
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined

    @classmethod
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

        actual_block_height = get_block_from_txid(tx.txid)["block_height"]

        change = []
        #we look if there is any previous tx where this address appeared, if not we will consider it the change address
        for out_addr, blocks_heights in zip(tx.outputs_addresses, total_blocks_heights):
                #since we have sorted the elements, we can only check the first block height
                #means we found a previous tx where this address was used, so is not new. If we find any equal block height, we also will asume it is not new
                #this first comprovation is to check if we find any other tx rather than the one we are evaluating
                if len(blocks_heights) > 0 and actual_block_height < blocks_heights[0]:
                    change.append(out_addr)

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