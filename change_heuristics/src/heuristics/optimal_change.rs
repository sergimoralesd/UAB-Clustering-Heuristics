use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements, HeuristicError};

use super::Heuristic; 

pub struct OptimalChange;

impl Heuristic for OptimalChange {
    fn name(&self) -> &str {
        "OptimalChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::Low
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false);

        let outputs_values = tx.outputs_values();
        let inputs_values = tx.inputs_values()?;

        // assert tx.input_count > 1
        if tx.input_count() <= 1 {
            return Err(AppError::Heuristic(HeuristicError::NotApplicable(
                format!("tx {} must contain at least 2 inputs", tx.txid())
            )));
        }

        // assert tx.output_count == 2
        if tx.output_count() != 2 {
            return Err(AppError::Heuristic(HeuristicError::NotApplicable(
                format!("tx {} must contain exactly 2 outputs", tx.txid())
            )));
        }

        let potential_change_value = outputs_values.iter().min().unwrap();
        let mut possible_change: Vec<bool> = vec![false; outputs_values.len()];

        let matching_indices: Vec<usize> = outputs_values
        .iter()
        .enumerate()
        .filter(|(_, v)| **v == *potential_change_value)
        .map(|(i, _)| i)
        .collect();

        if matching_indices.len() > 1 {
            return Ok(vec![false; outputs_values.len()]);
        }

        for &input_value in inputs_values.iter() {
            if *potential_change_value > input_value {
                return Ok(vec![false; outputs_values.len()]);
            }
        }

        possible_change[matching_indices[0]] = true;

        Ok(possible_change)
    }
}