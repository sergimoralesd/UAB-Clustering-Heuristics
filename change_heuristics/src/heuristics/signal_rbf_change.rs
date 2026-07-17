use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct SignalRBFChange;

impl Heuristic for SignalRBFChange {
    fn name(&self) -> String {
        return "SignalRBFChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::MediumLow
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false);

        let actual_signals_rbf: bool = tx.signals_rbf();

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| -> Result<bool, AppError> {
            Ok(actual_signals_rbf == future_tx.signals_rbf())
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
    fn test_signal_rbf_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "fb27096fe0285d185c7c78bf79e990591d69a6d2d1548de07486af779f54f485", 
            "ecc785804ed0bd24f2f935110fe4641d995466eeb8f5c6e9ba9e1c50fc1edbc7", 
        ];

        let expected_results = vec![
            vec![true, true],
            vec![true, false],
        ];

        run_heuristic_test(&SignalRBFChange, txids, expected_results, false)

    }
}