use bitcoin::Address;

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct PresentReusedAddressChange;

impl Heuristic for PresentReusedAddressChange {
    fn name(&self) -> &str {
        "PresentReusedAddressChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::Low
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false);

        let input_addresses: Vec<Address> = tx.inputs_addresses()?;
        let output_addresses: Vec<Address> = tx.outputs_addresses()?;

        let mut possible_change: Vec<bool> = Vec::new();
        for output_addr in output_addresses {
            if input_addresses.contains(&output_addr) {
                possible_change.push(true);
            }
            else {
                possible_change.push(false);
            }
        }

        Ok(possible_change)
    }
}