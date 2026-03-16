def low_r_only(tx):
    for i in range(tx.input_count):
        #p2wpkh
        if tx.inputs_witness[i] != []:
            #detect p2ms
                if tx.inputs_witness[i][0] != "":
                    r_len = tx.inputs_witness[i][0][6:8]
                return False
        #p2pkh
        else:
            r_len = tx.inputs_scriptSig[i][8:10]

        if int(r_len, 16) > 32:
                return False
        return True