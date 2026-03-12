def get_raw_tx_from_id(txid):
    from ..core import BitcoinDataFetcher
    data_fetcher = BitcoinDataFetcher()
    try:
        return (bytes.fromhex(data_fetcher.get_raw_from_txid(txid=txid)))
    except Exception as e:
        print(f"Get_raw_tx_from_id failed")