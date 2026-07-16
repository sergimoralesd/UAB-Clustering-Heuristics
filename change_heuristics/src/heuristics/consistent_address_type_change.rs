use std::collections::HashMap;

use bitcoin::AddressType;

use crate::tx::Tx;
use crate::types::{AppError, HeuristicError, InputDataRequirements};

use super::Heuristic; 

pub struct ConsistentAddressTypeChange;

impl Heuristic for ConsistentAddressTypeChange {
    fn name(&self) -> String {
        return "ConsistentAddressTypeChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements{
        InputDataRequirements::Low
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false);

        let input_types: Vec<AddressType> = tx.inputs_types()?;

        let mut counts: HashMap<AddressType, usize> = HashMap::new();
        for input_type in &input_types {
            *counts.entry(*input_type).or_insert(0) += 1;
        }

        if counts.len() != 1 {
            return Err(AppError::Heuristic(HeuristicError::InconsistentInputsAddressesTypes(
                format!("more than one input type founded")
            )));
        }

        let possible_change: Vec<bool> = tx.outputs_types()?
        .iter()
        .map(|out_type| input_types.contains(out_type))
        .collect();

        Ok(possible_change)
    }
}