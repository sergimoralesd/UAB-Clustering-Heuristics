def get_historical_price(timestamp, currency):
    from ..core import BitcoinDataFetcher
    data_fetcher = BitcoinDataFetcher(sources=["external_sources"])
    try:
        return data_fetcher.get_historical_price(timestamp=timestamp, currency=currency)
    except Exception as e:
        print(f"Get_historical_price failed")