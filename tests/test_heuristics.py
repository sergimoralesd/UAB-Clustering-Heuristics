from pathlib import Path

try:
    from rust_tx_core import Tx
except ImportError as e:
    print("Error")
    from uab_heuristics.core import Tx
from uab_heuristics.heuristics import *
from uab_heuristics.utils import get_collection_tx

BASE_DIR = Path(__file__).resolve().parent


def test_heuristic(txs, heuristic_cls, prev_tx=False, future_txs=False, currency=None, n=None):
    print("#" * 50)
    if isinstance(heuristic_cls, type):
        heuristic = heuristic_cls()
    else:
        heuristic = heuristic_cls
    print(f"Starting test with heuristic: {heuristic.name}")

    for tx in txs:
        tx_id = tx["tx_id"]
        tx_raw = tx["tx_raw"]
        try:
            print(f"Applying heuristic to tx: \n{tx_id}")
            tx_object = Tx.from_raw(tx_raw)
            if prev_tx:
                tx_object.import_previous_txs()
            if future_txs:
                tx_object.import_future_txs(future_txids=tx["future_txs"])
            
            if n and currency:
                result_reused_addr_change = heuristic.apply(tx_object, n=n, currency=currency)
            elif n:
                result_reused_addr_change = heuristic.apply(tx_object, n=n)
            else:
                result_reused_addr_change = heuristic.apply(tx_object)
            if result_reused_addr_change['result'] == True:
                print(f"Result from heurisitc: \n{result_reused_addr_change}")
        except Exception as e:
            print(e)
        print("-"*50)
    print("#" * 50)

