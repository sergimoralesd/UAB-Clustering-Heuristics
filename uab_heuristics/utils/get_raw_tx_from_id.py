from ..api import make_request, rpc_call

def get_raw_tx_from_id(txid):
    templates = ["https://mempool.space/api/tx/{0}/hex", "https://blockchain.info/rawtx/{0}?format=hex"]
    try:
        return(bytes.fromhex(rpc_call("getrawtransaction", [txid, False])))
    except Exception as e:
        print(f"RPC failed, trying external APIs...")
        return(bytes.fromhex(make_request(txid, templates)))