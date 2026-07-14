use bitcoin::Script;

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct OutputOrderChange;

impl Heuristic for OutputOrderChange {
    fn name(&self) -> &str {
        "OutputOrderChange"
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