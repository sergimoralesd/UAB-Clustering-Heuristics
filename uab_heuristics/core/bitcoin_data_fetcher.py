from ..api.bitcoin_rpc import _RPCAdapter
from ..api.external_sources import _ExternaSourcesAdapter
from ..api.blocksci import _BlocksciAdapter
from ..api.local_sources import _LocalSources
from .exceptions import NotFoundError, FetchError

SOURCES = {
    "rpc": _RPCAdapter,
    "external_sources": _ExternaSourcesAdapter,
    "blocksci" : _BlocksciAdapter,
    "local_sources" : _LocalSources
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
        source = source.lower()

        self.adapters = []

        if "all" in sources:
            self.adapters = list(SOURCES.values())
        else:
            unknown = set(sources) - SOURCES.keys()
            if unknown:
                raise ValueError(f"Unknown sources: {unknown}. Choose from: {list(SOURCES)}")
            self.adapters = [SOURCES[s] for s in sources]
            
    
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
                except (FetchError, NotImplementedError):
                    #try next one
                    continue

        raise FetchError("All sources failed")
    
    def get_raw_from_txid(self, txid: str) -> str:
        return self._run("get_raw_tx", txid)

    def get_historical_price(self, timestamp: int, currency: str) -> int:
        return self._run("get_historical_price", timestamp, currency)
    
    def get_txs_by_addr(self, addr: str) -> dict:
        return self._run("get_txs_by_addr", addr)
    
    def get_block_from_txid(self, txid: str) -> dict:
        return self._run("get_block_from_txid", txid)

            
        