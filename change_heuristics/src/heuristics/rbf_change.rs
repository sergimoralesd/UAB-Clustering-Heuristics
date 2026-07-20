// Original algorithm by @Bicaru20.

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};
use std::collections::HashSet;

use super::Heuristic; 

pub struct RBFChange;

impl Heuristic for RBFChange {
    fn name(&self) -> String {
        return "RBFChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::HighNonIndexed
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, true);

        let tx_replacement = tx.replacement().unwrap();
        
        if tx.output_count() == tx.replacement().unwrap().output_count() {
            Ok(same_output(tx, tx_replacement))
        }
        else {
            Ok(different_output(tx, tx_replacement)?)
        }
    }
}

fn same_output(tx: &Tx, tx_replacement: &Tx) -> Vec<bool> {
    let actual_values: Vec<u64> = tx.outputs_values();
    let replacement_values: Vec<u64> = tx_replacement.outputs_values();

    let mut possible_change: Vec<bool> = vec![false; actual_values.len()];

    for (i, x) in actual_values.iter().enumerate() {
        let not_in_next = replacement_values
            .iter()
            .all(|y| x != y);

        if not_in_next {
            possible_change[i] = true;
        }
    }

    possible_change
}


fn different_output(tx: &Tx, tx_replacement: &Tx) -> Result<Vec<bool>, AppError> {
    let actual_values: Vec<u64> = tx.outputs_values();
    let replacement_values: Vec<u64> = tx.replacement().unwrap().outputs_values();
    let replacement_addr:Vec<bitcoin::Address>  = tx_replacement.outputs_addresses()?;

    let mut possible_change: Vec<bool> = vec![false; actual_values.len()];

    let mut past_values: HashSet<String> = HashSet::new();
    for value in actual_values.iter() {
        let key = value.to_string();
        if past_values.contains(&key) {
            past_values.insert(format!("{}_{}", value, key));
        } else {
            past_values.insert(key);
        }
    }

    let mut seen_in_replacement: HashSet<String> = HashSet::new();
     for (i, (value, address)) in replacement_values
        .iter()
        .zip(replacement_addr.iter())
        .enumerate()
    {
        let key = value.to_string();
        let key = if seen_in_replacement.contains(&key) {
            format!("{}_{}", value, address)
        } else {
            key
        };

        seen_in_replacement.insert(key.clone());

        
        if !past_values.contains(&key) {
            possible_change[i] = true;
        }
    }

    Ok(possible_change)

}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;
    

    #[test]
    fn test_rbf_heuristic() -> Result<(),AppError> {

        let txids = vec![
            "0671a6a6f9385a0886cfcada90e74d18cd153956295ac4a5c3c7b0847f7e6bf1"
        ];

        let expected_results = vec![
            vec![false, true],
        ];

        run_heuristic_test(&RBFChange, txids, expected_results, false, true)
    }
}