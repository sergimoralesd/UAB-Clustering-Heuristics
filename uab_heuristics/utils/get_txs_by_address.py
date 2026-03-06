import json
from ..api import make_request

def get_txs_by_address(addr):
    templates = ["https://mempool.space/api/address/{0}/txs/chain"]
    tries = 5
    for _ in range(tries):
        try:
            txs =  make_request(addr, templates)
            txs = json.loads(txs)
            return txs
        except Exception as e:
            print(f"Request failed, trying again...")
    return None

