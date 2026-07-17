use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct LowConfirmationValue;

impl Heuristic for LowConfirmationValue {
    fn name(&self) -> String {
        return "LowConfirmationValue".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::HighIndexed
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, true, false);

        let actual_block_height: usize = tx.block_height().unwrap();

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok((future_tx.block_height().unwrap() - actual_block_height) < 6)
        })
        .collect::<Result<Vec<bool>, AppError>>()?;

        Ok(possible_change)
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_low_confirmation_value_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "c7161c1c29dd70dcdf292d643dcaa313d8cea3d05191f51e5e885acc7adbee93", 
            "faf172f5dc06b0ae03268555dddcd65be47e9a8a8bb44a122b12bfaf735f9a81", 
            "f2caac7783863d2d988c793bbda02de53101c99243d3f1a653bd0f7ae82a83ce"
        ];

        let expected_results = vec![
            vec![true, false],
            vec![false, true],
            vec![false, false]
        ];

        run_heuristic_test(&LowConfirmationValue, txids, expected_results, true)


        
    }
}