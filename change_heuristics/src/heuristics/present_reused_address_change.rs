use bitcoin::Address;

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct PresentReusedAddressChange;

impl Heuristic for PresentReusedAddressChange {
    fn name(&self) -> String {
        return "PresentReusedAddressChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::Low
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false)?;

        let input_addresses: Vec<Address> = tx.inputs_addresses()?;

        let possible_change: Vec<bool> = tx.outputs_addresses()?
        .iter()
        .map(|addr| input_addresses.contains(addr))
        .collect();

        Ok(possible_change)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;

    #[test]
    fn test_present_reused_address_heuristic() -> Result<(),AppError> {
        let txids = vec![
            "e36f06a8dfe44c3d64be2d3fe56c77f91f6a39da4a5ffc086ecb5db9664e8583", 
            "450034dbc12a1d584d1d689add794da0254d5a531a8e15ffc78ebaf6f744c092"
        ];

        let expected_results = vec![
            vec![false, true],
            vec![false, false],

        ];

        run_heuristic_test(&PresentReusedAddressChange, txids, expected_results, false, false)

    }
}