use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

pub trait Heuristic {

    //Heuristic's name
    fn name(&self) -> &str;

    //Heurisitic's input data requirement level, following the documentation
    fn input_data_requirements(&self) -> InputDataRequirements;

    //Heuristic's main functionality
    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError>;
}

pub use address_type_change::AddressTypeChange;

pub use consistent_address_type_change::ConsistentAddressTypeChange;


mod address_type_change;
mod backdating_change;
mod consistent_address_type_change;
mod fee_absolute_change;
mod fee_relative_change;
mod future_address_reuse_change;
mod input_order_change;
mod locktime_change;
mod low_confirmation_value;
mod low_r_change;
mod malformed_coinjoin_change;
mod multisignature_change;
mod optimal_change;
mod output_order_change;
mod past_address_reuse_change;
mod present_reused_address_change;
mod rounded_change;
mod rounded_fiat_change;
mod segwit_conform_change;
mod signal_rbf_change;
mod smaller_output_change;
mod uncompress_public_key_change;
mod version_change;