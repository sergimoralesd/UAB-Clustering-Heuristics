from ..core import Tx
from ..utils import get_block_height_from_txid 

def get_input_order(tx: Tx):
    """
    Return ordering type of inputs of a transaction

    0 -> single input
    1 -> ascending order
    2 -> descending order
    3 -> BIP69 order
    4 -> historical
    5 -> undetermined

    """
    if tx.input_count == 1:
        return 0
    
    if sorted(tx.inputs_values) == tx.inputs_values:
        return 1
    
    if sorted(tx.inputs_values)[::-1] == tx.inputs_values:
        return 2
    
    if sorted(tx.prevouts) == tx.prevouts:
        return 3
    
    blocks = [get_block_height_from_txid(txid=prev_txid) for prev_txid in tx.previous_txid]
    if sorted(blocks) == blocks:
        return 4
    return 5