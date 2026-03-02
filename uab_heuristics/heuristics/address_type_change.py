from .base import Heuristic

class AddressTypeChange(Heuristic):
    """
    Heurisitic that detects change address by using same address type in inputs and outputs
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"

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