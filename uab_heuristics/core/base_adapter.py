class BaseAdapter:
    name: str = ""

    def get_raw_from_txid(self, txid: str) -> str:
        raise NotImplementedError(f"'{self.name}' does not support get_raw_from_txid")

    def get_historical_price(self, timestamp: int, currency: str) -> int:
        raise NotImplementedError(f"'{self.name}' does not support get_historical_price")
    
    def get_txs_by_addr(self, addr: str) -> dict:
        raise NotImplementedError(f"'{self.name}' does not support get_txs_by_addr")

    def get_block_from_txid(self, txid: str) -> dict:
        raise NotImplementedError(f"'{self.name}' does not support get_raget_block_from_txidw_tx")
        