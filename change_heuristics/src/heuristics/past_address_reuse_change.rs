use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic;
use super::api::get_txs_by_address; 

pub struct PastReusedAddressChange;

impl Heuristic for PastReusedAddressChange {
    fn name(&self) -> String {
        return "PastReusedAddressChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::HighIndexed
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, true, false);

        let outputs_addresses = tx.outputs_addresses()?;
        let actual_block_height = tx.block_height().unwrap();   

        let mut possible_change: Vec<bool> = vec![false; outputs_addresses.len()];
        for (index, out_addr) in outputs_addresses.iter().enumerate() {
            let all_txs_from_address: Vec<Tx> = get_txs_by_address(out_addr.to_string())?;

            let mut blocks_heights: Vec<usize> = all_txs_from_address
                .iter()
                .filter(|tx_from_addr| tx_from_addr.txid() != tx.txid())
                .filter_map(|tx_from_addr| tx_from_addr.block_height())
                .collect();

            blocks_heights.sort();

            // if no previous txs found for this address: it is new so possible change
            if blocks_heights.is_empty() {
                possible_change[index] = true;
                continue;
            }

            // if actual block height < first block height: address is new so possible change
            // same block height means it is not new
            if actual_block_height < blocks_heights[0] {
                possible_change[index] = true;
            }
        }
        Ok(possible_change)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::run_heuristic_test;
    

    #[test]
    fn test_past_address_reuse_heuristic() -> Result<(),AppError> {

        let txids = vec![
            "ddf89407656fd4ac32e375420f96186c6b54661746d815e96648812dc3f44669", "d2416edba67840e699b064f17125e6fb071cae153227a8e8ca0a6c1c7596095e"
        ];

        let expected_results = vec![
            vec![true, false],
            vec![true, false]
        ];

        run_heuristic_test(&PastReusedAddressChange, txids, expected_results, true, false)
    }
}