from ..core.base_heuristic import Heuristic
from ..utils import get_block_from_txid, get_historical_price

class RoundedFiatChange(Heuristic):
    """
    Heurisitic that detects change address by checking if exists any rounded value
    """
    __complexity__ = "high"
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(self, tx=None, n=None, currency=None):
        if tx is None:
            raise ValueError("Specify a transaction")
        if currency is None:
            raise ValueError("The currency can not be empty")
        if n is None:
            raise ValueError("The precision parameter can not be empty")
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        
        block_time = get_block_from_txid(txid=tx.txid)["block_time"]
        price = get_historical_price(block_time, currency)


        precision = 10 ** n
        #transform satoshis to btc, and compute the value in fiat
        change = [addr for addr, amount in zip(tx.outputs_addresses, tx.outputs_values) if (price * (amount/(10**8))) % precision != 0]

        if len(change) == 1:
            return {
                "result" : True,
                "address" : change
            }
        return {
                "result" : False,
                "address" : []
            }