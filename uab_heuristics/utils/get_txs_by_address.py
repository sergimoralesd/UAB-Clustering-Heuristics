def get_txs_by_address(addr):
    from ..core import BitcoinDataFetcher
    data_fetcher = BitcoinDataFetcher()
    try:
        return data_fetcher.get_txs_by_addr(addr=addr)
    except Exception as e:
        print(f"Get_txs_by_address failed")