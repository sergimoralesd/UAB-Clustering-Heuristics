#TODO:
    # implement the low_r detection for the 
        # P2SH-P2PKWH
        # P2SH-P2WPKH
        # P2WSH-P2PKWH
        # P2WSH-P2WPKH 

def low_r_only(tx):
    for i, input_type in enumerate(tx.inputs_types):
        if input_type == "p2wpkh":
            r_len = tx.inputs_witness[i][0][6:8]
        elif input_type == "p2pkh":
            r_len = tx.inputs_scriptSig[i][8:10]
        else:
             return False
        if int(r_len, 16) > 32:
                return False
        return True