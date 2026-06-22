"""
Wallet fingerprinting features.

Each function takes a `Tx` object and returns a single structural signal that
helps identify which software wallet created the transaction. Functions reuse
the existing `uab_heuristics.utils` primitives where they already exist
(signals_rbf, low_r_only, get_output_order, ...) and implement the rest here.

Features split into two groups:
  - NO_PREV   : computable from the transaction alone.
  - NEED_PREV : require the previous transactions (input values/types/addresses)
                to be resolved via `tx.import_previous_txs(...)`.
"""

from binascii import unhexlify
from decimal import Decimal

from ..utils import signals_rbf, get_output_order
# NOTE: utils.low_r_only is buggy for segwit inputs (returns False for any
# witness input regardless of the signature), so it conflates "fully-legacy" with
# "low-R". We use the corrected `low_r_only` defined below instead.

# Dust threshold in satoshis (standard Bitcoin Core relay limit for P2PKH-ish).
DUST_SATS = 546

# Standard output script types, using the short names returned by get_address_type().
STANDARD_TYPES = {"p2pkh", "p2sh", "p2wpkh", "p2wsh", "p2tr"}


# ──────────────────────────────────────────────────────────────────────────────
#  NO_PREV features
# ──────────────────────────────────────────────────────────────────────────────

def low_r_only(tx) -> bool:
    """
    True if every ECDSA signature in the inputs is low-R (the r value is encoded
    in <= 32 bytes). Low-R grinding is a wallet fingerprint (Bitcoin Core, BDK,
    Electrum and others grind to a low r).

    Works for both witness (p2wpkh, p2sh-p2wpkh) and legacy (p2pkh) inputs.
    Taproot (Schnorr, 64-byte) signatures have no low-R concept and are skipped.

    DER signature layout (hex): 30 <total_len> 02 <r_len> <r...> 02 <s_len> <s...> <sighash>
    so the r length byte is at hex offset [6:8].
    """
    for i in range(tx.input_count):
        wit = tx.inputs_witness[i]
        sig = None
        if wit:
            # Find the DER signature among the witness items (starts with '30').
            # Taproot key-path spends carry a 64-byte Schnorr sig instead -> skipped.
            for item in wit:
                if item.startswith("30"):
                    sig = item
                    break
        else:
            ss = tx.inputs_scriptSig[i]
            if ss and len(ss) >= 4 and ss[2:4] == "30":
                sig = ss[2:]  # skip the 1-byte push opcode before the DER sig
        if sig and len(sig) >= 8:
            try:
                if int(sig[6:8], 16) > 32:
                    return False
            except ValueError:
                pass
    return True


def anti_fee_sniping(tx) -> int:
    """
    Anti-fee-sniping flag based on locktime only (no block-height lookup).
      -1 = locktime is 0 (no anti-fee-sniping)
       1 = locktime != 0 (anti-fee-sniping active)
    """
    return 1 if tx.locktime > 0 else -1


def nonstandard_sighash(tx) -> bool:
    """True if any input uses a sighash type other than SIGHASH_ALL (0x01)."""
    for i in range(tx.input_count):
        sig = None
        wit = tx.inputs_witness[i]
        if wit:
            for item in wit:
                if len(item) >= 2 and item.startswith("30"):
                    sig = item
                    break
        else:
            ss_hex = tx.inputs_scriptSig[i]
            if ss_hex and ss_hex.startswith("30"):
                try:
                    sig_len = int(ss_hex[0:2], 16)
                    sig = ss_hex[2:2 + sig_len * 2]
                except Exception:
                    pass
        if sig and len(sig) >= 2 and sig[-2:].lower() != "01":
            return True
    return False


def unusual_outputs(tx) -> bool:
    """True if any output has a non-standard script type."""
    return any(t not in STANDARD_TYPES for t in tx.outputs_types)


def dust_on_outputs(tx) -> bool:
    """True if any output value is dust (<= 546 sat)."""
    return any(0 < v <= DUST_SATS for v in tx.outputs_values)


