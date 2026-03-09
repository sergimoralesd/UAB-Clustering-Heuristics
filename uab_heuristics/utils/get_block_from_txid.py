import json
from ..api import make_request, rpc_call

def get_block_from_txid(txid):
    templates = ["https://mempool.space/api/tx/{0}", "https://blockchain.info/rawtx/{0}"]
    try:
        block_hash = rpc_call("getrawtransaction", [txid, True])["blockhash"]
        block = rpc_call("getblock", [block_hash, 0])
        return {
            "block_height": block["height"],
            "block_hash": block["hash"],
            "block_time": block["time"]
        }
    except Exception as e:
        print(f"RPC failed, trying external APIs...")
        block = make_request(txid, templates)
        if isinstance(block, str):
            block = json.loads(block)
        if "status" in block:
                return {
                    "block_height": block["status"].get("block_height"),
                    "block_hash": block["status"].get("block_hash"),
                    "block_time": block["status"].get("block_time")
                }
        
        return {
                "block_height": block.get("block_height"),
                "block_hash": block.get("block_hash"),
                "block_time": block.get("block_time")
        }