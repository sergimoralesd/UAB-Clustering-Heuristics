use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct LocktimeChange;

impl Heuristic for LocktimeChange {
    fn name(&self) -> String {
        return "LocktimeChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::HighIndexed
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, true, false);

        let actual_anti_fee_snipping_conf: u8 = get_anti_fee_snipping(tx)?;

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok(actual_anti_fee_snipping_conf == get_anti_fee_snipping(future_tx)?)
        })
        .collect::<Result<Vec<bool>, AppError>>()?;

        Ok(possible_change)
    }
}

fn get_anti_fee_snipping(tx: &Tx) -> Result<u8, AppError> {
    if tx.locktime() == 0 {
        return Ok(0);
    }


    if (tx.block_height().unwrap() as u32) - tx.locktime() >= 100 {
        return Ok(1);
    }
    
    Ok(2)
}