from bitcointx.core import Hash160
from bitcointx.wallet import CCoinAddress, P2PKHBitcoinAddress

def compute_addr(script_pubkey):
    try:
        address = str(CCoinAddress.from_scriptPubKey(script_pubkey))
    except Exception:
        #we found a p2pk
        pubkey_bytes = script_pubkey[1:-1]  # strip the length prefix and OP_CHECKSIG
        pubkey_hash = Hash160(pubkey_bytes)
        address = str(P2PKHBitcoinAddress.from_bytes(pubkey_hash))
    return address