from bitcoin.core.script import CScript
#TODO:
#detect other scenarios
    #- P2SH-P2PKH
    #- P2SH-P2MS


def _is_uncompressed_pubkey(pubkey):
    return isinstance(pubkey, bytes) and len(pubkey) == 65 and pubkey[0] == 0x04


def has_uncompress_public_keys(tx):
    for idx, input_type in enumerate(tx.inputs_types):
        if input_type == "p2pkh":
            try:
                script_sig_items = list(CScript(bytes.fromhex(tx.inputs_scriptSig[idx])))
            except (ValueError, IndexError, TypeError):
                continue

            # Canonical p2pkh scriptSig is [signature, public_key].
            if len(script_sig_items) >= 2 and _is_uncompressed_pubkey(script_sig_items[1]):
                return True

        elif input_type == "p2ms":
            try:
                prev_tx = tx._previous_txs[idx]
                prev_vout = int(tx.prevouts[idx].split(":")[1])
                script_pub_key_hex = prev_tx.outputs_scriptPubKey[prev_vout]
                script_pub_key_items = list(CScript(bytes.fromhex(script_pub_key_hex)))
            except (ValueError, IndexError, TypeError, AttributeError):
                continue

            # In bare multisig scriptPubKey, pushed pubkeys are byte items.
            for item in script_pub_key_items:
                if _is_uncompressed_pubkey(item):
                    return True

    return False