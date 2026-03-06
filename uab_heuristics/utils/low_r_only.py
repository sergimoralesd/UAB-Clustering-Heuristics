#TODO:
    # implement the low_r detection for the 
        # P2SH-P2PKH
        # P2SH-P2WPKH
        # P2WSH-P2PKH

def low_r_only(tx):
    for i, input_type in enumerate(tx.inputs_types):
        if input_type == "p2wpkh" or input_type == "p2wsh":
            r_len = tx.inputs_witness[i][0][6:8]
        elif input_type == "p2pkh":
            r_len = tx.inputs_scriptSig[i][8:10]
        elif input_type == "p2sh":
            if tx.inputs_witness[i] is not []:
                r_len = tx.inputs_scriptSig[i][8:10]
            else:
                r_len = tx.inputs_witness[i][0][6:8]
        else:
            return False
        if int(r_len, 16) > 32:
                return False
        return True