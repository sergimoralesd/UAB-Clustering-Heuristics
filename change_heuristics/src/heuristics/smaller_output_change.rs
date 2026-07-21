use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct SmallerOutputChange;

impl Heuristic for SmallerOutputChange {
    fn name(&self) -> String {
        return "SmallerOutputChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::None
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false);

        let output_values = tx.outputs_values();
        let min_value: &u64 = output_values.iter().min().unwrap();
        let possible_change: Vec<bool> = tx.outputs_values()
        .iter()
        .map(|value| value == min_value)
        .collect();

        Ok(possible_change)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_smaller_output_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "46d8960eb6d0660f2b2cc68662e46345b086870ab9ac75092b064e0dbf0fbc8b", 
            "d83be2140893f7ba6663f621e4ee1719a2051e61525432012c4f43700d1d29fe", 
        ];

        let expected_results = vec![
            vec![true, false],
            vec![false, true],
        ];

        run_heuristic_test(&SmallerOutputChange, txids, expected_results, false, false)

    }
}