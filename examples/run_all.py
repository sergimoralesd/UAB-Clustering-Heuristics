"""
run_all.py
----------
Runnable example that exercises every heuristic in the uab_heuristics library.

Usage:
    python examples/run_all.py

The script uses three hard-coded raw transactions taken from the public
Bitcoin blockchain so it works out of the box without a local node.
"""

from pathlib import Path

try:
    from rust_tx_core import Tx
except ImportError:
    from uab_heuristics.core import Tx

from uab_heuristics.heuristics import (
    # Standalone
    ReusedAddressChange,
    AddressTypeChange,
    RoundedChange,
    SmallerOutputChange,
    OptimalChange,
    OneTimeChange,
    # Future-tx
    InputOrderChange,
    OutputOrderChange,
    LocktimeChange,
    FeeAbsoluteChange,
    FeeRelativeChange,
    VersionChange,
    SignalRBFChange,
    MultiSignatureChange,
    ConsistentAddressTypeChange,
    LowConfirmationChange,
    LowRChange,
    SegwitConformChange,
    FutureAddressReuse,
    # Combined (prev + future)
    UncompressPublicKeyChange,
    BackdatingChange,
    RoundedFiatChange,
    # Coinjoin
    MalformedCoinjoinChange,
)
from uab_heuristics.utils import get_collection_tx

# ---------------------------------------------------------------------------
# Sample transactions
# ---------------------------------------------------------------------------

# Three regular transactions used for standalone and combined heuristics
TX_A = {
    "tx_id": "252cab241aed16d68c4a01a09ee12349ef55147ebfd12746891ae50f149163e7",
    "tx_raw": (
        "010000000625dad429ca53220f72b1427602d70d8871fe463f2f50fc04cb8abaeb3e7edcd"
        "0000000004847304402205ab198d5a4958d764469337a301934085cb0fcca69ec202b26c9"
        "db81aaf6184002203355c91b427d689ac122185b37551347274ec8389aedc0897b8bbc259"
        "cddf8c501ffffffff026689a5b69ce3c797a16454ebb85749e0decac0fa5fabc446c5dafb"
        "55fa80aa010000008a473044022026470595ba2e3ad7705b2d14bfbbc9413ba9eb4b1e882"
        "5d4963a40f8cf103f0d0220512a0ce259f67ea8288dbc2cd8c0694e191f87a380052d0195"
        "097df052d32776014104855e4bc832b79334e195feb2702d7e731425312c78a366c4b32b9"
        "56027119ce9efb77ca50362d3067313306a46caabd384d42974d87efb92637027a596d502"
        "f3ffffffff7e7e921acf75b44e17bb5d2fd43436b2cfd5640de913ebb8c7a8fd4f2c060cff"
        "010000008a47304402207c5bc814620ffdf915020fed83a12df15349328776d9d93a6e2079"
        "723567147f022032ec5b3b23f024fda022f94047b14c681f8f878fe9aebb351f3297f29508"
        "a9da014104855e4bc832b79334e195feb2702d7e731425312c78a366c4b32b956027119ce9"
        "efb77ca50362d3067313306a46caabd384d42974d87efb92637027a596d502f3ffffffff28"
        "041e8e2afe03ef1db7217ac36cd3d7b8107068326b97af5a7859f95dea6c470000000049483"
        "045022100cfd7f7190bfebea6a2fd8ae5cfb86474532c67373d432b012ff77b1c721ccf7f02"
        "204b8736d56475afcb30f0d243e1f01016dbb8e5d6201d9f48ab89e5fd32807a2d01ffffffff"
        "1b822feb52a8be6ba5e212a1c9ab23c7b7eae7feb1e8c35414585c9df93db183010000008b48"
        "304502205e7bdb084b0c40659448265e125700d814efb408753da3464ef0da147a75bda9022100"
        "dccebd84de3dddaceb387ac6c192b0ea603a7b861eb24d10adc732ed80471daa014104855e4bc"
        "832b79334e195feb2702d7e731425312c78a366c4b32b956027119ce9efb77ca50362d30673133"
        "06a46caabd384d42974d87efb92637027a596d502f3ffffffff34089a63a08d7239fac0bce2295a"
        "5bfa728bdca030e8484bee29f0ee8c84d183000000008b483045022100da210601f7664307fa190"
        "883e6712f3ce4bc00cbfff8ab260fb7286be7d8714202201366ff439e2893da8899aee0266cd62"
        "c2797753d4894765551cc1bdf76bb6385014104855e4bc832b79334e195feb2702d7e731425312"
        "c78a366c4b32b956027119ce9efb77ca50362d3067313306a46caabd384d42974d87efb9263702"
        "7a596d502f3ffffffff020098a06b150000004341048f41cf5017db935e297a66b02796a1c377dc"
        "2eb790d61ea1dc4c9137a2fb1c9863032339d228ab424a5e4848673f176f58c8108673bc356cba"
        "69f68cb40629b5ac80841e00000000004341042f61a95bcf3a054e35dbc0cabe0aa6251b6ee3f6"
        "e74b0589561f0dfb5d025c41528fab4f71b347ec66bb8222813b1fd62325528d05a464b30995b1"
        "ac27e18dd8ac00000000"
    ),
}

