from bitcoin.core.script import CScript, OP_CHECKMULTISIG


def _decode_op_n(op):
    """Decode OP_N opcode values to integers (0-16)."""
    if not isinstance(op, int):
        return None
    if op == 0:
        return 0
    if 81 <= op <= 96:
        return op - 80
    return None

def get_multisignature_script_type(tx):
    """
    Return multisignature script type of inputs
    We asume every input is from the same user

    m-n -> any multisignature type
    0 -> if it is not a multisignature script
    """
    results = []
    for i in range(tx.input_count):
        try:
            #non witness
            if tx.inputs_witness[i] == []:
                #transform the hex into a script
                scriptSig = list(CScript(bytes.fromhex(tx.inputs_scriptSig[i])))
                #obtain the redeemScript in order to see if its a multisignature
                if not scriptSig:
                    continue
                redeem = scriptSig[-1]
                if not isinstance(redeem, (bytes, bytearray)):
                    continue
                multisignature_script = list(CScript(bytes(redeem)))
            else:
                witness = tx.inputs_witness[i]
                if not witness:
                    continue
                multisignature_script = list(CScript(bytes.fromhex(witness[-1])))

        except Exception:
            #if we find any error, sure is not a multisig
            continue
        
        #by this we ensure is a multisig script
        if OP_CHECKMULTISIG not in multisignature_script:
            continue

        op_idx = multisignature_script.index(OP_CHECKMULTISIG)
        if op_idx < 2:
            continue
        
        # amount of signatures needed and total pubkeys (m-of-n)
        m = _decode_op_n(multisignature_script[0])
        n = _decode_op_n(multisignature_script[op_idx - 1])

        if m is None or n is None:
            continue
        if m <= 0 or n <= 0 or m > n:
            continue
        
        results.append(f"{m}-{n}")

    return list(set(results))