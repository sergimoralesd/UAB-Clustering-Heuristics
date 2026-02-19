from uab_heuristics.core import Tx

if __name__ == "__main__":
    tx = Tx.from_raw("020000000001011ee478e7ee58756d9007e59e9ef30a16b77e77e8444466f96b0087f4a5ac09c00100000000fdffffff02a522ea3900000000160014192e80ed2c7c412bdc2a6c8f371d15cb90f3c85b8150020000000000160014cc07da45f13efa6ad252972b891f36d84e17bb260247304402202cfff2529f38e38559a50ddd67a473dd0637437fbe13878d5872f1365a8e1fb402203b97e17bd35d0eba67ab8ad99657b947a872073f090c0eac35ff5eaf3e2b2b1d012103b01bd095f648ea829f000207087f16622431077bb5cc0875225ada601375c88500000000")
    print(tx.input_addresses)
    print(tx.output_addresses)
    print(tx.txid)
    print(tx.input_count)


    tx = Tx.from_txid("6662bcc9aee93d57aaa0fd734596b2f3dbca629956623a78786105106ac46ac4")
    print(tx.inputs)
    print(tx.input_addresses)
    print(tx.outputs)
    print(tx.output_addresses)
    print(tx.txid)