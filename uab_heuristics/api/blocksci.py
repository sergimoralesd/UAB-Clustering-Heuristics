import os
from dotenv import load_dotenv
from ..core.exceptions import FetchError, ConfigurationError
from ..core.base_adapter import BaseAdapter

try:
    import blocksci
    BLOCKSCI_AVAILABLE = True
except ImportError:
    BLOCKSCI_AVAILABLE = False

class _BlocksciAdapter(BaseAdapter):
    name = "blocksci"
    def __init__(self):
        if not BLOCKSCI_AVAILABLE:
            raise ImportError("blocksci is not installed.")
        load_dotenv()
        blocksci_path = os.getenv("BLOCKSCI_PATH")
        if not blocksci_path:
            raise ConfigurationError("Missing BlockSci config in .env file")
        self.chain = blocksci.Blockchain(blocksci_path)
    
    def get_block_from_txid(self, txid: str) -> dict:
        try:
            block = self.chain.tx_with_hash(txid).block
        except Exception as exc:
            raise FetchError(f"txid not found in BlockSci: {txid}") from exc
        return {
                "block_height": block.height,
                "block_hash": block.hash,
                "block_time": block.timestamp
            }

    
    def get_txs_by_addr(self, addr: str) -> dict:
        #disclaimer!
        #blocksci only works until block 676078, meaning that some addresses taht have been used after that won't show all the information
        addr = self.chain.address_from_string(addr)
        if addr is None:
            raise FetchError(f"addr not found in BlockSci: {addr}")
        
        txs = [tx.hash for tx in addr.input_txes] + [tx.hash for tx in addr.output_txes]
        return txs



        