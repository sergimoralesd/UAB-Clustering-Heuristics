from uab_heuristics.core import Tx

if __name__ == "__main__":
    tx = Tx.from_raw("020000000001011ee478e7ee58756d9007e59e9ef30a16b77e77e8444466f96b0087f4a5ac09c00100000000fdffffff02a522ea3900000000160014192e80ed2c7c412bdc2a6c8f371d15cb90f3c85b8150020000000000160014cc07da45f13efa6ad252972b891f36d84e17bb260247304402202cfff2529f38e38559a50ddd67a473dd0637437fbe13878d5872f1365a8e1fb402203b97e17bd35d0eba67ab8ad99657b947a872073f090c0eac35ff5eaf3e2b2b1d012103b01bd095f648ea829f000207087f16622431077bb5cc0875225ada601375c88500000000")
    print(tx.inputs_addresses)
    print(tx.outputs_addresses)
    print(tx.txid)
    print(tx.input_count)
    print(tx.inputs_types)
    print(tx.outputs_types)
    tx.import_previous_txs()
    print(tx.inputs_values)
    print(tx.outputs_values)
    print(tx.absolute_fee)
    print(tx.relative_fee)
    print(tx.size)



    tx = Tx.from_txid("6662bcc9aee93d57aaa0fd734596b2f3dbca629956623a78786105106ac46ac4")
    print(tx.inputs_addresses)
    print(tx.outputs_addresses)
    print(tx.txid)
    print(tx.input_count)
    print(tx.inputs_types)
    print(tx.outputs_types)
    tx.import_future_txs(["ad164b6e7c034243e5488c49d3bf879bdac533bdca07d32cce6b82c1eaf52999", "3d2abf76a0ab0bbaf464b7b58f1593f96539e6f3587b34f80c6ca419797cf9b3"])
    print(tx.future_txid)
    print(tx.outputs_scriptPubKey)
    tx.import_previous_txs()
    print(tx.absolute_fee)
    print(tx.relative_fee)
    print(tx.size)
    print(tx.version)
    print(tx.inputs_sequence)
    print(tx.inputs_witness)
    print(tx.inputs_scriptSig)
    
    #tx = Tx.from_txid("6662bcc9aee93d57aaa0fd734596b2f3dbca629956623a78786105106ac46ac4")
    #print(tx.inputs_witness)
    #print(tx.inputs_scriptSig)
    #tx = Tx.from_txid("e832a048ff7330d3e23c766a5d725997f96789d38923654f5533ff3f314de4bd")
    #print(tx.inputs_witness)
    #print(tx.inputs_scriptSig)

    print("##MULTISIG##")
    tx = Tx.from_txid("1085ee6d2b65eb2cbd322e4afd0a43342bb943dd27a4ad6eddfdc6a7102b6b3c")
    print(tx.inputs_scriptSig)
    print(tx.inputs_witness)

    tx = Tx.from_txid("4d8eabfc8e6c266fb0ccd815d37dd69246da634df0effd5a5c922e4ec37880f6")
    print(tx.inputs_scriptSig)
    print(tx.inputs_witness)

    #taproot tx
    tx = Tx.from_txid("3179b878515d5ac2918e0bc1e7efdf58f04515691c3b5a96c6f734d5162556e7")
    
    

