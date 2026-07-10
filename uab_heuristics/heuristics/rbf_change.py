from ..core.base_heuristic import Heuristic
from ..utils import same_output, different_output

class RBFChange(Heuristic):
    """
    Heurisitic that detects change by comparing it with the replacement with the same number of outputs
    """
    __complexity__ = "high"
    
    @classmethod
    def apply(cls, tx=None):
        if tx is None:
            raise ValueError("Specify a transaction")
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert tx.replacement != None, f"The tx {tx.txid} must contain the replacement transaction"

        values = [tx.outputs_values, tx.replacement.outputs_values]
        addresses = [tx.outputs_addresses, tx.replacement.outputs_addresses]

        if len({len(value) for value in values}) == 1:
            # Function for replacements with the same number of outputs
            succes, address = same_output(values, addresses)
            
        else:
            # Function for replacements with different number of outputs (less relaiable)
            succes, address = different_output(values, addresses)

        if succes:
                return {
                    "result" : True,
                    "address" : address
                }

        return  {
            "result" : False,
            "address" : []
        }
        

