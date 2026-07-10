import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uab_heuristics.core import Tx
from uab_heuristics.heuristics import RBFChange

"""
Original tx:
   'hex_tx': '02000000000101e3f151d06777252729a38163b4b171f7d1aa858f126278852b1dd30d35d1f46c0100000000fdffffff0230e6020000000000160014b8f3e08162ae04338a7e0dae257cc98df5db0e4ef0a70300000000001600142500ef0b70ecfcfe2c9ff6ee474cc63dab149b7d0247304402207937320658adc8b65d128f244d81bd32b22b6be66e07bb37f469ccb66a6040d302206311226d9521466f61c1a3a4c82ddb63cdfd75ef0d83245b4faa0eac00c885d30121037a9068bded09cb8f8df42e6c5b5f44dc978d2377fafb36bd65b77adc1220c35715ae0d00',
   'txid': '0671a6a6f9385a0886cfcada90e74d18cd153956295ac4a5c3c7b0847f7e6bf1',
   'vin': '[{"txid": "6cf4d1350dd31d2b857862128f85aad1f771b1b46381a32927257767d051f1e3", "vout": 1, "scriptSig": {"asm": "", "hex": ""}, "txinwitness": ["304402207937320658adc8b65d128f244d81bd32b22b6be66e07bb37f469ccb66a6040d302206311226d9521466f61c1a3a4c82ddb63cdfd75ef0d83245b4faa0eac00c885d301", "037a9068bded09cb8f8df42e6c5b5f44dc978d2377fafb36bd65b77adc1220c357"], "sequence": 4294967293}]',
   'hash': '0c1958ca58ed40df20ba304335454568630a5e9cc40336f1c957faeb75163d8b',
   'vout': '[{"value": 0.0019, "n": 0, "scriptPubKey": {"asm": "0 b8f3e08162ae04338a7e0dae257cc98df5db0e4e", "desc": "addr(bc1qhre7pqtz4czr8zn7pkhz2lxf3h6akrjwj5t8cz)#hwvgd2hq", "hex": "0014b8f3e08162ae04338a7e0dae257cc98df5db0e4e", "address": "bc1qhre7pqtz4czr8zn7pkhz2lxf3h6akrjwj5t8cz", "type": "witness_v0_keyhash"}}, {"value": 0.002396, "n": 1, "scriptPubKey": {"asm": "0 2500ef0b70ecfcfe2c9ff6ee474cc63dab149b7d", "desc": "addr(bc1qy5qw7zmsan70utyl7mhywnxx8k43fxma37rpmx)#m0z70z86", "hex": "00142500ef0b70ecfcfe2c9ff6ee474cc63dab149b7d", "address": "bc1qy5qw7zmsan70utyl7mhywnxx8k43fxma37rpmx", "type": "witness_v0_keyhash"}}]',

Replacement tx:
   'previous': '0671a6a6f9385a0886cfcada90e74d18cd153956295ac4a5c3c7b0847f7e6bf1',
   'hex_tx': '02000000000101e3f151d06777252729a38163b4b171f7d1aa858f126278852b1dd30d35d1f46c0100000000fdffffff0230e6020000000000160014b8f3e08162ae04338a7e0dae257cc98df5db0e4e28a70300000000001600142500ef0b70ecfcfe2c9ff6ee474cc63dab149b7d0247304402206787641d860b9057fc91720a24d515472e7a3e0dbc4e15335cce692f4a837ed702206b209b582cea2ce35901b2069928657eb0e019c2a9e1287d068a3eed734b0d690121037a9068bded09cb8f8df42e6c5b5f44dc978d2377fafb36bd65b77adc1220c35715ae0d00',
   'txid': '21b577e3c8aa7e460aaa933164b0d13ced505f3e656eef6f4f77495cccb51006',
   'vin': '[{"txid": "6cf4d1350dd31d2b857862128f85aad1f771b1b46381a32927257767d051f1e3", "vout": 1, "scriptSig": {"asm": "", "hex": ""}, "txinwitness": ["304402206787641d860b9057fc91720a24d515472e7a3e0dbc4e15335cce692f4a837ed702206b209b582cea2ce35901b2069928657eb0e019c2a9e1287d068a3eed734b0d6901", "037a9068bded09cb8f8df42e6c5b5f44dc978d2377fafb36bd65b77adc1220c357"], "sequence": 4294967293}]',
   'hash': '9dd1cc7f10b6a2de55c6a25507db37da185fccb978d938633a8e7bf4eb658abf',
   'vout': '[{"value": 0.0019, "n": 0, "scriptPubKey": {"asm": "0 b8f3e08162ae04338a7e0dae257cc98df5db0e4e", "desc": "addr(bc1qhre7pqtz4czr8zn7pkhz2lxf3h6akrjwj5t8cz)#hwvgd2hq", "hex": "0014b8f3e08162ae04338a7e0dae257cc98df5db0e4e", "address": "bc1qhre7pqtz4czr8zn7pkhz2lxf3h6akrjwj5t8cz", "type": "witness_v0_keyhash"}}, {"value": 0.002394, "n": 1, "scriptPubKey": {"asm": "0 2500ef0b70ecfcfe2c9ff6ee474cc63dab149b7d", "desc": "addr(bc1qy5qw7zmsan70utyl7mhywnxx8k43fxma37rpmx)#m0z70z86", "hex": "00142500ef0b70ecfcfe2c9ff6ee474cc63dab149b7d", "address": "bc1qy5qw7zmsan70utyl7mhywnxx8k43fxma37rpmx", "type": "witness_v0_keyhash"}}]'
"""

if __name__ == "__main__":
    tx_original = Tx.from_raw("02000000000101e3f151d06777252729a38163b4b171f7d1aa858f126278852b1dd30d35d1f46c0100000000fdffffff0230e6020000000000160014b8f3e08162ae04338a7e0dae257cc98df5db0e4ef0a70300000000001600142500ef0b70ecfcfe2c9ff6ee474cc63dab149b7d0247304402207937320658adc8b65d128f244d81bd32b22b6be66e07bb37f469ccb66a6040d302206311226d9521466f61c1a3a4c82ddb63cdfd75ef0d83245b4faa0eac00c885d30121037a9068bded09cb8f8df42e6c5b5f44dc978d2377fafb36bd65b77adc1220c35715ae0d00")
    tx_replacement = Tx.from_raw("02000000000101e3f151d06777252729a38163b4b171f7d1aa858f126278852b1dd30d35d1f46c0100000000fdffffff0230e6020000000000160014b8f3e08162ae04338a7e0dae257cc98df5db0e4e28a70300000000001600142500ef0b70ecfcfe2c9ff6ee474cc63dab149b7d0247304402206787641d860b9057fc91720a24d515472e7a3e0dbc4e15335cce692f4a837ed702206b209b582cea2ce35901b2069928657eb0e019c2a9e1287d068a3eed734b0d690121037a9068bded09cb8f8df42e6c5b5f44dc978d2377fafb36bd65b77adc1220c35715ae0d00")
    tx_replacement.import_original_tx(tx_original)
    result = RBFChange.apply(tx_replacement)
    print(result)
    if result['result']:
    	assert result['address'] == "bc1qy5qw7zmsan70utyl7mhywnxx8k43fxma37rpmx", "The address returnd is not the correct one!"
        print("Test was succesfull")
    else:
        print("ERROR: Test failed unexpectadly")
