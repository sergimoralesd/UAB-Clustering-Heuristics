from .base import Heuristic

class OptimalChange(Heuristic):
    """
    Heurisitic that detects change address by checking that any input has higher amount than any output, meaning that are all needed
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined


    def apply(self, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.input_count > 1, f"The tx {tx.txid} must contain at min 2 inputs"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"

        tx.import_previous_txs()

        for values in tx.inputs_values:
            assert values != 0, f"All inputs from {tx.txid} must containg amount associated"

        #we start extracting the potential change address, following the min output rule
        potential_change_value = min(tx.outputs_values)
        potential_change_addr = tx.outputs_addresses[tx.outputs_values.index(potential_change_value)]

        #if we find any input smaller than the min output, we can not extract the change
        for input_value in tx.inputs_values:
            if potential_change_value > input_value:
                return {
                    "result" : False,
                    "address" : []
                }

        return {
                "result" : True,
                "address" : [potential_change_addr]
            }