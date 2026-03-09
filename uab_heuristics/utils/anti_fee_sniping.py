from .get_block_from_txid import get_block_from_txid

def anti_fee_sniping(tx):
    if tx.locktime == 0:
        return 0
    block_height = get_block_from_txid(tx.txid)["block_height"]
    if block_height - tx.locktime >= 100:
        return 1
    return 2