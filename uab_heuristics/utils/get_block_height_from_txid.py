import json
from ..api import make_request, rpc_call

def get_block_height_from_txid(txid):
    templates = ["https://mempool.space/api/tx/{0}", "https://blockchain.info/rawtx/{0}"]
    try:
        block_hash = rpc_call("getrawtransaction", [txid, True])["blockhash"]
        return rpc_call("getblock", [block_hash, 0])["height"]
    except Exception as e:
        print(f"RPC failed, trying external APIs...")
        tx = make_request(txid, templates)
        if isinstance(tx, str):
            tx = json.loads(tx)
        if "status" in tx:
            return tx["status"]["block_height"]
        return tx["block_height"]