from ..core.base_heuristic import Heuristic
from collections import Counter

class EqualOutputCoinjoinChange(Heuristic):
    """
    Heurisitic that detects change address by using the not equal-valued outputs in a coinjoin
    """
    __complexity__ = "low"
    __accuracy__ = 0 #to be determined

    @classmethod
    def apply(cls, tx=None):
        if tx is None:
            raise ValueError("Specify a transaction")
        assert tx.output_count > 1, f"The tx {tx.txid} must containat least 2 outputs"


        tx.import_previous_txs()

        amount_equal_outputs = Counter(tx.outputs_values)

        max_freq = max(amount_equal_outputs.values())
        posible_payment_amount = [v for v, c in amount_equal_outputs.items() if c == max_freq]

        #we can not determine the posible payment amount
        if len(posible_payment_amount) > 1:
            return {
                "result" : False,
                "address" : []
            }  

        tx_fee = tx.absolute_fee
        addr_change = []
        payment_amount = posible_payment_amount[0]
        for in_addr, in_value in zip(tx.inputs_addresses, tx.inputs_values):
            addrs_posible_change = []
            posible_change = in_value - payment_amount
            
            #check for every output the amount to see if it matches the change
            for out_addr, out_amount in zip(tx.outputs_addresses, tx.outputs_values):

                #see if it falls inside the posible change amount taking into account the fees
                if posible_change - tx_fee <= out_amount <= posible_change:
                    addrs_posible_change.append(out_addr)
            
            #check if the posible change is unique
            if len(addrs_posible_change) > 1:
                return {
                    "result" : False,
                    "address" : []
                }
            #there are inputs that may not have any change associated
            if len(addrs_posible_change) < 1:
                continue

            #check if the posible change has been already selected
            if addrs_posible_change[0] in addr_change:
                return {
                    "result" : False,
                    "address" : []
                }
            
            #we are sure that is the only posible change for this input
            addr_change.append((in_addr, addrs_posible_change[0]))

        return {
            "result" : len(addr_change) != 0,
            "address" : addr_change
        }