if __name__ == "__main__":

    filename = BASE_DIR / "data" / "tx_collection.json"
    txs = get_collection_tx(filename, ["change_address"])
    txs_coinjoin = get_collection_tx(filename, ["coinjoin"])

    tx = {
        "tx_id" : "252cab241aed16d68c4a01a09ee12349ef55147ebfd12746891ae50f149163e7",
        "tx_raw" : "010000000625dad429ca53220f72b1427602d70d8871fe463f2f50fc04cb8abaeb3e7edcd0000000004847304402205ab198d5a4958d764469337a301934085cb0fcca69ec202b26c9db81aaf6184002203355c91b427d689ac122185b37551347274ec8389aedc0897b8bbc259cddf8c501ffffffff026689a5b69ce3c797a16454ebb85749e0decac0fa5fabc446c5dafb55fa80aa010000008a473044022026470595ba2e3ad7705b2d14bfbbc9413ba9eb4b1e8825d4963a40f8cf103f0d0220512a0ce259f67ea8288dbc2cd8c0694e191f87a380052d0195097df052d32776014104855e4bc832b79334e195feb2702d7e731425312c78a366c4b32b956027119ce9efb77ca50362d3067313306a46caabd384d42974d87efb92637027a596d502f3ffffffff7e7e921acf75b44e17bb5d2fd43436b2cfd5640de913ebb8c7a8fd4f2c060cff010000008a47304402207c5bc814620ffdf915020fed83a12df15349328776d9d93a6e2079723567147f022032ec5b3b23f024fda022f94047b14c681f8f878fe9aebb351f3297f29508a9da014104855e4bc832b79334e195feb2702d7e731425312c78a366c4b32b956027119ce9efb77ca50362d3067313306a46caabd384d42974d87efb92637027a596d502f3ffffffff28041e8e2afe03ef1db7217ac36cd3d7b8107068326b97af5a7859f95dea6c470000000049483045022100cfd7f7190bfebea6a2fd8ae5cfb86474532c67373d432b012ff77b1c721ccf7f02204b8736d56475afcb30f0d243e1f01016dbb8e5d6201d9f48ab89e5fd32807a2d01ffffffff1b822feb52a8be6ba5e212a1c9ab23c7b7eae7feb1e8c35414585c9df93db183010000008b48304502205e7bdb084b0c40659448265e125700d814efb408753da3464ef0da147a75bda9022100dccebd84de3dddaceb387ac6c192b0ea603a7b861eb24d10adc732ed80471daa014104855e4bc832b79334e195feb2702d7e731425312c78a366c4b32b956027119ce9efb77ca50362d3067313306a46caabd384d42974d87efb92637027a596d502f3ffffffff34089a63a08d7239fac0bce2295a5bfa728bdca030e8484bee29f0ee8c84d183000000008b483045022100da210601f7664307fa190883e6712f3ce4bc00cbfff8ab260fb7286be7d8714202201366ff439e2893da8899aee0266cd62c2797753d4894765551cc1bdf76bb6385014104855e4bc832b79334e195feb2702d7e731425312c78a366c4b32b956027119ce9efb77ca50362d3067313306a46caabd384d42974d87efb92637027a596d502f3ffffffff020098a06b150000004341048f41cf5017db935e297a66b02796a1c377dc2eb790d61ea1dc4c9137a2fb1c9863032339d228ab424a5e4848673f176f58c8108673bc356cba69f68cb40629b5ac80841e00000000004341042f61a95bcf3a054e35dbc0cabe0aa6251b6ee3f6e74b0589561f0dfb5d025c41528fab4f71b347ec66bb8222813b1fd62325528d05a464b30995b1ac27e18dd8ac00000000",
        }
    tx2 = {
        "tx_id" : "a2e79986c21d73a2ff1606c5e30946ca870ac62736a8e52969cd6a3e1edf93d5",
        "tx_raw" : "010000000330ba615b26a8a875ff58ed776066d60aa826c35eb3ffea86f430a4db2f708e28010000008a47304402205cb7a2e7947035e232c390305118d2c41899a9d7622cc3bfbd986d0c1871565e0220320e8135e9f8c63b4326fe103d9c080e0c2cc1321547627f1c7ea792aba43eb8014104dc332db6dcdc9841f6876aa7b49c0ba87a96c8d7d5737ea3bbb2d9da5ec546ecc75fb7def3315223a681163cbeccf5b6a99e06d7c5abaa4dec40173cfd852f06ffffffff5684a403be9803ab9fb22c1b169e1a452243cf5827ed1c0df2321da6d65455d70100000049483045022100b2f49c1994d912d0347158d10ab9cd35e41ff34a86af41f9a02e0ac8140e6861022026954046c0985b35719d7f0ced08fbb8620395256117a12613278bf2d2642eec01ffffffffec37e88484a81d6aa907ccdff294c96fcd37a5ebdbcdf4061c3fb8450dceb745000000004948304502202b8d13a67a54c7245e858cea5b259b38ba65d30b81306e367b33f9df190556a4022100c03b407d68dcb039d9cdc8f3797b235d3fb0720d5fce65088b7dafb06a2c490f01ffffffff020065cd1d000000004341041e9d2988ca48c111bd52634888634d2157c5b365b8d5b55573a2cb89960fbc3f3530f5e25c52d993b36e3edce488fd07b2b02c59bff562f152afa2958054935fac00093d0000000000434104758d2063651f193e80b192cbc0cb194e0ffd1c0e3a6bb393eef6828870fe68a5c85f768bf299cffce5191241bc57770671f2568ce5c831559d4ec65dc8208254ac00000000",
        }
    tx3 = {
        "tx_id" : "47f179ea04b09ebfeb8572b6165e5a025e58b3c25bc89a5effb0dc3d0b9d5de8",
        "tx_raw" : "01000000047869f2733f6db32d9436e8eca65bc38f8e630316beb5047c3fb2054afcc99131010000008b48304502205d3fe3d3757943d06d1925f5ec5037ac434796901748f6e0fc62d5c51b1423ea022100fdef384994c9d585c80ad833f20d9ca1cbd22369b7186275f83b3f6d0f4ecdb401410410fd878036fb88fb8a2bc45ca454da43a75e9da972872268f6c5cdb77ed5e3e5538a24c14364763101bb72acc1619b531640142a356f87bd933b39439bf2c1a5ffffffffa8102f1d6b83d72b32f2a1dfc74ddd4ed993907b3bd7bec93435aa218abd246c0000000049483045022076be1f935ff44122ae4c7a0f6bb24f7975b83f14eb30b6ae4593e57f4c287614022100ef3ceecbbe7ac6e0b8d32dedc907f05d7541c1e19e78b1a36eac1201193f3ae901ffffffff88faeb5c03c6aa9b3fdf0671ddc76c42fccfaf772edebb490bb97c0c8867adc5010000008c493046022100992f6c93d9a3f8a9467db30dfea13b255a4f2a7e10f8df79eac574b05b165526022100bfac3ca66909cac92613fb366555b48bf4754665cb798ce0ec6f98addcb7b4cb014104f50fcea5703a3868240518ecf66cacc544b5dbdc51847959c5ef3052f6ab0d29af339788c23c6c0e1d58fe61dae2724dc45d1cb5e9a4f8a056d74eea2dd516bbffffffffd0d0707ffb69d46466adba2b2371922e54f1754e5c4cd41beb940431d27090de010000008a4730440220274c0e866dc1b35118352e2297c1a03a73e6d0acc2b85b8490b8476e57030d37022020587f2ad8b211a4e178a92e3f0372ccd333ef2c735e462f1d8bc7eca0b2606b014104dc332db6dcdc9841f6876aa7b49c0ba87a96c8d7d5737ea3bbb2d9da5ec546ecc75fb7def3315223a681163cbeccf5b6a99e06d7c5abaa4dec40173cfd852f06ffffffff0200a3e11100000000434104d92011aafebdb12947281b390bcdc545d95e7313d69268c35796bfdeed2c66b24ddb44b6330b2882eebb8bd719cfac4ba88c22cb8a4ba18573a78b2cb51cf29cac40420f00000000004341041a1a79ac01078970799fa8d0af2ae99b581e473ff5e1da4aa2d78d1ff59b406557d61aea98d41d92a6568547cc45644dda02536aedfa7e8c7f39420a95a6cd91ac00000000",
        }
    txs = [tx, tx2, tx3]

    test_heuristic(txs, ReusedAddressChange)
    
    #test_heuristic(txs, AddressTypeChange)

    #for n in range(2, 8):
    #    print(f"-- N:{n} --")
    #    test_heuristic(txs, RoundedChange, n=n)

    #test_heuristic(txs, SmallerOutputChange)

    #test_heuristic(txs, OptimalChange)

    tx = {
        "tx_id" : "8eabad99fe4607a1f4a7e2979d34e0c8cad0a36e41d8e68061457fbc535bbfeb",
        "tx_raw" : "0100000002aea7dfe9cfbe2d28ac53dc8ac2f6ea77b6f2e0397de01277234ac6be6150a431080000006a473044022028bbc2a4e6ba6f0bbbcceb8e9629e5464031145ad13aa4b0dbb84321a429e0e802206c4981d412a1671ddc35dc5b0b70c4b2b7a43bd6641ebf22f7b6828643962c6401210255c741304a8cf6a4a64cd49f27db5cfee89eb671a5ae2661a4c5aa8f87afab2cffffffff93268f6a52bf8e521f47a8c574bc93798a11a7467447b7ddc70ee02a665ee2d9010000006a473044022005ab6e4cffa7fce1b6a193b170f84bdb16c3eadd120b1ad6efa88ca59f935d5d02207c40a5f6034a1b05aabadece6a47dfb70084d8ac0bb2bebb74a8c860372dffe8012102662eff4ced7133015a6fc1322aed949317756eb737b6857fd18778c8766bac33ffffffff0201672100000000001976a9145a4299fd379988a5f066aa35b3e7e54a0285d1ad88ac00a7e103000000001976a91425d31aa80e2a991034f4066f12900c4a6ce56c8988ac00000000",
        "future_txs" : ["9aa9e5917c29d739c8f8c7c8c1580fdc7a2b701dcb756eb3b80bdc84bab69977", "1e53ae0cc698954d1036b2491c2f193be115194a1a34bc194a841bf6504874c5"]
    }
    txs = [tx]
    #test_heuristic(txs, InputOrderChange, future_txs=True)
    
    #test_heuristic(txs, OutputOrderChange, future_txs=True)

    #test_heuristic(txs, LocktimeChange, future_txs=True)

    #test_heuristic(txs, FeeAbsoluteChange, future_txs=True)

    #test_heuristic(txs, FeeRelativeChange, future_txs=True)

    #test_heuristic(txs, VersionChange, future_txs=True)

    #test_heuristic(txs, SignalRBFChange, future_txs=True)

    #test_heuristic(txs, ConsistentAddressTypeChange, future_txs=True)

    #test_heuristic(txs, LowConfirmationChange, future_txs=True) 
    
    #test_heuristic(txs, LowRChange, future_txs=True)  

    test_heuristic(txs, MultiSignatureChange, future_txs=True)

    #test_heuristic(txs_coinjoin, MalformedCoinjoinChange)

    #test_heuristic(txs, OneTimeChange)
    
    #test_heuristic(txs, FutureAddressReuse)

    #test_heuristic(txs, SegwitConformChange, future_txs=True)
    
    currencies = ['USD', 'EUR', 'GBP', 'CAD', 'CHF', 'AUD', 'JPY']
    
    #for currency in currencies:
    #    print(f"-- Currency:{currency} --")
    #    for n in range(2, 8):
    #        print(f"-- N:{n} --")
    #        test_heuristic(txs, RoundedFiatChange, currency=currency, n=n)

    #test_heuristic(txs, UncompressPublicKeyChange, prev_tx=True, future_txs=True)

    #test_heuristic(txs, BackdatingChange, prev_tx=True, future_txs=True)

