use bitcoin::AddressType;

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct UncompressPublicKeyChange;

impl Heuristic for UncompressPublicKeyChange {
    fn name(&self) -> String {
        return "UncompressPublicKeyChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::MediumHigh
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false);

        let actual_has_uncompressed: bool = has_uncompressed_public_keys(tx);

        for fut in tx.future_txs().unwrap().iter() {
            println!("{}", has_uncompressed_public_keys(fut));
        }

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok(actual_has_uncompressed == has_uncompressed_public_keys(future_tx))
        })
        .collect::<Result<Vec<bool>, AppError>>()?;

        Ok(possible_change)
    }
}

fn parse_script_items(bytes: &[u8]) -> Vec<&[u8]> {
    let mut items: Vec<&[u8]> = Vec::new();
    let mut i = 0;

    while i < bytes.len() {
        let push_len = bytes[i] as usize;
        i += 1;
        
        if i + push_len > bytes.len() {
            break; 
        }
        
        items.push(&bytes[i..i + push_len]);
        i += push_len;
    }

    items
}

fn is_uncompressed_pubkey(bytes: &[u8]) -> bool {
    bytes.len() == 65 && bytes.first() == Some(&0x04)
}


fn has_uncompressed_public_keys(tx: &Tx) -> bool {
    let input_types = match tx.inputs_types() {
        Ok(types) => types,
        Err(_) => return false,
    };

    let script_sigs = tx.inputs_scriptsig();

    for (idx, input_type) in input_types.iter().enumerate() {
        match input_type {
            // P2PKH — pubkey is second item in scriptSig
            AddressType::P2pkh => {
                let script_sig = match script_sigs.get(idx) {
                    Some(s) => s,
                    None => continue,
                };

                let items = parse_script_items(script_sig.as_bytes());

                if items.len() >= 2 && is_uncompressed_pubkey(items[1]) {
                    return true;
                }
            },

            // P2SH — pubkeys inside redeem script (last scriptSig item)
            AddressType::P2sh => {
                let script_sig = match script_sigs.get(idx) {
                    Some(s) => s,
                    None => continue,
                };

                let items = parse_script_items(script_sig.as_bytes());
                if let Some(redeem_script) = items.last() {
                    let inner_items = parse_script_items(redeem_script);
                    if inner_items.iter().any(|item| is_uncompressed_pubkey(item)) {
                        return true;
                    }
                }
            },

            // P2WPKH, P2WSH, P2TR — compressed keys enforced by protocol
            _ => continue,
        }
    }

    false
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_uncompressed_pubkey_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "2fb20b3eca06902bdfdfbda4bf7f03555325ea7886a0af9b2dc76324fe3e382a", 
            "118ffa26c1645625ae370b2b59054c5e966acb16e066e8caa5047f7b093734b3", 
        ];

        let expected_results = vec![
            vec![true, true],
            vec![false, true],
        ];

        run_heuristic_test(&UncompressPublicKeyChange, txids, expected_results, false)

    }
}