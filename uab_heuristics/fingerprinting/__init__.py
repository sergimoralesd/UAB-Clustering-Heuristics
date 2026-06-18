"""
Wallet fingerprinting subpackage.

Structural signals that identify which software wallet created a transaction.
This integrates the features formerly maintained in the separate
UAB-Fingerprinting project, reusing the existing `uab_heuristics.utils`
primitives where they already existed.
"""

from .features import (
    extract_features,
    ALL_FEATURES,
    FEATURES_NO_PREV,
    FEATURES_NEED_PREV,
    # individual features
    anti_fee_sniping,
    nonstandard_sighash,
    unusual_outputs,
    dust_on_outputs,
    dust_on_inputs,
    input_order_bip69,
    input_order_full,
    output_structure,
    compressed_keys,
    multi_type_inputs,
    address_reuse,
    fee_rate_precision,
    change_type_matched_inputs,
    STANDARD_TYPES,
    DUST_SATS,
)

__all__ = [
    "extract_features",
    "ALL_FEATURES",
    "FEATURES_NO_PREV",
    "FEATURES_NEED_PREV",
    "anti_fee_sniping",
    "nonstandard_sighash",
    "unusual_outputs",
    "dust_on_outputs",
    "dust_on_inputs",
    "input_order_bip69",
    "input_order_full",
    "output_structure",
    "compressed_keys",
    "multi_type_inputs",
    "address_reuse",
    "fee_rate_precision",
    "change_type_matched_inputs",
    "STANDARD_TYPES",
    "DUST_SATS",
]