def input_order_bip69(tx) -> bool:
    """True if inputs are ordered by BIP69 (lexicographic prevout). No prev_tx needed."""
    if tx.input_count <= 1:
        return True
    try:
        prevouts = tx.prevouts
        aux = []
        for p in prevouts:
            txid_hex, vout_str = p.split(":")
            aux.append((unhexlify(txid_hex), int(vout_str)))
        sorted_bin = sorted(aux, key=lambda x: (x[0], x[1]))
        sorted_hex = [f"{t.hex()}:{v}" for t, v in sorted_bin]
        return sorted_hex == prevouts
    except Exception:
        return False


def output_structure(tx, change_idx: int) -> list[str]:
    """Output layout flags: SINGLE / DOUBLE / MULTI / CHANGE_LAST / BIP69."""
    n = tx.output_count
    if n == 1:
        return ["SINGLE"]
    flags = ["DOUBLE" if n == 2 else "MULTI"]
    if change_idx >= 0 and change_idx == n - 1:
        flags.append("CHANGE_LAST")
    vals = tx.outputs_values
    hexes = tx.outputs_scriptPubKey
    unique = len(set(vals)) == len(vals)
    if unique:
        bip69 = sorted(vals) == vals
    else:
        paired = list(zip(vals, hexes))
        bip69 = sorted(paired, key=lambda x: (x[0], bytes.fromhex(x[1]))) == paired
    if bip69:
        flags.append("BIP69")
    return flags


# ──────────────────────────────────────────────────────────────────────────────
#  NEED_PREV features
# ──────────────────────────────────────────────────────────────────────────────

def compressed_keys(tx) -> bool:
    """True if all public keys in the inputs are compressed (33 bytes)."""
    for i in range(tx.input_count):
        wit = tx.inputs_witness[i]
        if wit and len(wit) >= 2:
            pubkey = wit[1]
            if len(pubkey) > 1 and pubkey[1] == '4':
                return False
        else:
            ss = tx.inputs_scriptSig[i]
            if ss:
                parts = ss.split()
                for part in parts:
                    if len(part) == 130 and part.startswith('04'):
                        return False
    return True


def multi_type_inputs(tx) -> bool:
    """True if the transaction spends inputs of more than one script type."""
    return len(set(tx.inputs_types)) > 1


def dust_on_inputs(tx) -> bool:
    """True if any spent input value is dust (<= 546 sat). Requires prev_txs."""
    return any(0 < v <= DUST_SATS for v in tx.inputs_values)


def address_reuse(tx) -> bool:
    """True if any output address also appears among the input addresses. Requires prev_txs."""
    in_addrs = set(a for a in tx.inputs_addresses if a)
    out_addrs = set(a for a in tx.outputs_addresses if a)
    return bool(in_addrs & out_addrs)


def fee_rate_precision(tx) -> str | None:
    """
    LOW / MEDIUM / HIGH based on the number of significant decimals of fee/weight.
    Requires prev_txs (to know input values).
    """
    try:
        total_out = Decimal(str(sum(tx.outputs_values)))
        total_in = Decimal(str(sum(tx.inputs_values)))
        fee = (total_in - total_out) / Decimal(str(tx.weight))
        fee = fee.quantize(Decimal('0.00000001'))
        s = format(fee, 'f')
        decimals = s.split('.')[1] if '.' in s else ''
        nonzero = sum(1 for d in decimals if d != '0')
        if nonzero <= 1:
            return "LOW"
        if nonzero <= 3:
            return "MEDIUM"
        return "HIGH"
    except Exception:
        return None


def change_type_matched_inputs(tx, change_idx: int) -> int:
    """
    Relationship between the change output type and the input/output types.
      2 = inconclusive (no known change)
      1 = change type matches the inputs
     -1 = change type matches the other outputs
      0 = matches both or neither
    Requires prev_txs.
    """
    if change_idx < 0 or change_idx >= tx.output_count:
        return 2
    change_type = tx.outputs_types[change_idx]
    in_types = tx.inputs_types
    out_types = [t for i, t in enumerate(tx.outputs_types) if i != change_idx]
    in_match = change_type in in_types
    out_match = change_type in out_types
    if in_match and out_match:
        return 0
    if in_match:
        return 1
    if out_match:
        return -1
    return 0


