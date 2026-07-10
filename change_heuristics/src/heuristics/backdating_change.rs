use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct BackdatingChange;

impl Heuristic for BackdatingChange {
    fn name(&self) -> &str {
        "BackdatingChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::HighIndexed
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, true);

        let actual_is_backdating: bool = is_backdated(tx);
    
        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| actual_is_backdating && is_backdated(&future_tx))
        .collect();

        Ok(possible_change)
    }
}

pub fn is_backdated(tx: &Tx) -> bool {
    const LOCKTIME_THRESHOLD: u32 = 500000000;
    let actual_uses_blockheight: bool = tx.locktime() < LOCKTIME_THRESHOLD;

    if ! actual_uses_blockheight {
        return false;
    }

    for prev_tx in tx.previous_txs().unwrap() {
        let prev_uses_blockheight: bool = prev_tx.locktime() < LOCKTIME_THRESHOLD;

        if actual_uses_blockheight != prev_uses_blockheight {
            continue;
        }

        if tx.locktime() < prev_tx.locktime() {
            return true;
        }
    }

    let block_height: u32 = tx.block_height().unwrap() as u32;

    if tx.locktime() >= block_height - 100 && tx.locktime() < block_height {
        return true;
    }

    return false
}