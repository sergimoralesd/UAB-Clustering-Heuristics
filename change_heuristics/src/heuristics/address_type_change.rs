use bitcoin::AddressType;

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct AddressTypeChange;

impl Heuristic for AddressTypeChange {
    fn name(&self) -> &str {
        "AddressTypeChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::Low
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        self.check_requirements(tx, false);

        let input_types: Vec<AddressType> = tx.inputs_types()?;
        let output_types: Vec<AddressType> = tx.outputs_types()?;

        let mut possible_change: Vec<bool> = Vec::new();
        for output_type in output_types {
            if input_types.contains(&output_type) {
                possible_change.push(true);
            }
            else {
                possible_change.push(false);
            }
        }

        Ok(possible_change)
    }
}