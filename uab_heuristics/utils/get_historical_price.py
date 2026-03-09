import json
from ..api import make_request

def get_historical_price(timestamp, currency):
    templates = ["https://mempool.space/api/v1/historical-price?currency={0}&timestamp={1}"]
    tries = 5
    for _ in range(tries):
        try:
            prices =  make_request((currency, timestamp), templates)
            prices = json.loads(prices)
            return prices["prices"][0][currency]
        except Exception as e:
            print(f"Request failed, trying again...")
    return None