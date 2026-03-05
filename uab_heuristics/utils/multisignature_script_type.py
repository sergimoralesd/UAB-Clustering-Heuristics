from bitcoin.core.script import CScript, OP_CHECKMULTISIG

def get_multisignature_script_type(tx):
    """
    Return multisignature script type of inputs
    We asume every input is from the same user

    m-n -> any multisignature type
    0 -> if it is not a multisignature script
    """
    results = []
    for i, type in enumerate(tx.inputs_types):
        try:
            if type == "p2sh":
                #check first if the data is in witness field
                if tx.inputs_witness[i] == []:
                    #transform the hex into a script
                    scriptSig = list(CScript(bytes.fromhex(tx.inputs_scriptSig[i])))
                    #obtain the redeemScript in order to see if its a multisignature
                    multisignature_script = list(CScript(scriptSig[-1]))
                else:
                    multisignature_script = list(CScript(bytes.fromhex(tx.inputs_witness[i][-1])))
            elif type == "p2wsh":
                multisignature_script = list(CScript(bytes.fromhex(tx.inputs_witness[i][-1])))
            else:
                continue
        except:
            #if we find any erro, sure isnt a multisig
            continue
        
        #by this we ensure is a multisig script
        if OP_CHECKMULTISIG not in multisignature_script:
            continue
        
        #amount of public keys
        m = multisignature_script[0]

        #amount of signatures needed
        n = multisignature_script[m + 1]
        
        results.append(f"{m}-{n}")

    return list(set(results))