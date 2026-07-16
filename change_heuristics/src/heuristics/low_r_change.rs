use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements, TxError};

use super::Heuristic; 

pub struct LowRChange;

impl Heuristic for LowRChange {
    fn name(&self) -> String {
        return "LowRChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::MediumLow
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, true, false);

        let actual_low_r: bool = is_low_r_only(tx)?;

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok(actual_low_r == is_low_r_only(future_tx)?)
        })
        .collect::<Result<Vec<bool>, AppError>>()?;

        Ok(possible_change)
    }
}

fn is_low_r_only(tx: &Tx) -> Result<bool, AppError> {
    for (script_sig, witness) in tx.inputs_scriptsig().iter().zip(tx.inputs_witness().iter()){
        if !witness.is_empty() {
            let items: Vec<&[u8]> = witness.iter().collect();

            match items.len() {
                1 => continue,

                // P2WPKH
                2 => {
                    let r_len = *items[0].get(3)
                        .ok_or(TxError::MalformedScript(
                            "P2WPKH signature too short".to_string()
                        ))?;
                    if r_len > 0x20 {
                        return Ok(false);
                    }
                },

                // P2WSH multisig
                n if n >= 4 => {
                    for sig in &items[1..items.len()-1] {
                        if sig.is_empty() { continue; }
                        let r_len = *sig.get(3)
                            .ok_or(TxError::MalformedScript(
                                "P2WSH signature too short".to_string()
                            ))?;
                        if r_len > 0x20 {
                            return Ok(false);
                        }
                    }
                },

                // P2TR
                _ => continue,
            }

        } else {
            let script_sig_bytes = script_sig.as_bytes();

            if script_sig_bytes.first() == Some(&0x00) {
                // P2SH multisig — parse each item dynamically
                let mut i = 1;  // skip OP_0
                while i < script_sig_bytes.len() {
                    let push_len = script_sig_bytes[i] as usize;
                    i += 1;

                    if i + push_len > script_sig_bytes.len() {
                        break;
                    }

                    let item = &script_sig_bytes[i..i + push_len];

                    // only check DER signatures (start with 0x30)
                    if item.first() == Some(&0x30) {
                        let r_len = *item.get(3)
                            .ok_or(TxError::MalformedScript(
                                "P2SH signature too short".to_string()
                            ))?;
                        if r_len > 0x20 {
                            return Ok(false);
                        }
                    }

                    i += push_len;
                }

            } else {
                // P2PKH
                let r_len = *script_sig_bytes.get(4)
                    .ok_or(TxError::MalformedScript(
                        "P2PKH scriptSig too short".to_string()
                    ))?;
                if r_len > 0x20 {
                    return Ok(false);
                }
            }
        }
    }

    Ok(true)
}
