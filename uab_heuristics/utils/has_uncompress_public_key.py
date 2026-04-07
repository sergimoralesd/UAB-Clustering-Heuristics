from bitcoin.core.script import CScript
#TODO:
#detect other scenarios
    #- P2SH-P2PKH
    #- P2SH-P2MS

def has_uncompress_public_keys(tx):
    for i, input_type in enumerate(tx.inputs_types):
        if input_type == "p2pkh":
            scriptSig = list(CScript(bytes.fromhex(tx.inputs_scriptSig[i])))
            public_key = scriptSig[1].hex()
            if public_key[1] == "4":
                return True
            
        elif input_type == "p2ms":
            prev_tx = tx._previous_txs[i]
            prev_vout = int(tx.prevouts[i].split(":")[1])

            scriptPubKey = prev_tx.outputs_scriptPubKey[prev_vout]
            scriptPubKey = list(CScript(bytes.fromhex(scriptPubKey)))

            n_pubkeys = int(scriptPubKey[-2])
            for i in range(n_pubkeys):
                public_key = scriptPubKey[i + 1].hex()
                if public_key[1] == "4":
                    return True
        
    return False