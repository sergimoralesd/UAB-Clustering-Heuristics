use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements, HeuristicError};

use super::Heuristic; 

pub struct OptimalChange;

impl Heuristic for OptimalChange {
    fn name(&self) -> String {
        return "OptimalChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::Low
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false)?;

        let outputs_values = tx.outputs_values();
        let inputs_values = tx.inputs_values()?;

        // assert tx.input_count > 1
        if tx.input_count() <= 1 {
            return Err(AppError::Heuristic(HeuristicError::NotApplicable(
                format!("tx {} must contain at least 2 inputs", tx.txid())
            )));
        }

        // Exactly 2 outputs that carry value: an OP_RETURN output pays no one,
        // so a payment, its change and a data output still qualify.
        let op_return = tx.outputs_are_op_return();
        let value_outputs: Vec<usize> = (0..outputs_values.len()).filter(|&i| !op_return[i]).collect();
        if value_outputs.len() != 2 {
            return Err(AppError::Heuristic(HeuristicError::NotApplicable(
                format!("tx {} must contain exactly 2 outputs that are not OP_RETURN", tx.txid())
            )));
        }

        let potential_change_value = value_outputs.iter().map(|&i| outputs_values[i]).min().unwrap();
        let mut possible_change: Vec<bool> = vec![false; outputs_values.len()];

        let matching_indices: Vec<usize> = value_outputs
        .iter()
        .copied()
        .filter(|&i| outputs_values[i] == potential_change_value)
        .collect();

        if matching_indices.len() > 1 {
            return Ok(vec![false; outputs_values.len()]);
        }

        for &input_value in inputs_values.iter() {
            if potential_change_value > input_value {
                return Ok(vec![false; outputs_values.len()]);
            }
        }

        possible_change[matching_indices[0]] = true;

        Ok(possible_change)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_optimal_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "9ba576707044407d0543c3060cafc4dd9320fb60e4e55940653863cc6f9baafa", 
            "285a12fe93eb0679446e9845e50f61b033601eedc777c566ff2dfd5c62aa2341", 
            "7aaa37a2775a1bc61841248ec559a210d18717cb2cd12899e40606b6c88e13c1"
        ];

        let expected_results = vec![
            vec![true, false],
            vec![false, true],
            vec![false, false]
        ];

        run_heuristic_test(&OptimalChange, txids, expected_results, false, false)

    }
}