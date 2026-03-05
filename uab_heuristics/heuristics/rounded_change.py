from .base import Heuristic

class RoundedChange(Heuristic):
    """
    Heurisitic that detects change address by checking if exists any rounded value
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined

    def __init__(self, n):
        self.n = n


    def apply(self, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"

        #transform satoshis to btcs
        precision = 10 ** (8 - self.n)
        change = [addr for addr, amount in zip(tx.outputs_addresses, tx.outputs_values) if amount % precision == 0]

        if len(change) == 1:
            return {
                "result" : True,
                "address" : change
            }
        return {
                "result" : False,
                "address" : []
            }