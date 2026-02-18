from bitcoinlib.transactions import Transaction as BaseTransaction
from io import BytesIO

class Tx:
    def __init__(self, base_tx: BaseTransaction = None):
        self._tx = base_tx
    
    # ----------------------
    # Constructor methods
    # ----------------------
    @classmethod
    def from_raw(cls, rawtx, network='bitcoin', strict=True):
        """
        Build Tx from raw bytes or hex string
        """
        if isinstance(rawtx, str):
            rawtx = bytes.fromhex(rawtx)
        base_tx = BaseTransaction.parse_bytesio(BytesIO(rawtx), strict=strict, network=network)
        return cls(base_tx)
        
    def from_txid(cls, txid, network='bitcoin'):
        """
        Build Tx from txid by accessing the blockchain
        """
        #raw_tx = 
        base_tx = BaseTransaction.import_raw(txid, network=network)
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

tx = Tx.from_raw("020000000001011ee478e7ee58756d9007e59e9ef30a16b77e77e8444466f96b0087f4a5ac09c00100000000fdffffff02a522ea3900000000160014192e80ed2c7c412bdc2a6c8f371d15cb90f3c85b8150020000000000160014cc07da45f13efa6ad252972b891f36d84e17bb260247304402202cfff2529f38e38559a50ddd67a473dd0637437fbe13878d5872f1365a8e1fb402203b97e17bd35d0eba67ab8ad99657b947a872073f090c0eac35ff5eaf3e2b2b1d012103b01bd095f648ea829f000207087f16622431077bb5cc0875225ada601375c88500000000")
print(tx.input_addresses)
print(tx.output_addresses)
print(tx)