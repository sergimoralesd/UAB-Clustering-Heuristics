from ..core.base_heuristic import Heuristic

class RoundedChange(Heuristic):
    """
    Heurisitic that detects change address by checking if exists any rounded value
    """
    __complexity__ = "none"
    

    @classmethod
    def apply(self, tx=None, n=None):
        if tx is None:
            raise ValueError("Specify a transaction")
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert n != None, f"The precision parameter can not be empty"

        #transform satoshis to btcs
        precision = 10 ** (8 - n)
        change = [addr for addr, amount in zip(tx.outputs_addresses, tx.outputs_values) if amount % precision != 0]

        if len(change) == 1:
            return {
                "result" : True,
                "address" : change
            }
        return {
                "result" : False,
                "address" : []
            }