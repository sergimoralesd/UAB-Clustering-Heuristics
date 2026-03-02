def signals_rbf(tx):
    for sequence_num in tx.inputs_sequence:
        if sequence_num < 4294967295:
            return True
    return False