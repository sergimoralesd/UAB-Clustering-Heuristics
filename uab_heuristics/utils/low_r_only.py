def low_r_only(tx):
    for i, input_type in enumerate(tx.inputs_types):
        if input_type == "p2wpkh":
            r_len = tx.inputs_witness[i][0][6:8]
        elif input_type == "p2pkh":
            r_len = tx.inputs_scriptSig[i][8:10]
        elif input_type == "p2sh":
            if tx.inputs_witness[i]:
                r_len = tx.inputs_witness[i][0][6:8]
            else:
                r_len = tx.inputs_scriptSig[i][8:10]
        else:
            return False
        if int(r_len, 16) > 32:
                return False
        return True