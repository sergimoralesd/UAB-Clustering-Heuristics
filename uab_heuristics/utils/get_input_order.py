from binascii import unhexlify
from .get_block_height_from_txid import get_block_height_from_txid 

def get_input_order(tx):
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
    
    aux = []
    for p in tx.prevouts:
        txid_hex, vout_str = p.split(":")
        aux.append((unhexlify(txid_hex), int(vout_str)))

    sorted_prevouts_bin = sorted(aux, key=lambda x: (x[0], x[1]))
    sorted_prevouts_hex = [f"{txid.hex()}:{vout}" for txid, vout in sorted_prevouts_bin]
    if sorted_prevouts_hex == tx.prevouts:
        return 3
    
    blocks = [get_block_height_from_txid(txid=prev_txid) for prev_txid in tx.previous_txid]
    if sorted(blocks) == blocks:
        return 4
    return 5