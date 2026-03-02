from .base import Heuristic

class ConsistentAddressTypeChange(Heuristic):
    """
    Heurisitic that detects change address by using same address type in all inputs and in outputs
    It differs with the other because this heuristic checks all inputs' types are the same
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"

        #more than one type could mena more than one user
        if len(set(tx.inputs_types)) > 2:
            return {
                "result" : False,
                "address" : []
            }

        change = [addr for addr, addr_type in zip(tx.output_addresses, tx.outputs_types) if addr_type in tx.inputs_types]

        if len(change) == 1:
            return {
                "result" : True,
                "address" : change
            }
        return {
                "result" : False,
                "address" : []
            }