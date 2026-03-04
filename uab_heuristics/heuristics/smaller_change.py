from .base import Heuristic

class SmallerChange(Heuristic):
    """
    Heurisitic that detects change address by checking if one output is smaller than the other
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined


    def apply(self, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"

        min_value = min(tx.outputs_values)
        candidates = [addr for addr, v in zip(tx.outputs_addresses, tx.outputs_values) if v == min_value]
        
        if len(candidates) == 1:
            return {
                "result" : True,
                "address" : candidates
            }
        return {
                "result" : False,
                "address" : []
            }