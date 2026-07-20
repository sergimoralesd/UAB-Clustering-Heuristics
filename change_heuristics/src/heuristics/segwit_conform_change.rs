use bitcoin::{AddressType};

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct SegwitConformChange;

impl Heuristic for SegwitConformChange {
    fn name(&self) -> String {
        return "SegwitConformChange".to_string();
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_segwit_conform_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "9ba576707044407d0543c3060cafc4dd9320fb60e4e55940653863cc6f9baafa", 
            "f626b1aa370c29e39f44f1764b8026b8a868e7017b7a16630f871cdcd7c96958"
        ];

        let expected_results = vec![
            vec![true, true],
            vec![true, true]
        ];

        run_heuristic_test(&SegwitConformChange, txids, expected_results, false, false)

    }
}