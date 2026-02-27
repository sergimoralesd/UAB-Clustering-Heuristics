from bitcoinlib.transactions import Transaction as BaseTransaction
from io import BytesIO
from ..utils import get_address_type, get_raw_tx_from_id


class Tx:
    def __init__(self, base_tx: BaseTransaction = None):
        self._tx = base_tx
        self._previous_txs = None
        self._future_txs = None

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
        raw_tx = get_raw_tx_from_id(txid=txid)
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

    def import_future_txs(self, txs, network='bitcoin', strict=True):
        """
        Include the txs spending the outputs. If no tx is provided for an output, it will be considered unspent
        """

        future_txs = [None for _ in range(self.output_count)]
        for future_txid in txs:  
            future_tx = self.__class__.from_txid(future_txid, network=network, strict=strict)

            for future_tx_input in future_tx._tx.inputs:
                if future_tx_input.prev_txid.hex() == self.txid:
                    output_n = int.from_bytes(future_tx_input.output_n, byteorder="big")
                    future_txs[output_n] = future_tx

        self._future_txs = future_txs

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
        return [o.value for o in self._tx.outputs]

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
        return [get_address_type(i.address) for i in self._tx.inputs] 

    @property
    def outputs_types(self):
        return [get_address_type(o.address) for o in self._tx.outputs]
    
    @property
    def previous_txid(self):
        return [i.prev_txid.hex() for i in self._tx.inputs]
    
    @property
    def future_txid(self):
        return [o.txid if o is not None else None for o in self._future_txs]
    
    @property
    def prevouts(self):
        return [f"{i.prev_txid.hex()}:{i.output_n}" for i in self._tx.inputs]
    
    @property
    def previous_txs(self):
        return self._previous_txs

    @property
    def future_txs(self):
        return self._future_txs
    
    @property
    def outputs_scriptPubKey(self):
        return [o.lock_script.hex() for o in self._tx.outputs]
    
    @property
    def locktime(self):
        return self._tx.locktime
    
    @property
    def absolute_fee(self):
        assert self._previous_txs is not None, f"Tx {self.txid} has not any previous tx, try running import_previous_txs"
        return sum(self.inputs_values) - sum(self.outputs_values)
    
    @property
    def relative_fee(self):
        return round(self.absolute_fee/self.size)