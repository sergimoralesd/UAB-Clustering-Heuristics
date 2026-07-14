use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct SmallerOuputChange;

impl Heuristic for SmallerOuputChange {
    fn name(&self) -> &str {
        "SmallerOuputChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::None
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false);

        let output_values = tx.outputs_values();
        let min_value: &u64 = output_values.iter().min().unwrap();
        let possible_change: Vec<bool> = tx.outputs_values()
        .iter()
        .map(|value| value == min_value)
        .collect();

        Ok(possible_change)
    }
}