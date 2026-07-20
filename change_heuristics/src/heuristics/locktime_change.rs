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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_locktime_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "8b0da777f660dece668f826e159bc4c589531bb9751ca0f0943e1ad34cee26b2", 
            "9e9f5ff157d1e04ad9e3fd3699ee9956613ce66fd3b4625ff69b650b923206da", 
            "d2416edba67840e699b064f17125e6fb071cae153227a8e8ca0a6c1c7596095e"
        ];

        let expected_results = vec![
            vec![false, true],
            vec![true, true],
            vec![true, false]
        ];

        run_heuristic_test(&LocktimeChange, txids, expected_results, true, false)


        
    }
}