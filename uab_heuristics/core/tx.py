from __future__ import annotations # To allows Tx class to reference itself 
from bitcointx.core import CTransaction, b2x
from ..utils import get_address_type, get_raw_tx_from_id, varint_size, compute_addr


class Tx:
    def __init__(
        self,
        base_tx: CTransaction | None = None,
        previous_txids: list[str] = None,
        futures_txids: list[str] = None,
        replacement: Tx = None,
    ):
        self._tx = base_tx
        self.previous_txids = previous_txids
        self.futures_txids = futures_txids
        self.replacement = replacement
        self._previous_txs = None
        self._future_txs = None
        self._output_addrs = None
        self._inputs_addresses = None
        self._output_values = None
        self._inputs_values = None
        self._outputs_types = None
        self._inputs_types = None
        self._txid = None

    # ----------------------
    # Constructor methods
    # ----------------------

    @classmethod
    def from_raw(cls, raw_tx, network="bitcoin"):
        """
        Build Tx from raw bytes or hex string
        """
        if network != "bitcoin":
            raise ValueError("Only bitcoin network is supported")
        if isinstance(raw_tx, str):
            raw_tx = bytes.fromhex(raw_tx)
        base_tx = CTransaction.deserialize(raw_tx)
        return cls(base_tx)

    @classmethod
    def from_txid(cls, txid, network="bitcoin"):
        """
        Build Tx from txid by accessing the blockchain
        """
        if network != "bitcoin":
            raise ValueError("Only bitcoin network is supported")
        raw_tx = get_raw_tx_from_id(txid=txid)
        base_tx = CTransaction.deserialize(raw_tx)
        return cls(base_tx)

    @classmethod
    def from_json(cls, filename, network="bitcoin"):
        raise NotImplementedError("from_json is not implemented")

    @classmethod
    def from_psbt(cls, psbt, network="bitcoin"):
        raise NotImplementedError("from_psbt is not implemented")

    def import_previous_txs(self, prev_txs=None, network="bitcoin"):
        """
        Include the txs where the inputs come from.
        """
        if self._previous_txs:
            return
        if network != "bitcoin":
            raise ValueError("Only bitcoin network is supported")
        if prev_txs:
            self._previous_txs = prev_txs
            return
        if not self.previous_txids:
            self.previous_txids = [
                b2x(tx_input.prevout.hash[::-1]) for tx_input in self._tx.vin
            ]
        self._previous_txs = [
            self.__class__.from_txid(prev_txid, network=network)
            for prev_txid in self.previous_txids
        ]

    def import_future_txs(self, future_txs=None, future_txids=None, network="bitcoin"):
        """
        Include the txs spending the outputs.
        If no tx is provided for an output, it will be considered unspent.
        """
        if self._future_txs:
            return
        if network != "bitcoin":
            raise ValueError("Only bitcoin network is supported")
        if future_txs:
            self._future_txs = future_txs
            return
        if not self.futures_txids:
            if not future_txids:
                raise ValueError("Include future txs_ids to compute the future_txs")
            self.futures_txids = future_txids
        aux_future_txs = [None for _ in range(self.output_count)]
        for future_txid in self.futures_txids:
            future_tx = self.__class__.from_txid(future_txid, network=network)
            for future_tx_input in future_tx._tx.vin:
                if b2x(future_tx_input.prevout.hash[::-1]) == self.txid:
                    output_n = future_tx_input.prevout.n
                    aux_future_txs[output_n] = future_tx
        self._future_txs = aux_future_txs

    def import_original_tx(self, original: Tx = None):
        """
        Import the previous transactions of a replace by fee chain
        """
        if self.replacement:
            return

        if original:
            self.replacement = original
            return

        raise ValueError("The original tx must be of the type Tx")

    def print_summary(self):
        print("=== Transaction Summary ===")
        print(f"TXID: {self.txid}")
        print(f"Size: {self.size} bytes")
        print(f"Virtual Size: {self.vsize} vbytes")
        print(f"Version: {self.version}")
        print(f"Locktime: {self.locktime}")
        print(f"Absolute Fee: {self.absolute_fee}")
        print(f"Relative Fee: {self.relative_fee}")

    # ----------------------
    # Properties
    # ----------------------

    @property
    def txid(self):
        if not self._txid:
            self._txid = b2x(self._tx.GetTxid()[::-1])
        return self._txid

    @property
    def size(self):
        return len(self._tx.serialize())

    @property
    def weight(self):
        total_size = self.size
        has_witness = not self._tx.wit.is_null()
        if not has_witness:
            return total_size * 4
        witness_size = 2
        for txinwit in self._tx.wit.vtxinwit:
            stack = txinwit.scriptWitness.stack
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
    def outputs_values(self):
        if not self._output_values:
            self._output_values = [o.nValue for o in self._tx.vout]
        return self._output_values

    @property
    def outputs_scriptPubKey(self):
        return [vout.scriptPubKey.hex() for vout in self._tx.vout]

    @property
    def outputs_addresses(self):
        if not self._output_addrs:
            self._output_addrs = self.compute_output_addresses()
        return self._output_addrs

    @property
    def previous_txid(self):
        return [b2x(vin.prevout.hash[::-1]) for vin in self._tx.vin]

    @property
    def prevouts(self):
        return [
            f"{b2x(vin.prevout.hash[::-1])}:{vin.prevout.n}" for vin in self._tx.vin
        ]

    @property
    def locktime(self):
        return self._tx.nLockTime

    @property
    def version(self):
        return self._tx.nVersion

    @property
    def inputs_sequence(self):
        return [vin.nSequence for vin in self._tx.vin]

    @property
    def inputs_scriptSig(self):
        return [vin.scriptSig.hex() for vin in self._tx.vin]

    @property
    def inputs_witness(self):
        if self._tx.wit.is_null():
            return [[] for _ in self._tx.vin]
        witness_data = []
        for vin_index, vin in enumerate(self._tx.vin):
            stack = self._tx.wit.vtxinwit[vin_index].scriptWitness.stack
            witness_data.append([b2x(w) for w in stack])
        return witness_data

    @property
    def is_segwit(self):
        """
        True if any input has witness data (mirrors Rust: any input with non-empty witness).
        """
        if self._tx.wit.is_null():
            return False
        return any(
            len(self._tx.wit.vtxinwit[i].scriptWitness.stack) > 0
            for i in range(len(self._tx.vin))
        )

    @property
    def previous_txs(self):
        return self._previous_txs

    @property
    def future_txs(self):
        return self._future_txs

    @property
    def future_txid(self):
        if not self._future_txs:
            return []
        return [o.txid if o is not None else None for o in self._future_txs]

    @property
    def inputs_values(self):
        assert self._previous_txs is not None, (
            f"Tx {self.txid} has no previous txs, try running import_previous_txs"
        )
        if not self._inputs_values:
            self._inputs_values = self.compute_inputs_values()
        return self._inputs_values

    @property
    def inputs_addresses(self):
        assert self._previous_txs is not None, (
            f"Tx {self.txid} has no previous txs, try running import_previous_txs"
        )
        if not self._inputs_addresses:
            self._inputs_addresses = self.compute_inputs_addresses()
        return self._inputs_addresses

    @property
    def inputs_types(self):
        if not self._inputs_types:
            self._inputs_types = [get_address_type(a) for a in self.inputs_addresses]
        return self._inputs_types

    @property
    def outputs_types(self):
        if not self._outputs_types:
            self._outputs_types = [get_address_type(a) for a in self.outputs_addresses]
        return self._outputs_types

    @property
    def absolute_fee(self):
        assert self._previous_txs is not None, "Call import_previous_txs first"
        return sum(self.inputs_values) - sum(self.outputs_values)

    @property
    def relative_fee(self):
        """
        Satoshis per 1000 virtual bytes (sat/kvbyte), matching the Rust implementation.
        """
        return int((self.absolute_fee * 1000) / self.vsize)

    @property
    def is_segwit_conform(self):
        """
        True when the tx's SegWit serialization matches its input types:
        - has SegWit inputs AND uses SegWit serialization, OR
        - has no SegWit inputs AND does not use SegWit serialization.
        """
        witness_types = {"p2wpkh", "p2wsh", "p2tr", "p2sh-p2wpkh"}
        has_segwit_input = any(t in witness_types for t in self.inputs_types)
        uses_segwit_serialization = self.is_segwit
        return has_segwit_input == uses_segwit_serialization

    @property
    def has_uncompressed_public_keys(self):
        """
        True if any input uses an uncompressed (65-byte, 0x04-prefixed) public key.
        Checks P2PKH scriptSigs and P2MS scriptPubKeys in previous txs.
        """
        for i, vin in enumerate(self._tx.vin):
            addr_type = self.inputs_types[i]

            if addr_type == "p2pkh":
                # Uncompressed pubkey is the second push in scriptSig (sig + pubkey)
                ops = list(vin.scriptSig)
                if len(ops) >= 2:
                    pubkey_bytes = ops[1]
                    if len(pubkey_bytes) == 65 and pubkey_bytes[0] == 0x04:
                        return True

            elif addr_type == "p2ms":
                if self._previous_txs is None:
                    continue
                prev_tx = self._previous_txs[i]
                vout_idx = vin.prevout.n
                script_pubkey = prev_tx._tx.vout[vout_idx].scriptPubKey
                for op in script_pubkey:
                    if isinstance(op, bytes) and len(op) == 65 and op[0] == 0x04:
                        return True

        return False

    # ----------------------
    # Compute helpers
    # ----------------------

    def compute_output_addresses(self):
        return [compute_addr(vout.scriptPubKey) for vout in self._tx.vout]

    def compute_inputs_addresses(self):
        addresses = []
        for i, vin in enumerate(self._tx.vin):
            prev_tx = self._previous_txs[i]
            vout_idx = vin.prevout.n
            script_pubkey = prev_tx._tx.vout[vout_idx].scriptPubKey
            addresses.append(compute_addr(script_pubkey))
        return addresses

    def compute_inputs_values(self):
        data = []
        for tx_input, prev_tx in zip(self._tx.vin, self._previous_txs):
            prev_vout = tx_input.prevout.n
            data.append(prev_tx.outputs_values[prev_vout])
        return data