use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct UncompressPublicKeyChange;

impl Heuristic for UncompressPublicKeyChange {
    fn name(&self) -> &str {
        "UncompressPublicKeyChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::MediumHigh
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false);

        let actual_has_uncompressed: bool = has_uncompressed_public_keys(tx);

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok(actual_has_uncompressed == has_uncompressed_public_keys(future_tx))
        })
        .collect::<Result<Vec<bool>, AppError>>()?;

        Ok(possible_change)
    }
}

fn has_uncompressed_public_keys(tx: &Tx) -> bool {
    for scriptsig in tx.inputs_scriptsig().iter() {
        if scriptsig.is_empty() {
            //we return early false because if scriptsig is empty it means it has segwit
            return false;
        }
        let scriptsig_bytes = scriptsig.as_bytes();
        let mut i = 0;
        let mut items: Vec<&[u8]> = Vec::new();

        // parse all scriptSig items
        while i < scriptsig_bytes.len() {
            let push_len = scriptsig_bytes[i] as usize;
            i += 1;
            if i + push_len > scriptsig_bytes.len() { break; }
                items.push(&scriptsig_bytes[i..i + push_len]);
                i += push_len;
            }


        for item in &items {
            // check if item is uncompressed pubkey
            if item.len() == 65 && item.first() == Some(&0x04) {
                return true;
            }

            // check if item is a redeem script (P2SH-P2MS)
            // redeem script contains pubkeys inside it
            if item.first() == Some(&0x52) ||  // OP_2
                item.first() == Some(&0x53) ||  // OP_3
                item.first() == Some(&0x51) {   // OP_1
                // parse the redeem script to find pubkeys
                let mut j = 1;  // skip OP_n
                while j < item.len() {
                    let inner_push = item[j] as usize;
                    j += 1;
                    if j + inner_push > item.len() { break; }
                    let inner_item = &item[j..j + inner_push];
                    
                    // check if inner item is uncompressed pubkey
                    if inner_item.len() == 65 && inner_item.first() == Some(&0x04) {
                        return true;
                    }
                    j += inner_push;
                }
            }
        }
    }
        return false;
}