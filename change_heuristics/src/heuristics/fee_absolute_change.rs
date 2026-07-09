use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct FeeAbsoluteChange;

impl Heuristic for FeeAbsoluteChange {
    fn name(&self) -> &str {
        "FeeAbsoluteChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::MediumHigh
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        self.check_requirements(tx, false);

        let actual_absolute_fee: u64 = tx.absolute_fee()?;
    
        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok(actual_absolute_fee == future_tx.absolute_fee()?)
        })
        .collect::<Result<Vec<bool>, AppError>>()?;

        Ok(possible_change)
    }
}