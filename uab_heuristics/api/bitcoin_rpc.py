import os
import json
from dotenv import load_dotenv
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from base64 import b64encode
from ..core.exceptions import NotFoundError, FetchError, ConfigurationError
from ..core.base_adapter import BaseAdapter


class _RPCAdapter(BaseAdapter):
    name = "bitcoin_rpc"
    def __init__(self):
        load_dotenv()

        user = os.getenv("BTC_RPC_USER")
        passwd = os.getenv("BTC_RPC_PASSWORD")
        url = os.getenv("BTC_RPC_URL")

        if not user or not passwd or not url:
            raise ConfigurationError("Missing RPC config in .env file")

        self._url = url
        credentials = b64encode(f"{user}:{passwd}".encode()).decode()
        self._auth_header = f"Basic {credentials}"
        self._id = 0
    
    def _call(self, method: str, params: list) -> dict:
        self._id += 1
        payload = json.dumps({
            "jsonrpc": "1.1",
            "id": self._id,
            "method": method,
            "params": params,
        }).encode()

        req = Request(
            self._url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": self._auth_header,
            },
        )

        try:
            with urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode())
        except HTTPError as exc:
            try:
                body = json.loads(exc.read().decode())
            except Exception:
                raise FetchError(f"HTTP {exc.code} from RPC node") from exc
        except URLError as exc:
            raise FetchError(f"Cannot reach RPC node: {exc.reason}") from exc
        
        if body.get("error"):
            code = body["error"].get("code")
            msg = body["error"].get("message", "unknown RPC error")
            if code == -5:
                raise NotFoundError(f"txid not found via RPC: {msg}")
            raise FetchError(f"RPC error {code}: {msg}")

        return body["result"]

    def get_raw_from_txid(self, txid: str) -> str:
        return bytes.fromhex(self._call("getrawtransaction", [txid, False]))
    
    def get_block_from_txid(self, txid: str) -> dict:
        block_hash = self._call("getrawtransaction", [txid, True])["blockhash"]
        block = self._call("getblock", [block_hash, 0])
        return {
            "block_height": block["height"],
            "block_hash": block["hash"],
            "block_time": block["time"]
        }