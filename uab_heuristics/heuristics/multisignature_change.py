from ..core.base_heuristic import Heuristic
from ..utils import get_multisignature_script_type

class MultiSignatureChange(Heuristic):
    """
    Heurisitic that detects change address by checking if any input and output is a multisignature, a very unique script
    """
    __complexity__ = "none" #to be determined
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        assert tx != None, f"Specify a transaction"
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert tx.future_txs != None, f"The tx {tx.txid} must contain future tx associated"

        tx.import_previous_txs()

        multisignature_type = get_multisignature_script_type(tx)
        if len(multisignature_type) != 1:
            return  {
                "result" : False,
                "address" : []
            }
        multisignature_type = multisignature_type[0]

        future_tx_multisignature_type = [
            get_multisignature_script_type(future_tx) if future_tx is not None else None
            for future_tx in tx.future_txs
        ]

        change = []
        for addr, ms_type in zip(tx.outputs_addresses, future_tx_multisignature_type):
            if len(ms_type) != 1:
                continue
            if multisignature_type == ms_type[0]:
                change.append(addr)
        
        #if we find one coincidence, we can extract the change
        if len(change) == 1:
            return {
                "result" : True,
                "address" : change
            }
        #we find either none or more than one coincidence, so we can not extract the change
        return  {
            "result" : False,
            "address" : []
        }