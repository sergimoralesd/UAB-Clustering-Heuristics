use std::collections::HashMap;

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct MalformedCoinjoinChange;

impl Heuristic for MalformedCoinjoinChange {
    fn name(&self) -> String {
        return "MalformedCoinjoinChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::Low
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false)?;

        let outputs_values = tx.outputs_values();
        let inputs_values = tx.inputs_values()?;
        let tx_fee = tx.absolute_fee()?;

        let mut amount_equal_outputs: HashMap<u64, usize> = HashMap::new();
        for &value in &outputs_values {
            *amount_equal_outputs.entry(value).or_insert(0) += 1;
        }

        let max_freq = amount_equal_outputs.values().max().unwrap();

        let possible_payment_amounts: Vec<u64> = amount_equal_outputs
        .iter()
        .filter(|(_, c)| **c == *max_freq)
        .map(|(&v, _)| v)
        .collect();

        if possible_payment_amounts.len() > 1 {
            return Ok(vec![false; outputs_values.len()]);
        }

        let payment_amount = possible_payment_amounts[0];

            let mut possible_change: Vec<bool> = vec![false; outputs_values.len()];

        for in_value in inputs_values.iter() {
        let change_amount = match in_value.checked_sub(payment_amount) {
            Some(v) => v,
            None => continue,
        };

        let mut matching_indices: Vec<usize> = Vec::new();
        for (i, &out_amount) in outputs_values.iter().enumerate() {
            let lower_bound = change_amount.saturating_sub(tx_fee);
            if lower_bound <= out_amount && out_amount <= change_amount {
                matching_indices.push(i);
            }
        }

        if matching_indices.len() == 1 {
            possible_change[matching_indices[0]] = true;
        }
    }
    Ok(possible_change)
    
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;
    

    #[test]
    fn test_malformed_coinjoin_heuristic() -> Result<(),AppError> {

        let txids = vec![
            "c38aac9910f327700e0f199972eed8ea7c6b1920e965f9cb48a92973e7325046",
        ];

        let expected_results = vec![
            vec![false, true, false, true],
        ];

        run_heuristic_test(&MalformedCoinjoinChange, txids, expected_results, false, false)
    }
}