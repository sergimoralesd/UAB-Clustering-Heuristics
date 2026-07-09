use std::collections::HashMap;

use bitcoin::AddressType;

use crate::tx::Tx;
use crate::types::{AppError, HeuristicError, InputDataRequirements};

use super::Heuristic; 

pub struct ConsistentAddressTypeChange;

impl Heuristic for ConsistentAddressTypeChange {
    fn name(&self) -> &str {
        "ConsistentAddressTypeChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements{
        InputDataRequirements::Low
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false);

        let input_types: Vec<AddressType> = tx.inputs_types()?;

        let mut counts: HashMap<AddressType, usize> = HashMap::new();
        for input_type in &input_types {
            *counts.entry(*input_type).or_insert(0) += 1;
        }

        if counts.len() != 1 {
            return Err(AppError::Heuristic(HeuristicError::InconsistenInputsAddressesTypes(
                format!("more than one input type founded")
            )));
        }

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