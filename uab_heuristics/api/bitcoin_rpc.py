import requests
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

RPC_USER = os.getenv("BTC_RPC_USER")
RPC_PASSWORD = os.getenv("BTC_RPC_PASSWORD")
RPC_URL = os.getenv("BTC_RPC_URL")

if not RPC_USER or not RPC_PASSWORD or not RPC_URL:
    raise RuntimeError("Missing RPC config in .env file")

def rpc_call(method, params=None):
    payload = {
        "jsonrpc": "1.0",
        "id": "btc",
        "method": method,
        "params": params or []
    }

    r = requests.post(
        RPC_URL,
        json=payload,
        auth=HTTPBasicAuth(RPC_USER, RPC_PASSWORD),
        timeout=30
    )

    r.raise_for_status()
    result = r.json()

    if result.get("error"):
        raise RuntimeError(result["error"])

    return result["result"]