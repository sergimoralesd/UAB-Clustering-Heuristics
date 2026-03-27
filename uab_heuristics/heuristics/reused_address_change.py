from ..core.base_heuristic import Heuristic

class ReusedAddressChange(Heuristic):
    """
    Heurisitic that detects change address by reusing input address in outputs
    """
    __complexity__ = "medium-low"
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"

        tx.import_previous_txs()

        reused = [input for input in tx.inputs_addresses if input in tx.outputs_addresses]
        return {
            "result" : len(reused) != 0,
            "address" : reused
        }