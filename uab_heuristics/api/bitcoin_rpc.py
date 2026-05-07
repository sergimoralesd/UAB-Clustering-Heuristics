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

    def _batch_call(self, requests_list: list) -> list:
        payload = json.dumps(requests_list).encode()

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

        if not isinstance(body, list):
            body = [body]

        return body


    def get_raw_from_txid(self, txid: str) -> str:
        return self._call("getrawtransaction", [txid, False])
    
    def get_block_from_txid(self, txid: str) -> dict:
        block_hash = self._call("getrawtransaction", [txid, True])["blockhash"]
        block = self._call("getblockheader", [block_hash])
        return {
            "block_height": block["height"],
            "block_hash": block["hash"],
            "block_time": block["time"]
        }

    def get_blocks_from_txids(self, txids: list) -> dict:
        """Batch fetch block metadata for multiple txids."""
        if not txids:
            return {}

        raw_requests = [
            {
                "jsonrpc": "1.1",
                "id": f"raw-{idx}",
                "method": "getrawtransaction",
                "params": [txid, True],
            }
            for idx, txid in enumerate(txids)
        ]
        raw_responses = self._batch_call(raw_requests)
        raw_by_id = {resp.get("id"): resp for resp in raw_responses}

        block_hash_by_txid = {}
        header_requests = []
        for idx, txid in enumerate(txids):
            resp = raw_by_id.get(f"raw-{idx}")
            if not resp or resp.get("error"):
                continue
            result = resp.get("result") or {}
            block_hash = result.get("blockhash")
            if block_hash:
                block_hash_by_txid[txid] = block_hash
                header_requests.append(
                    {
                        "jsonrpc": "1.1",
                        "id": f"hdr-{idx}",
                        "method": "getblockheader",
                        "params": [block_hash],
                    }
                )

        if not header_requests:
            return {}

        header_responses = self._batch_call(header_requests)
        header_by_id = {resp.get("id"): resp for resp in header_responses}

        result_map = {}
        for idx, txid in enumerate(txids):
            if txid not in block_hash_by_txid:
                continue
            resp = header_by_id.get(f"hdr-{idx}")
            if not resp or resp.get("error"):
                continue
            block = resp.get("result") or {}
            if block:
                result_map[txid] = {
                    "block_height": block["height"],
                    "block_hash": block["hash"],
                    "block_time": block["time"],
                }

        return result_map
