use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct FeeRelativeChange;

impl Heuristic for FeeRelativeChange {
    fn name(&self) -> String {
        return "FeeRelativeChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::MediumHigh
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false)?;

        let actual_relative_fee: f32 = tx.relative_fee()?;
    
        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok(actual_relative_fee == future_tx.relative_fee()?)
        })
        .collect::<Result<Vec<bool>, AppError>>()?;

        Ok(possible_change)
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_fee_relative_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "40fe72e6cce5d7fa7c16a1714871215462956eef6138eeffa66338c9147c49f2", 
            "eadaf24d88bb6d6333f2f6df7ba3508130dd501981633750497043fd4eb66d21", 
            "f6ddb88c34223a4d9b358075e1201c0d9aa0b588bc35f87b390b8037564598cd"
        ];

        let expected_results = vec![
            vec![false, true],
            vec![true, true],
            vec![true, false]
        ];

        run_heuristic_test(&FeeRelativeChange, txids, expected_results, false, false)

    }
}