def input_order_full(tx) -> list[str]:
    """
    Input ordering flags: SINGLE / ASCENDING / DESCENDING / BIP69 / UNKNOWN.
    Requires prev_txs for the value-based checks.
    """
    if tx.input_count == 1:
        return ["SINGLE"]
    flags = []
    vals = tx.inputs_values
    if sorted(vals) == vals:
        flags.append("ASCENDING")
    if sorted(vals, reverse=True) == vals:
        flags.append("DESCENDING")
    if input_order_bip69(tx):
        flags.append("BIP69")
    return flags or ["UNKNOWN"]


# ──────────────────────────────────────────────────────────────────────────────
#  Feature catalogue + extractor
# ──────────────────────────────────────────────────────────────────────────────

# Features computable from the transaction alone.
FEATURES_NO_PREV = [
    "version", "is_segwit", "locktime", "anti_fee_sniping",
    "input_count", "output_count",
    "signals_rbf", "low_r_only", "nonstandard_sighash",
    "output_order", "output_types", "output_structure",
    "input_order_bip69", "unusual_outputs", "dust_on_outputs",
]

# Features that require the previous transactions to be resolved.
FEATURES_NEED_PREV = [
    "input_types", "compressed_keys", "multi_type_inputs",
    "input_order", "address_reuse",
    "dust_on_inputs", "fee_rate_precision", "change_type_matched_inputs",
]

ALL_FEATURES = FEATURES_NO_PREV + FEATURES_NEED_PREV


def extract_features(tx, change_idx: int = -1, has_prev: bool = False) -> dict:
    """
    Extract every fingerprinting feature for a transaction.

    :param tx: a `Tx` instance.
    :param change_idx: known change output index, or -1 if unknown.
    :param has_prev: whether `tx` has its previous transactions resolved. When
                     False, the NEED_PREV features are returned as None.
    :return: dict mapping feature name -> value.
    """
    s = {}

    # — no prev_tx needed —
    s["version"] = tx.version
    s["is_segwit"] = tx.is_segwit
    s["locktime"] = tx.locktime
    s["anti_fee_sniping"] = anti_fee_sniping(tx)
    s["input_count"] = tx.input_count
    s["output_count"] = tx.output_count

    try: s["signals_rbf"] = signals_rbf(tx)
    except Exception: s["signals_rbf"] = None

    try: s["low_r_only"] = low_r_only(tx)
    except Exception: s["low_r_only"] = None

    try: s["nonstandard_sighash"] = nonstandard_sighash(tx)
    except Exception: s["nonstandard_sighash"] = None

    try: s["output_order"] = get_output_order(tx)
    except Exception: s["output_order"] = None

    try: s["output_types"] = "|".join(tx.outputs_types)
    except Exception: s["output_types"] = None

    try: s["output_structure"] = "|".join(output_structure(tx, change_idx))
    except Exception: s["output_structure"] = None

    try: s["input_order_bip69"] = input_order_bip69(tx)
    except Exception: s["input_order_bip69"] = None

    try: s["unusual_outputs"] = unusual_outputs(tx)
    except Exception: s["unusual_outputs"] = None

    try: s["dust_on_outputs"] = dust_on_outputs(tx)
    except Exception: s["dust_on_outputs"] = None

    # — need prev_txs —
    if has_prev:
        try: s["input_types"] = "|".join(tx.inputs_types)
        except Exception: s["input_types"] = None

        try: s["compressed_keys"] = compressed_keys(tx)
        except Exception: s["compressed_keys"] = None

        try: s["multi_type_inputs"] = multi_type_inputs(tx)
        except Exception: s["multi_type_inputs"] = None

        try: s["input_order"] = "|".join(input_order_full(tx))
        except Exception: s["input_order"] = None

        try: s["address_reuse"] = address_reuse(tx)
        except Exception: s["address_reuse"] = None

        try: s["dust_on_inputs"] = dust_on_inputs(tx)
        except Exception: s["dust_on_inputs"] = None

        try: s["fee_rate_precision"] = fee_rate_precision(tx)
        except Exception: s["fee_rate_precision"] = None

        try: s["change_type_matched_inputs"] = change_type_matched_inputs(tx, change_idx)
        except Exception: s["change_type_matched_inputs"] = 2
    else:
        for f in FEATURES_NEED_PREV:
            s[f] = None

    return s
