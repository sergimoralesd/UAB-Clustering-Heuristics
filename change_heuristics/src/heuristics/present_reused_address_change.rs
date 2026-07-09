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

        let possible_change: Vec<bool> = tx.outputs_addresses()?
        .iter()
        .map(|addr| input_addresses.contains(addr))
        .collect();

        Ok(possible_change)
    }
}