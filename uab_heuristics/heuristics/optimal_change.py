from ..core.base_heuristic import Heuristic

class OptimalChange(Heuristic):
    """
    Heurisitic that detects change address by checking that any input has higher amount than any output, meaning that are all needed
    """
    __complexity__ = "low"
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(self, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.input_count > 1, f"The tx {tx.txid} must contain at min 2 inputs"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"

        tx.import_previous_txs()

        #we start extracting the potential change address, following the min output rule
        potential_change_value = min(tx.outputs_values)

        potential_change_addr = []
        for out_value, out_addr in zip(tx.outputs_values, tx.outputs_addresses):
            if out_value == potential_change_value:
                potential_change_addr.append(out_addr)

        if len(potential_change_addr) > 1:
            return {
                    "result" : False,
                    "address" : []
                }

        #if we find any input smaller than the min output, we can not extract the change
        for input_value in tx.inputs_values:
            if potential_change_value > input_value:
                return {
                    "result" : False,
                    "address" : []
                }
        return {
                "result" : True,
                "address" : potential_change_addr
            }