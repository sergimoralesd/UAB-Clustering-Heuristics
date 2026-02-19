from uab_heuristics.core import Tx
from uab_heuristics.heuristics import ReusedAddressChange

txid = "547c6649c318d9238438f1acd26702c7e9e49e1dadd89fe50c8043426c943b52"
raw_tx = "020000000001011ee478e7ee58756d9007e59e9ef30a16b77e77e8444466f96b0087f4a5ac09c00100000000fdffffff02a522ea3900000000160014192e80ed2c7c412bdc2a6c8f371d15cb90f3c85b8150020000000000160014cc07da45f13efa6ad252972b891f36d84e17bb260247304402202cfff2529f38e38559a50ddd67a473dd0637437fbe13878d5872f1365a8e1fb402203b97e17bd35d0eba67ab8ad99657b947a872073f090c0eac35ff5eaf3e2b2b1d012103b01bd095f648ea829f000207087f16622431077bb5cc0875225ada601375c88500000000"

if __name__ == "__main__":
    tx = Tx.from_raw(raw_tx)
    print(tx.txid)
    print(tx.input_addresses)
    print(tx.output_addresses)
    result_reused_addr_change = ReusedAddressChange.apply(tx)
    print(result_reused_addr_change)
    