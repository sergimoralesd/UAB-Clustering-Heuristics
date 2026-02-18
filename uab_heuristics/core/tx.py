from bitcoinlib.transactions import Transaction as BaseTransaction
from io import BytesIO
from ..api import rpc_call, make_request


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

    def from_json(self):
        pass

    def from_psbt(self):
        pass
    
    @property
    def inputs(self):
        return [(i.address, i.value) for i in self._tx.inputs]

    @property
    def outputs(self):
        return [(o.address, o.value) for o in self._tx.outputs]

    @property
    def input_addresses(self):
        return {i.address for i in self._tx.inputs}

    @property
    def output_addresses(self):
        return {o.address for o in self._tx.outputs}

    @property
    def txid(self):
        return self._tx.txid

    @property
    def size(self):
        return self._tx.size


if __name__ == "__main__":
    tx = Tx.from_raw("020000000001011ee478e7ee58756d9007e59e9ef30a16b77e77e8444466f96b0087f4a5ac09c00100000000fdffffff02a522ea3900000000160014192e80ed2c7c412bdc2a6c8f371d15cb90f3c85b8150020000000000160014cc07da45f13efa6ad252972b891f36d84e17bb260247304402202cfff2529f38e38559a50ddd67a473dd0637437fbe13878d5872f1365a8e1fb402203b97e17bd35d0eba67ab8ad99657b947a872073f090c0eac35ff5eaf3e2b2b1d012103b01bd095f648ea829f000207087f16622431077bb5cc0875225ada601375c88500000000")
    print(tx.input_addresses)
    print(tx.output_addresses)


    tx2 = Tx.from_txid("6662bcc9aee93d57aaa0fd734596b2f3dbca629956623a78786105106ac46ac4")
    print(tx2.input_addresses)
    print(tx2.output_addresses)

