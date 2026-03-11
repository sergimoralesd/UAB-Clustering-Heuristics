import requests
import json
from ..core.base_adapter import BaseAdapter
from ..core.exceptions import FetchError, NotFoundError

class _ExternaSourcesAdapter(BaseAdapter):
    name = "external_sources"
    
    def _call(self, *params, templates: list) -> str:
        """Try each URL template in order, return first success."""

        for template in templates:
            url = template.format(*params)
            try:
                r = requests.get(url, timeout=5)
                r.raise_for_status()
                res = r.text.strip()
                if not res:
                    raise NotFoundError(f"Empty response from {url}")
                return res
            except Exception as exc:
                continue

        raise FetchError("All templates failed")
        

    def get_raw_from_txid(self, txid: str) -> str:
        templates = ["https://mempool.space/api/tx/{0}/hex", "https://blockchain.info/rawtx/{0}?format=hex"]
        return self._call(txid, templates=templates)
    
    def get_block_from_txid(self, txid) -> dict:
        templates = ["https://mempool.space/api/tx/{0}", "https://blockchain.info/rawtx/{0}"]
        block = self._call(txid, templates=templates)
        if isinstance(block, str):
            block = json.loads(block)
        if "status" in block:
            return {
                "block_height": block["status"].get("block_height"),
                "block_hash": block["status"].get("block_hash"),
                "block_time": block["status"].get("block_time")
            }
        
        return {
            "block_height": block.get("block_height"),
            "block_hash": block.get("block_hash"),
            "block_time": block.get("block_time")
        }
    
    def get_historical_price(self, timestamp, currency) -> int:
        templates = ["https://mempool.space/api/v1/historical-price?currency={0}&timestamp={1}"]
        prices =  self._call(currency, timestamp, templates=templates)
        prices = json.loads(prices)
        return prices["prices"][0][currency]
    
    def get_txs_by_addr(self, addr) -> dict:
        templates = ["https://mempool.space/api/address/{0}/txs/chain"]
        txs =  self._call(addr, templates=templates)
        txs = json.loads(txs)
        return txs