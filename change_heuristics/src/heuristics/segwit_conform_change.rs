use bitcoin::{AddressType};

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct SegwitConformChange;

impl Heuristic for SegwitConformChange {
    fn name(&self) -> &str {
        "SegwitConformChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::MediumHigh
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false);

        let actual_is_segwit_conform: bool = is_segwit_conform(tx)?;

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok(actual_is_segwit_conform == is_segwit_conform(future_tx)?)
        })
        .collect::<Result<Vec<bool>, AppError>>()?;

        Ok(possible_change)
    }
}

fn is_segwit_conform(tx: &Tx) -> Result<bool, AppError> {
    let witness_types: Vec<AddressType> = vec![AddressType::P2wpkh, AddressType::P2wsh, AddressType::P2tr];

    let has_witness_inputs: bool = tx.inputs_types()?
    .iter()
    .any(|input_type| witness_types.contains(input_type));

    Ok(has_witness_inputs && tx.is_segwit())
}