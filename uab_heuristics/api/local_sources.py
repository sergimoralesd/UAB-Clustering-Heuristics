from dotenv import load_dotenv
import os
import plyvel

from ..core.base_adapter import BaseAdapter
from ..core.exceptions import NotFoundError, ConfigurationError

class _LocalSources(BaseAdapter):
    #the idea behind is that we have a leveldb with the raw_hex for each txid
    name = "local_sources"

    def __init__(self):
        load_dotenv()

        leveldb_path = os.getenv("LEVELDB_PATH")

        if not leveldb_path:
            raise ConfigurationError("Missing DB config in .env file")
        
        self._ldb = plyvel.DB(leveldb_path, create_if_missing=False)
    
    def close(self):
        self._ldb.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def get_raw_from_txid(self, txid: str) -> str:
        raw = self._ldb.get(txid.encode())
    
        if raw is None:
            raise NotFoundError(f"txid not found in local LevelDB: {txid}")
    
        return raw.hex()