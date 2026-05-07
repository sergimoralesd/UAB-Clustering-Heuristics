from ..api import _RPCAdapter, _ExternaSourcesAdapter, _BlocksciAdapter, _LocalSources
from .exceptions import NotFoundError, FetchError, ConfigurationError

SOURCES = {
    "local_sources" : _LocalSources,
    "blocksci" : _BlocksciAdapter,
    "rpc": _RPCAdapter,
    "external_sources": _ExternaSourcesAdapter
}

class BitcoinDataFetcher:
    """
    Unified fetcher for Bitcoin data.

    Parameters
    ----------
    source : str
        Any source from SOURCE list, it can be one or more.
        if "all" is selected, the class will try any source available, from fastest to slowest
    """

    def __init__(self, sources: list[str] = ["all"]):
        self.adapters = []

        if "all" in sources:
            for cls in SOURCES.values():
                try:
                    self.adapters.append(cls())
                except Exception as e:
                    continue
        else:
            unknown = set(sources) - SOURCES.keys()
            if unknown:
                raise ValueError(f"Unknown sources: {unknown}. Choose from: {list(SOURCES)}")
            for s in sources:
                try:
                    self.adapters.append(SOURCES[s]())
                except:
                    continue 
            
    
    def _run(self, method: str, *args):
        """
        Try the selected adapters, returns the first successful result.
        """
        
        for adapter in self.adapters:
                try:
                    result = getattr(adapter, method)(*args)
                    return result
                except NotFoundError:
                    raise
                except (FetchError, NotImplementedError, ImportError):
                    #try next one
                    continue

        raise FetchError("All sources failed")
    
    def get_raw_from_txid(self, txid: str) -> str:
        return self._run("get_raw_from_txid", txid)

    def get_historical_price(self, timestamp: int, currency: str) -> int:
        return self._run("get_historical_price", timestamp, currency)
    
    def get_txs_by_addr(self, addr: str) -> dict:
        return self._run("get_txs_by_addr", addr)
    
    def get_block_from_txid(self, txid: str) -> dict:
        return self._run("get_block_from_txid", txid)

    def get_blocks_from_txids(self, txids: list) -> dict:
        for adapter in self.adapters:
            if not hasattr(adapter, "get_blocks_from_txids"):
                continue
            try:
                return adapter.get_blocks_from_txids(txids)
            except (FetchError, NotImplementedError, ImportError):
                continue

        raise FetchError("All sources failed")
    