use bitcoin::Txid;

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct InputOrderChange;

impl Heuristic for InputOrderChange {
    fn name(&self) -> &str {
        "InputOrderChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::HighIndexed
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        self.check_requirements(tx, true);

        let actual_input_order: u8 = get_input_order(tx)?;

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok(actual_input_order == get_input_order(future_tx)?)
        })
        .collect::<Result<Vec<bool>, AppError>>()?;

        Ok(possible_change)
    }
}

fn get_input_order(tx: &Tx) -> Result<u8, AppError> {
    if tx.input_count() == 1 {
        return Ok(0);
    }

    let inputs_values_original = tx.inputs_values()?;
    let mut inputs_values_sorted = inputs_values_original.clone();
    inputs_values_sorted.sort();
    if inputs_values_original == inputs_values_sorted {
        return Ok(1);
    }

    inputs_values_sorted.reverse();
    if inputs_values_original == inputs_values_sorted {
        return Ok(2);
    }

    let prevouts: Vec<(Txid, usize)> = tx.previous_txids()
    .iter()
    .zip(tx.prevouts().iter())
    .map(|(prev_txid, vout)| (*prev_txid, *vout))
    .collect();

    let mut sorted_prevouts = prevouts.clone();

    sorted_prevouts.sort_by(|(txid_a, vout_a), (txid_b, vout_b)| {
    txid_a.as_ref().cmp(txid_b.as_ref())
        .then_with(|| vout_a.cmp(vout_b))
    });

    if prevouts == sorted_prevouts {
        return Ok(3);
    }

    let prev_block_height_original: Vec<Option<Option<usize>>>= tx.previous_txs().unwrap()
    .iter()
    .map(|prev_tx| Some(prev_tx.block_height()))
    .collect();

    let mut prev_block_height_sorted = prev_block_height_original.clone();
    prev_block_height_sorted.sort();
    if prev_block_height_original == prev_block_height_sorted {
        return Ok(4);
    }
    Ok(5)
}