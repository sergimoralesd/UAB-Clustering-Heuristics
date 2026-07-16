use bitcoin::{Script, Witness};

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements, TxError};

use super::Heuristic; 

pub struct MultisignatureChange;

impl Heuristic for MultisignatureChange {
    fn name(&self) -> String{
        return "MultisignatureChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::MediumLow
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false);

        // use get_multisig_type which internally uses inputs_scriptsig/inputs_witness
        let multisig_types = get_multisig_type(tx, None);
        if multisig_types.len() != 1 {
            return Ok(vec![false; tx.output_count()]);
        }

        let multisig_type = &multisig_types[0];

        // use outputs_addresses() from your methods
        let outputs_addresses = tx.outputs_addresses()
            .map_err(AppError::Tx)?;

        // use future_txs() from your methods
        let future_txs = tx.future_txs()
            .ok_or(AppError::Tx(TxError::MissingFutureTxs(
                "import future txs before running the heuristic".to_string()
            )))?;

        let mut possible_change: Vec<bool> = vec![false; outputs_addresses.len()];

        for (vout_index, future_tx) in future_txs.iter().enumerate() {
            // use previous_txids() and prevouts() from your methods
            let spending_input_index = future_tx.previous_txids()
                .iter()
                .zip(future_tx.prevouts().iter())
                .enumerate()
                .find(|(_, (txid, vout))| {
                    **txid == tx.txid() && **vout == vout_index
                })
                .map(|(i, _)| i);

            let spending_input_index = match spending_input_index {
                Some(idx) => idx,
                None => continue,
            };

            let future_ms_type = get_multisig_type(future_tx, Some(spending_input_index));

            if future_ms_type.len() != 1 {
                continue;
            }

            if multisig_type == &future_ms_type[0] {
                possible_change[vout_index] = true;
            }
        }

        Ok(possible_change)
    }
}


fn decode_op_n(op: u8) -> Option<u8> {
    if op == 0x00 {
        return Some(0);
    }
    if (0x51..=0x60).contains(&op) {
        return Some(op - 0x50);
    }
    None
}

const OP_CHECKMULTISIG: u8 = 0xae;

fn get_multisig_type_from_input(script_sig: &Script, witness: &Witness) -> Option<String> {
    let redeem_script_bytes: Vec<u8> = if witness.is_empty() {
        // legacy — get last item from scriptSig
        let bytes = script_sig.as_bytes();
        if bytes.is_empty() {
            return None;
        }

        // parse scriptSig items and get last one
        let mut items: Vec<&[u8]> = Vec::new();
        let mut i = 0;
        while i < bytes.len() {
            let push_len = bytes[i] as usize;
            i += 1;
            if i + push_len > bytes.len() { break; }
            items.push(&bytes[i..i + push_len]);
            i += push_len;
        }

        items.last()?.to_vec()
    } else {
        witness.iter().last()?.to_vec()
    };

    if redeem_script_bytes.is_empty() {
        return None;
    }

    let mut opcodes: Vec<u8> = Vec::new();
    let mut op_checkmultisig_idx: Option<usize> = None;
    let mut i = 0;

    while i < redeem_script_bytes.len() {
        let byte = redeem_script_bytes[i];

        if byte >= 0x01 && byte <= 0x4b {
            let push_len = byte as usize;
            opcodes.push(byte);
            i += 1 + push_len;
            continue;
        }

        if byte == OP_CHECKMULTISIG {
            op_checkmultisig_idx = Some(opcodes.len());
        }

        opcodes.push(byte);
        i += 1;
    }

    let op_idx = op_checkmultisig_idx?;
    if op_idx < 2 { return None; }

    let m = decode_op_n(*opcodes.first()?)?;
    let n = decode_op_n(*opcodes.get(op_idx - 1)?)?;

    if m == 0 || n == 0 || m > n { return None; }

    Some(format!("{}-{}", m, n))
}


fn get_multisig_type(tx: &Tx, input_index: Option<usize>) -> Vec<String> {
    let script_sigs = tx.inputs_scriptsig();
    let witnesses = tx.inputs_witness();

    match input_index {
        // check specific input
        Some(idx) => {
            match (script_sigs.get(idx), witnesses.get(idx)) {
                (Some(script_sig), Some(witness)) => {
                    match get_multisig_type_from_input(script_sig, witness) {
                        Some(ms_type) => vec![ms_type],
                        None => vec![],
                    }
                },
                _ => vec![],
            }
        },

        // check all inputs and return unique types
        None => {
            let mut results: Vec<String> = script_sigs
                .iter()
                .zip(witnesses.iter())
                .filter_map(|(script_sig, witness)| {
                    get_multisig_type_from_input(script_sig, witness)
                })
                .collect();

            results.sort();
            results.dedup();
            results
        }
    }
}