from bitcoinlib.transactions import Transaction as BaseTransaction
from io import BytesIO
from ..api import rpc_call, make_request
from ..utils import get_address_type


class Tx:
    def __init__(self, base_tx: BaseTransaction = None):
        self._tx = base_tx
        self._previous_txs = None
    
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
    
    def import_previous_txs(self, network='bitcoin', strict=True):
        """
        Include the txs where the inputs comes from.
        """
        previous_txs = []
        for tx_input in self._tx.inputs:
            prev_txid = tx_input.prev_txid.hex()
            previous_txs.append(self.__class__.from_txid(prev_txid, network=network, strict=strict))
        self._previous_txs = previous_txs
    
    @property
    def inputs_values(self):
        assert self._previous_txs is not None, f"Tx {self.txid} has not any previous tx, try running import_previous_txs"
        data =  []
        for tx_input, prev_tx in zip(self._tx.inputs, self._previous_txs):
            prev_vout = int.from_bytes(tx_input.output_n, byteorder="big")
            data.append(prev_tx.outputs_values[prev_vout])
        return data

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
    
    @property
    def previous_txid(self):
        return [(i.prev_txid, i.output_n) for i in self._tx.inputs]