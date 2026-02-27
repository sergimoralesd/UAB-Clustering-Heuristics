from .get_block_height_from_txid import get_block_height_from_txid

def anti_fee_sniping(tx):
    if tx.locktime == 0:
        return 0
    block_heihgt = get_block_height_from_txid(tx.txid)
    if block_heihgt - tx.locktime >= 100:
        return 1
    return 2