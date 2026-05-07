_DATA_FETCHER = None
_BLOCK_HEIGHT_CACHE = {}
_BATCH_SIZE = 25
_MAX_RETRIES = 5


def _get_data_fetcher():
    global _DATA_FETCHER
    if _DATA_FETCHER is None:
        from ..core import BitcoinDataFetcher

        _DATA_FETCHER = BitcoinDataFetcher(sources=["rpc", "external_sources"])
    return _DATA_FETCHER


def prime_block_height_cache(txids):
    """Preload block metadata for txids in the current process using chunked batch RPC calls."""
    unique_txids = [txid for txid in set(txids) if txid not in _BLOCK_HEIGHT_CACHE]
    if not unique_txids:
        return

    fetcher = _get_data_fetcher()
    for i in range(0, len(unique_txids), _BATCH_SIZE):
        pending = unique_txids[i:i + _BATCH_SIZE]

        for _ in range(_MAX_RETRIES):
            if not pending:
                break

            try:
                if hasattr(fetcher, "get_blocks_from_txids"):
                    batch_results = fetcher.get_blocks_from_txids(pending)
                    _BLOCK_HEIGHT_CACHE.update(batch_results)
                    pending = [txid for txid in pending if txid not in batch_results]
                    continue
            except Exception:
                pass

            remaining = []
            for txid in pending:
                try:
                    _BLOCK_HEIGHT_CACHE[txid] = fetcher.get_block_from_txid(txid=txid)
                except Exception as e:
                    remaining.append(txid)
                    print(f"Get_block_from_txid failed for {txid}: {e}")
            pending = remaining

        if pending:
            print(f"Get_block_from_txid gave up on {len(pending)} txids after {_MAX_RETRIES} retries")


def get_block_from_txid(txid):
    cached = _BLOCK_HEIGHT_CACHE.get(txid)
    if cached is not None:
        return cached

    try:
        result = _get_data_fetcher().get_block_from_txid(txid=txid)
        _BLOCK_HEIGHT_CACHE[txid] = result
        return result
    except Exception as e:
        print(f"Get_block_from_txid failed {e}")