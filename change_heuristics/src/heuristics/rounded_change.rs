use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct RoundedChange {
    precision_parameter: u8,
}

impl RoundedChange {
    pub fn new(precision_parameter: u8) -> Self {
        RoundedChange { precision_parameter }
    }
}

impl Heuristic for RoundedChange {
    fn name(&self) -> String {
        return format!("RoundedChange_{}", self.precision_parameter);
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::None
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false);

        let precision: u64 = 10 ^ self.precision_parameter as u64;
        let possible_change: Vec<bool> = tx.outputs_values()
        .iter()
        .map(|value| value % precision != 0)
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
        let _ = run_heuristic_test(&RoundedChange::new(4), txids, expected_results, false, false)?;

        let txids = vec!["134d82e432ba31b59e6940cace017f969a2d37feffcccce7c3367587b389af41"];
        let expected_results = vec![vec![true, false]];
        let _ = run_heuristic_test(&RoundedChange::new(2), txids, expected_results, false, false)?;

        let txids = vec!["aa952a2f01a7c14470408fd1bccac2ecf92bc104a11fd779e34e0b1ff8156068", ];
        let expected_results = vec![vec![false, true]];
        let _ = run_heuristic_test(&RoundedChange::new(2), txids, expected_results, false, false)?;

        let txids = vec!["5cdbfc35d2c06fb551349ab5de1c33fc9bd84f3d553943f3cb482108dc1816c6", ];
        let expected_results = vec![vec![true, true]];
        let _ = run_heuristic_test(&RoundedChange::new(1), txids, expected_results, false, false)?;

        Ok(())

    }
}