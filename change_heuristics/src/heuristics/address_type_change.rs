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
        let _ = self.check_requirements(tx, false);

        let input_types: Vec<AddressType> = tx.inputs_types()?;

        let possible_change: Vec<bool> = tx.outputs_types()?
        .iter()
        .map(|out_type| input_types.contains(out_type))
        .collect();

        Ok(possible_change)
    }
}