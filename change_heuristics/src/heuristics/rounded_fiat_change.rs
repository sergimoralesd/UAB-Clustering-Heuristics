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
    fn name(&self) -> String {
        return format!("RoundedChange_{}_{}", self.precision_parameter, self.currency);
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


#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_present_addr_reuse_heuristic() -> Result<(),AppError> {
        let txids = vec!["c9cfd7e0cda60ab0d21d3b7402b141953f48b3bebc9ca7bd32f1caa78c31a3fb"];
        let expected_results = vec![vec![true, true]];
        let _ = run_heuristic_test(&RoundedFiatChange::new(4, "EUR".to_string()), txids, expected_results, true, false)?;

        let txids = vec!["134d82e432ba31b59e6940cace017f969a2d37feffcccce7c3367587b389af41"];
        let expected_results = vec![vec![true, false]];
        let _ = run_heuristic_test(&RoundedFiatChange::new(2, "EUR".to_string()), txids, expected_results, true, false)?;

        let txids = vec!["aa952a2f01a7c14470408fd1bccac2ecf92bc104a11fd779e34e0b1ff8156068", ];
        let expected_results = vec![vec![true, true]];
        let _ = run_heuristic_test(&RoundedFiatChange::new(2,"USD".to_string()), txids, expected_results, true, false)?;

        let txids = vec!["5cdbfc35d2c06fb551349ab5de1c33fc9bd84f3d553943f3cb482108dc1816c6", ];
        let expected_results = vec![vec![true, true]];
        let _ = run_heuristic_test(&RoundedFiatChange::new(1, "GBP".to_string()), txids, expected_results, true, false)?;

        Ok(())

    }
}