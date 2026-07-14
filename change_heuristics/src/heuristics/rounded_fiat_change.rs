use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 
use super::api::get_historical_price;

pub struct RoundedFiatChange {
    precision_parameter: u8,
    currency: String,
}

impl RoundedFiatChange {
    pub fn new(precision_parameter: u8, currency: String) -> Self {
        RoundedFiatChange { precision_parameter, currency }
    }
}

impl Heuristic for RoundedFiatChange {
    fn name(&self) -> &str {
        "RoundedFiatChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::HighNonIndexed
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, true, false);

        let precision: f32 = (10 ^ self.precision_parameter as u64) as f32;
        let price: f32 = get_historical_price(tx.block_height().unwrap(), self.currency.clone())?;
        
        let possible_change: Vec<bool> = tx.outputs_values()
        .iter()
        .map(|value| price*((value/10^8) as f32) % precision != 0.0)
        .collect();

        Ok(possible_change)
    }
}
