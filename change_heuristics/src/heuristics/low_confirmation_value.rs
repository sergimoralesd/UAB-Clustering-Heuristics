use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct LowConfirmationValue;

impl Heuristic for LowConfirmationValue {
    fn name(&self) -> &str {
        "LowConfirmationValue"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::HighIndexed
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        self.check_requirements(tx, true);

        let actual_block_height: usize = tx.block_height().unwrap();

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok((actual_block_height - future_tx.block_height().unwrap()) < 6)
        })
        .collect::<Result<Vec<bool>, AppError>>()?;

        Ok(possible_change)
    }
}