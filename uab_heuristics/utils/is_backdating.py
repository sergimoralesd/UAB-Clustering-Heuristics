from .get_block_from_txid import get_block_from_txid


LOCKTIME_THRESHOLD = 500000000


def is_backdating(tx):
    tx_locktime = tx.locktime
    tx_uses_block_height = tx_locktime < LOCKTIME_THRESHOLD

    for prev_tx in tx.previous_txs:
        prev_locktime = prev_tx.locktime
        prev_uses_block_height = prev_locktime < LOCKTIME_THRESHOLD

        if tx_uses_block_height != prev_uses_block_height:
            continue

        if tx_locktime < prev_locktime:
            return True

    if not tx_uses_block_height:
        return False

    block_height = get_block_from_txid(tx.txid)["block_height"]

    return tx_locktime >= block_height - 100 and tx_locktime < block_height