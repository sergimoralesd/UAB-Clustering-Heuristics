def get_block_from_txid(txid):
    from ..core import BitcoinDataFetcher
    data_fetcher = BitcoinDataFetcher()
    try:
        return data_fetcher.get_block_from_txid(txid=txid)
    except Exception as e:
        print(f"Get_block_from_txid failed {e}")