# Transaction with known future-spending txids (for future-tx heuristics)
TX_FUTURE = {
    "tx_id": "8eabad99fe4607a1f4a7e2979d34e0c8cad0a36e41d8e68061457fbc535bbfeb",
    "tx_raw": (
        "0100000002aea7dfe9cfbe2d28ac53dc8ac2f6ea77b6f2e0397de01277234ac6be6150a431"
        "080000006a473044022028bbc2a4e6ba6f0bbbcceb8e9629e5464031145ad13aa4b0dbb843"
        "21a429e0e802206c4981d412a1671ddc35dc5b0b70c4b2b7a43bd6641ebf22f7b6828643962"
        "c6401210255c741304a8cf6a4a64cd49f27db5cfee89eb671a5ae2661a4c5aa8f87afab2cff"
        "ffffff93268f6a52bf8e521f47a8c574bc93798a11a7467447b7ddc70ee02a665ee2d9010000"
        "006a473044022005ab6e4cffa7fce1b6a193b170f84bdb16c3eadd120b1ad6efa88ca59f935"
        "d5d02207c40a5f6034a1b05aabadece6a47dfb70084d8ac0bb2bebb74a8c860372dffe80121"
        "02662eff4ced7133015a6fc1322aed949317756eb737b6857fd18778c8766bac33ffffffff02"
        "01672100000000001976a9145a4299fd379988a5f066aa35b3e7e54a0285d1ad88ac00a7e103"
        "000000001976a91425d31aa80e2a991034f4066f12900c4a6ce56c8988ac00000000"
    ),
    "future_txs": [
        "9aa9e5917c29d739c8f8c7c8c1580fdc7a2b701dcb756eb3b80bdc84bab69977",
        "1e53ae0cc698954d1036b2491c2f193be115194a1a34bc194a841bf6504874c5",
    ],
}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def run(label: str, heuristic, tx: "Tx", **kwargs):
    try:
        result = heuristic.apply(tx, **kwargs)
        if result["result"]:
            print(f"  ✓ {label:45s} change_vout={result['change_vout']}")
    except Exception as exc:
        print(f"  ! {label:45s} error: {exc}")


# ---------------------------------------------------------------------------
# 1. Standalone heuristics
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("1. STANDALONE HEURISTICS  (tx_raw only)")
print("=" * 60)

tx_a = Tx.from_raw(TX_A["tx_raw"])

run("ReusedAddressChange", ReusedAddressChange(), tx_a)
run("AddressTypeChange",   AddressTypeChange(),   tx_a)
run("SmallerOutputChange", SmallerOutputChange(), tx_a)
run("OptimalChange",       OptimalChange(),       tx_a)
run("OneTimeChange",       OneTimeChange(),       tx_a)

print("\n  -- RoundedChange sweep (n=2..7) --")
h_round = RoundedChange()
for n in range(2, 8):
    run(f"RoundedChange n={n}", h_round, tx_a, n=n)


# ---------------------------------------------------------------------------
# 2. Future-tx heuristics
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("2. FUTURE-TX HEURISTICS  (import_future_txs required)")
print("=" * 60)

tx_f = Tx.from_raw(TX_FUTURE["tx_raw"])
tx_f.import_future_txs(future_txids=TX_FUTURE["future_txs"])

for cls in [
    InputOrderChange, OutputOrderChange, LocktimeChange,
    FeeAbsoluteChange, FeeRelativeChange, VersionChange,
    SignalRBFChange, MultiSignatureChange, ConsistentAddressTypeChange,
    LowConfirmationChange, LowRChange, SegwitConformChange, FutureAddressReuse,
]:
    run(cls.__name__, cls(), tx_f)


# ---------------------------------------------------------------------------
# 3. Combined heuristics (prev + future)
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("3. PREV + FUTURE HEURISTICS  (import_previous_txs + import_future_txs)")
print("=" * 60)

tx_c = Tx.from_raw(TX_FUTURE["tx_raw"])
tx_c.import_previous_txs()
tx_c.import_future_txs(future_txids=TX_FUTURE["future_txs"])

run("UncompressPublicKeyChange", UncompressPublicKeyChange(), tx_c)
run("BackdatingChange",          BackdatingChange(),          tx_c)

print("\n  -- RoundedFiatChange sweep --")
h_fiat = RoundedFiatChange()
for currency in ["USD", "EUR", "GBP", "CAD", "CHF", "AUD", "JPY"]:
    for n in range(2, 8):
        run(f"RoundedFiatChange {currency} n={n}", h_fiat, tx_c,
            currency=currency, n=n)


# ---------------------------------------------------------------------------
# 4. Coinjoin heuristic
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("4. COINJOIN HEURISTIC  (from collection file)")
print("=" * 60)

collection_path = Path(__file__).resolve().parent.parent / "data" / "tx_collection.json"
if collection_path.exists():
    txs_cj = get_collection_tx(collection_path, ["coinjoin"])
    h_cj = MalformedCoinjoinChange()
    for entry in txs_cj:
        tx_cj = Tx.from_raw(entry["tx_raw"])
        result = h_cj.apply(tx_cj)
        short_id = entry["tx_id"][:20] + "..."
        if result["result"]:
            print(f"  ✓ {short_id}  change_vouts={result.get('change_vouts')}")
        else:
            print(f"  - {short_id}  not detected as coinjoin")
else:
    print("  (collection file not found — skipping coinjoin example)")

print("\nDone.")
