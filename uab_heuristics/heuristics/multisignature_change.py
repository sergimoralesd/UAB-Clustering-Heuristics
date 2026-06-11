from ..core.base_heuristic import Heuristic
from ..utils import get_multisignature_script_type

class MultiSignatureChange(Heuristic):
    """
    Heurisitic that detects change address by checking if any input and output is a multisignature, a very unique script
    """
    __complexity__ = "medium-low"
    

    @classmethod
    def apply(cls, tx=None):
        if tx is None:
            raise ValueError("Specify a transaction")
        assert tx.output_count == 2, f"The tx {tx.txid} must contain 2 outputs"
        assert tx.future_txs != None, f"The tx {tx.txid} must contain future tx associated"

        multisignature_type = get_multisignature_script_type(tx)
        if len(multisignature_type) != 1:
            return  {
                "result" : False,
                "address" : []
            }
        multisignature_type = multisignature_type[0]
        change = []
        for vout_index, (addr, future_tx) in enumerate(zip(tx.outputs_addresses, tx.future_txs)):
            # unspent output
            if future_tx is None:
                continue

            # find the input index in future_tx that spends this exact output
            spending_input_index = None
            for i in range(future_tx.input_count):
                if future_tx.previous_txid[i] != tx.txid:
                    continue
                if future_tx._tx.vin[i].prevout.n != vout_index:
                    continue
                spending_input_index = i
                break

            if spending_input_index is None:
                continue

            ms_type = get_multisignature_script_type(future_tx, input_index=spending_input_index)
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