use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct VersionChange;

impl Heuristic for VersionChange {
    fn name(&self) -> String {
        return "VersionChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::MediumLow
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false,false);

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| tx.version() == future_tx.version())
        .collect();

        Ok(possible_change)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_version_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "83c0b88e22ca42c147ea9f92ce993bd7e760532b5587abcb9b67464904543a57", 
            "d2416edba67840e699b064f17125e6fb071cae153227a8e8ca0a6c1c7596095e", 
        ];

        let expected_results = vec![
            vec![true, true],
            vec![true, false],
        ];

        run_heuristic_test(&VersionChange, txids, expected_results, false)

    }
}