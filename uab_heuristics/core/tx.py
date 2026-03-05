from bitcointx.core import CTransaction, lx, b2x
from bitcointx.core.script import CScript
from bitcointx.wallet import CCoinAddress
from ..utils import get_address_type, get_raw_tx_from_id, varint_size


class Tx:
    def __init__(self, base_tx: CTransaction = None):
        self._tx = base_tx
        self._previous_txs = None
        self._future_txs = None

    # ----------------------
    # Constructor methods
    # ----------------------
    @classmethod
    def from_raw(cls, raw_tx, network='bitcoin'):
        """
        Build Tx from raw bytes or hex string
        """
        if isinstance(raw_tx, str):
            raw_tx = bytes.fromhex(raw_tx)
        base_tx = CTransaction.deserialize(raw_tx)
        return cls(base_tx)

    @classmethod  
    def from_txid(cls, txid, network='bitcoin'):
        """
        Build Tx from txid by accessing the blockchain
        """
        raw_tx = get_raw_tx_from_id(txid=txid)
        base_tx = CTransaction.deserialize(raw_tx)
        return cls(base_tx)

    @classmethod 
    def from_json(self, filename, network='bitcoin'):
        raise NotImplementedError

    @classmethod
    def from_psbt(self, psbt, network='bitcoin'):
        raise NotImplementedError
    
    def import_previous_txs(self, network='bitcoin'):
        """
        Include the txs where the inputs comes from.
        """
        previous_txs = []
        for tx_input in self._tx.vin:
            prev_txid = b2x(tx_input.prevout.hash[::-1])
            previous_txs.append(self.__class__.from_txid(prev_txid, network=network))
        self._previous_txs = previous_txs

    def import_future_txs(self, txs, network='bitcoin', strict=True):
        """
        Include the txs spending the outputs. If no tx is provided for an output, it will be considered unspent
        """

        future_txs = [None for _ in range(self.output_count)]
        for future_txid in txs:  
            future_tx = self.__class__.from_txid(future_txid, network=network)

            for future_tx_input in future_tx._tx.vin:
                if b2x(future_tx_input.prevout.hash[::-1]) == self.txid:
                    output_n = future_tx_input.prevout.n
                    future_txs[output_n] = future_tx

        self._future_txs = future_txs
    
    def print_summary(self):
        print("=== Transaction Summary ===")
        print(f"TXID: {self.txid}")
        print(f"Size: {self.size} bytes")
        print(f"Virtual Size: {self.vsize} vbytes")
        print(f"Version: {self.version}")
        print(f"Locktime: {self.locktime}")
        print(f"Absolute Fee: {self.absolute_fee}")
        print(f"Relative Fee: {self.relative_fee}\n")

        print("--- Inputs ---")
        for idx, txin in enumerate(self._tx.vin):
            addr = self.inputs_addresses[idx]
            value = self.inputs_values[idx]
            addr_type = self.inputs_types[idx]
            prevout = self.prevouts[idx]
            seq = self.inputs_sequence[idx]
            witness = self.inputs_witness[idx]
            scriptsig = self.inputs_scriptSig[idx]

            print(f"Input {idx}:")
            print(f"  Address: {addr}")
            print(f"  Value: {value}")
            print(f"  Type: {addr_type}")
            print(f"  Prevout: {prevout}")
            print(f"  Sequence: {seq}")
            print(f"  Witness: {witness}")
            print(f"  ScriptSig: {scriptsig}\n")

        print("--- Outputs ---")
        for idx, vout in enumerate(self._tx.vout):
            addr = self.outputs_addresses[idx]
            value = self.outputs_values[idx]
            addr_type = self.outputs_types[idx]
            script_pub = self.outputs_scriptPubKey[idx]

            print(f"Output {idx}:")
            print(f"  Address: {addr}")
            print(f"  Value: {value}")
            print(f"  Type: {addr_type}")
            print(f"  ScriptPubKey: {script_pub}\n")

        print("--- Previous TXs ---")
        for prev in self.previous_txs:
            print(f"  {prev.txid if prev else None}")

        print("--- Future TXs ---")
        for fut in self.future_txs:
            print(f"  {fut.txid if fut else None}")

    @property
    def inputs_values(self):
        assert self._previous_txs is not None, f"Tx {self.txid} has not any previous tx, try running import_previous_txs"
        data =  []
        for tx_input, prev_tx in zip(self._tx.vin, self._previous_txs):
            prev_vout = tx_input.prevout.n
            data.append(prev_tx.outputs_values[prev_vout])
        return data

    @property
    def outputs_values(self):
        return [o.nValue for o in self._tx.vout]

    @property
    def inputs_addresses(self):
        addresses = []
        for i, vin in enumerate(self._tx.vin):
            prev_tx = self._previous_txs[i]
            vout_idx = vin.prevout.n
            script_pubkey = prev_tx._tx.vout[vout_idx].scriptPubKey
            try:
                address = str(CCoinAddress.from_scriptPubKey(script_pubkey))
            except Exception:
                address = None
            addresses.append(address)
        return addresses

    @property
    def outputs_addresses(self):
        addrs = []
        for vout in self._tx.vout:
            try:
                addrs.append(str(CCoinAddress.from_scriptPubKey(vout.scriptPubKey)))
            except:
                addrs.append(None)
        return addrs

    @property
    def txid(self):
        return b2x(self._tx.GetTxid()[::-1])

    @property
    def size(self):
        return len(self._tx.serialize())
    
    @property
    def weight(self):
        total_size = self.size
        has_witness = not self._tx.wit.is_null()
        if not has_witness:
            # Legacy tx: weight = 4 * size, vsize = size
            return total_size * 4
        witness_size = 2
        for txinwit in self._tx.wit.vtxinwit:
            stack = txinwit.scriptWitness.stack
            # varint for number of stack items
            witness_size += varint_size(len(stack))
            for item in stack:
                witness_size += varint_size(len(item)) + len(item)
        base_size = total_size - witness_size
        return base_size * 3 + total_size
    
    @property
    def vsize(self):
        return self.weight / 4
    
    @property
    def input_count(self):
        return len(self._tx.vin)

    @property
    def output_count(self):
        return len(self._tx.vout)

    @property
    def inputs_types(self):
        return [get_address_type(a) for a in self.inputs_addresses] 

    @property
    def outputs_types(self):
        return [get_address_type(a) for a in self.outputs_addresses]

    @property
    def previous_txid(self):
        return [b2x(vin.prevout.hash[::-1]) for vin in self._tx.vin]

    @property
    def future_txid(self):
        return [o.txid if o is not None else None for o in self._future_txs]
    
    @property
    def prevouts(self):
        return [f"{b2x(vin.prevout.hash[::-1])}:{vin.prevout.n}" for vin in self._tx.vin]
    
    @property
    def previous_txs(self):
        return self._previous_txs

    @property
    def future_txs(self):
        return self._future_txs
    
    @property
    def outputs_scriptPubKey(self):
        return [vout.scriptPubKey.hex() for vout in self._tx.vout]
    
    @property
    def locktime(self):
        return self._tx.nLockTime

    @property
    def absolute_fee(self):
        assert self._previous_txs is not None, "Call import_previous_txs first"
        return sum(self.inputs_values) - sum(self.outputs_values)

    @property
    def relative_fee(self):
        return round(self.absolute_fee / self.vsize)

    @property
    def version(self):
        return self._tx.nVersion
    
    @property
    def inputs_sequence(self):
        return [vin.nSequence for vin in self._tx.vin]

    @property
    def inputs_witness(self):
        witness_data = []
        if self._tx.wit.is_null():
            # No witnesses (legacy inputs)
            return [[] for _ in self._tx.vin]
        for vin_index, vin in enumerate(self._tx.vin):
            stack = self._tx.wit.vtxinwit[vin_index].scriptWitness.stack
            witness_data.append([b2x(w) for w in stack])
        return witness_data

    @property
    def inputs_scriptSig(self):
        return [vin.scriptSig.hex() for vin in self._tx.vin]
