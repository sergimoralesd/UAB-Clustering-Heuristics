use crate::tx::Tx;
use crate::types::{AppError, HeuristicError, InputDataRequirements};

pub trait Heuristic {

    //Heuristic's name
    fn name(&self) -> String;

    //Heurisitic's input data requirement level, following the documentation
    fn input_data_requirements(&self) -> InputDataRequirements;

    //Heuristic's main functionality
    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError>;

    fn check_requirements(&self, tx: &Tx, block_height_needed: bool, replacement_needed: bool) -> Result<(), AppError> {
        check_data_requirements(tx, &self.input_data_requirements(), block_height_needed, replacement_needed)
    }
}

fn check_previous_txs(tx: &Tx) -> Result<(), AppError> {
    if tx.previous_txs().is_none() {
        return Err(AppError::Heuristic(HeuristicError::PreviousTxNotImported(
            format!("import_previous_txs before running the heuristic"))
        ));
    }
    Ok(())
}
fn check_future_txs(tx: &Tx) -> Result<(), AppError> { 
    if tx.future_txs().is_none() {
        return Err(AppError::Heuristic(HeuristicError::FutureTxsNotImported(
            format!("import_future_txs before running the heuristic"))
        ));
    }
    Ok(())
}
fn check_block_height(tx: &Tx) -> Result<(), AppError> { 
    if tx.block_height().is_none() {
        return Err(AppError::Heuristic(HeuristicError::BlockHeightNotImported(
            format!("import_block_height before running the heuristic"))
        ));
    }
    Ok(())

}
fn check_future_txs_previous_txs(tx: &Tx) -> Result<(), AppError> { 
    for future_tx in tx.future_txs().unwrap() {
        if future_tx.previous_txs().is_none() {
            return Err(AppError::Heuristic(HeuristicError::PreviousTxNotImported(
            format!("import_previous_txs for each future transaction before running the heuristic"))
            ));
        }
    }
    Ok(())
}
fn check_replacement(tx: &Tx) -> Result<(), AppError> {
    if tx.replacement().is_none() {
        return Err(AppError::Heuristic(HeuristicError::ReplacementNotImported(
            format!("import_replacement_tx before running the heuristic"))
        ));
    }
    Ok(())
}

fn check_data_requirements(tx: &Tx, requirements: &InputDataRequirements, block_height_needed: bool, replacement_needed: bool) -> Result<(), AppError> {
        match requirements {
        InputDataRequirements::None => {},

        InputDataRequirements::Low => {
            check_previous_txs(tx)?;
        },

        InputDataRequirements::MediumLow => {
            check_future_txs(tx)?;
        },

        InputDataRequirements::Medium => {
            check_previous_txs(tx)?;
            check_future_txs(tx)?;
        },

        InputDataRequirements::MediumHigh => {
            check_previous_txs(tx)?;
            check_future_txs(tx)?;
            check_future_txs_previous_txs(tx)?;
        },

        InputDataRequirements::HighIndexed => {
            check_previous_txs(tx)?;
            check_future_txs(tx)?;
            check_future_txs_previous_txs(tx)?;
            
            if block_height_needed {
                check_block_height(tx)?;
                for prev_tx in tx.previous_txs().unwrap() {
                    check_block_height(&prev_tx)?;
                }
                for fut_tx in tx.future_txs().unwrap() {
                    check_block_height(&fut_tx)?;
                }
            }
        },

        InputDataRequirements::HighNonIndexed => {
            if block_height_needed {
                check_block_height(tx)?;
                for prev_tx in tx.previous_txs().unwrap() {
                    check_block_height(&prev_tx)?;
                }
                for fut_tx in tx.future_txs().unwrap() {
                    check_block_height(&fut_tx)?;
                }
            }
            if replacement_needed {
                check_replacement(tx)?;
            }
        }
    }

    Ok(())
}

pub mod api;
pub use api::{get_txs_by_address, get_historical_price};

pub use address_type_change::AddressTypeChange;
pub use backdating_change::BackdatingChange;
pub use consistent_address_type_change::ConsistentAddressTypeChange;
pub use fee_absolute_change::FeeAbsoluteChange;
pub use fee_relative_change::FeeRelativeChange;
pub use future_address_reuse_change::FutureReusedAddressChange;
pub use input_order_change::InputOrderChange;
pub use locktime_change::LocktimeChange;
pub use low_confirmation_value::LowConfirmationValue;
pub use low_r_change::LowRChange;
pub use malformed_coinjoin_change::MalformedCoinjoinChange;
pub use multisignature_change::MultisignatureChange;
pub use optimal_change::OptimalChange;
pub use output_order_change::OutputOrderChange;
pub use past_address_reuse_change::PastReusedAddressChange;
pub use present_reused_address_change::PresentReusedAddressChange;
pub use rbf_change::RBFChange;
pub use rounded_change::RoundedChange;
pub use rounded_fiat_change::RoundedFiatChange;
pub use segwit_conform_change::SegwitConformChange;
pub use signal_rbf_change::SignalRBFChange;
pub use smaller_output_change::SmallerOuputChange;
pub use uncompress_public_key_change::UncompressPublicKeyChange;
pub use version_change::VersionChange;



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
mod rbf_change;
mod rounded_change;
mod rounded_fiat_change;
mod segwit_conform_change;
mod signal_rbf_change;
mod smaller_output_change;
mod uncompress_public_key_change;
mod version_change;



#[cfg(test)]
pub(crate) mod test_utils;