from bitcoinlib.transactions import Transaction as BaseTransaction
from io import BytesIO
from ..api import rpc_call, make_request
from ..utils import get_address_type


class Tx:
    def __init__(self, base_tx: BaseTransaction = None):
        self._tx = base_tx
    
    # ----------------------
    # Constructor methods
    # ----------------------
    @classmethod
    def from_raw(cls, raw_tx, network='bitcoin', strict=True):
        """
        Build Tx from raw bytes or hex string
        """
        if isinstance(raw_tx, str):
            raw_tx = bytes.fromhex(raw_tx)
        base_tx = BaseTransaction.parse_bytesio(BytesIO(raw_tx), strict=strict, network=network)
        return cls(base_tx)

    @classmethod  
    def from_txid(cls, txid, network='bitcoin', strict=True):
        """
        Build Tx from txid by accessing the blockchain
        """
        try:
            raw_tx = bytes.fromhex(rpc_call("getrawtransaction", [txid, False]))
        except Exception as e:
            print(f"RPC failed, trying external APIs...")
            raw_tx = bytes.fromhex(make_request(txid))

        base_tx = BaseTransaction.parse_bytesio(BytesIO(raw_tx), strict=strict, network=network)
        return cls(base_tx)

    @classmethod 
    def from_json(self, filename, network='bitcoin', strict=True):
        raise NotImplementedError

    @classmethod
    def from_psbt(self, psbt, network='bitcoin', strict=True):
        raise NotImplementedError
    
    @property
    def inputs_values(self):
        return [(i.address, i.value) for i in self._tx.inputs]

    @property
    def outputs_values(self):
        return [(o.address, o.value) for o in self._tx.outputs]

    @property
    def input_addresses(self):
        return [i.address for i in self._tx.inputs]

    @property
    def output_addresses(self):
        return [o.address for o in self._tx.outputs]

    @property
    def txid(self):
        return self._tx.txid

    @property
    def size(self):
        return self._tx.size
    
    @property
    def input_count(self):
        return len(self._tx.inputs)
    
    @property
    def output_count(self):
        return len(self._tx.outputs)

    @property
    def inputs_types(self):
        return [(i.address, get_address_type(i.address)) for i in self._tx.inputs] 

    @property
    def outputs_types(self):
        return [(o.address, get_address_type(o.address)) for o in self._tx.outputs]