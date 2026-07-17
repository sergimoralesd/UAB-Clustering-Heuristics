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
        let _ = self.check_requirements(tx, false, false)?;

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


#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_consistent_address_type_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "2a1f0786f97551c501f75219db691f4c62e564a3ee3c0a250cd3ca054d3cd8ff", 
            "ddf89407656fd4ac32e375420f96186c6b54661746d815e96648812dc3f44669", "d2416edba67840e699b064f17125e6fb071cae153227a8e8ca0a6c1c7596095e"
        ];

        let expected_results = vec![
            vec![false, true],
            vec![true, false],
            vec![true, true]
        ];

        run_heuristic_test(&ConsistentAddressTypeChange, txids, expected_results, false)

    }
}