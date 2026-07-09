use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct SignalRBFChange;

impl Heuristic for SignalRBFChange {
    fn name(&self) -> &str {
        "SignalRBFChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::MediumLow
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false);

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