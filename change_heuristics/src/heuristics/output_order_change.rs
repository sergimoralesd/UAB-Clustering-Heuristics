use bitcoin::Script;

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct OutputOrderChange;

impl Heuristic for OutputOrderChange {
    fn name(&self) -> String {
        return "OutputOrderChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::MediumLow
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, true, false);

        let actual_ouput_order: u8 = get_output_order(tx)?;

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok(actual_ouput_order == get_output_order(future_tx)?)
        })
        .collect::<Result<Vec<bool>, AppError>>()?;

        Ok(possible_change)
    }
}

fn get_output_order(tx: &Tx) -> Result<u8, AppError> {
    if tx.input_count() == 1 {
        return Ok(0);
    }

    let outputs_values_original = tx.outputs_values();
    let mut outputs_values_sorted = outputs_values_original.clone();
    outputs_values_sorted.sort();
    if outputs_values_original == outputs_values_sorted {
        return Ok(1);
    }

    outputs_values_sorted.reverse();
    if outputs_values_original == outputs_values_sorted {
        return Ok(2);
    }

    let paired: Vec<(u64, Script)> = tx.outputs_values()
    .iter()
    .zip(tx.outputs_scriptpubkeys().iter())
    .map(|(values, scriptpubkey)| (*values, scriptpubkey.clone()))
    .collect();

    let mut sorted_paired = paired.clone();

    sorted_paired.sort_by(|(value_a, scriptpubkey_a), (value_b, scriptpubkey_b)| {
    value_a.cmp(value_b)
        .then_with(|| scriptpubkey_a.cmp(scriptpubkey_b))
    });

    if paired == sorted_paired {
        return Ok(2);
    }
    Ok(3)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_output_order_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "9ba576707044407d0543c3060cafc4dd9320fb60e4e55940653863cc6f9baafa", 
            "46d8960eb6d0660f2b2cc68662e46345b086870ab9ac75092b064e0dbf0fbc8b", 
            "7aaa37a2775a1bc61841248ec559a210d18717cb2cd12899e40606b6c88e13c1"
        ];

        let expected_results = vec![
            vec![true, true],
            vec![true, false],
            vec![true, true]
        ];

        run_heuristic_test(&OutputOrderChange, txids, expected_results, false)

    }
}