use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct RoundedChange {
    precision_parameter: u8,
}

impl RoundedChange {
    pub fn new(precision_parameter: u8) -> Self {
        RoundedChange { precision_parameter }
    }
}

impl Heuristic for RoundedChange {
    fn name(&self) -> &str {
        "RoundedChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::None
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false);

        let precision: u64 = 10 ^ self.precision_parameter as u64;
        let possible_change: Vec<bool> = tx.outputs_values()
        .iter()
        .map(|value| value % precision != 0)
        .collect();

        Ok(possible_change)
    }
}