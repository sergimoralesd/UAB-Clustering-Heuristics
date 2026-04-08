from .get_block_from_txid import get_block_from_txid

def is_backdating(tx):
    #check for every input
    for prev_tx in tx.previous_txs:
        if tx.locktime < prev_tx.locktime:
            return True

    block_height = get_block_from_txid(tx.txid)["block_height"]
    return tx.locktime >= block_height - 100 and tx.locktime < block_height