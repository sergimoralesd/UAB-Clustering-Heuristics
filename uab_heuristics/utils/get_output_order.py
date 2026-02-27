from binascii import unhexlify

def get_output_order(tx):
    """
    Return ordering type of outputs of a transaction

    0 -> ascending order
    1 -> descending order
    2 -> BIP69 order
    3 -> undetermined

    """
    
    if sorted(tx.outputs_values) == tx.outputs_values:
        return 0
    
    if sorted(tx.outputs_values)[::-1] == tx.outputs_values:
        return 1
    
    paired = list(zip(tx.outputs_values, tx.outputs_scriptPubKey))
    if sorted(paired,key=lambda x: (x[0], unhexlify(x[1]))) == paired:
        return 2
    return 3