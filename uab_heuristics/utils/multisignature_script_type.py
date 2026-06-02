from bitcointx.core.script import CScript, OP_CHECKMULTISIG


def _decode_op_n(op):
    """Decode OP_N opcode values to integers (0-16)."""
    if not isinstance(op, int):
        return None
    if op == 0:
        return 0
    if 81 <= op <= 96:
        return op - 80
    return None


def _get_multisignature_script_type_from_input(tx, i):
    try:
        # non witness
        if tx.inputs_witness[i] == []:
            # transform the hex into a script
            scriptSig = list(CScript(bytes.fromhex(tx.inputs_scriptSig[i])))
            # obtain the redeemScript in order to see if its a multisignature
            if not scriptSig:
                return None
            redeem = scriptSig[-1]
            if not isinstance(redeem, (bytes, bytearray)):
                return None
            multisignature_script = list(CScript(bytes(redeem)))
        else:
            witness = tx.inputs_witness[i]
            if not witness:
                return None
            # witness items are hex strings
            multisignature_script = list(CScript(bytes.fromhex(witness[-1])))

    except Exception:
        # if we find any error, sure is not a multisig
        return None

    # by this we ensure is a multisig script
    if OP_CHECKMULTISIG not in multisignature_script:
        return None

    op_idx = multisignature_script.index(OP_CHECKMULTISIG)
    if op_idx < 2:
        return None

    # amount of signatures needed and total pubkeys (m-of-n)
    m = _decode_op_n(multisignature_script[0])
    n = _decode_op_n(multisignature_script[op_idx - 1])

    if m is None or n is None:
        return None
    if m <= 0 or n <= 0 or m > n:
        return None

    return f"{m}-{n}"


def get_multisignature_script_type(tx, input_index=None):
    """
    Return multisignature script type of inputs
    We asume every input is from the same user

    m-n -> any multisignature type
    0 -> if it is not a multisignature script
    """
    results = []
    if input_index is not None:
        ms_type = _get_multisignature_script_type_from_input(tx, input_index)
        return [ms_type] if ms_type is not None else []

    for i in range(tx.input_count):
        ms_type = _get_multisignature_script_type_from_input(tx, i)
        if ms_type is None:
            continue
        results.append(ms_type)

    return list(set(results))