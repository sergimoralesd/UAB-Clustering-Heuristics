use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 
use super::api::get_txs_by_address;

pub struct FutureReusedAddressChange;

impl Heuristic for FutureReusedAddressChange {
    fn name(&self) -> String {
        return "FutureReusedAddressChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::HighNonIndexed
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, true, false)?;

        let outputs_addresses = tx.outputs_addresses()?;
        let actual_block_height = tx.block_height().unwrap();

        let mut possible_change: Vec<bool> = vec![false; outputs_addresses.len()];

        let mut total_blocks_heights: Vec<Vec<usize>> = Vec::new();

        for out_addr in outputs_addresses.iter() {
            let all_txs = get_txs_by_address(out_addr.to_string())?;

            let mut blocks_heights: Vec<usize> = all_txs
                .iter()
                .filter(|tx_from_addr| tx_from_addr.txid() != tx.txid())
                .filter_map(|tx_from_addr| tx_from_addr.block_height())
                .collect();

            blocks_heights.sort();
            total_blocks_heights.push(blocks_heights);
        }

        let mut addresses_with_future: Vec<String> = Vec::new();

        for (out_addr, blocks_heights) in outputs_addresses.iter().zip(total_blocks_heights.iter()) {
            if !blocks_heights.is_empty() {
                for &block_height in blocks_heights.iter() {
                    if actual_block_height < block_height {
                        addresses_with_future.push(out_addr.to_string());
                        break;
                    }
                }
            }
        }
        
        for (index, out_addr) in outputs_addresses.iter().enumerate() {
            if !addresses_with_future.contains(&&out_addr.to_string()) {
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
    fn test_future_address_reuse_heuristic() -> Result<(),AppError> {

        let txids = vec![
            "ddf89407656fd4ac32e375420f96186c6b54661746d815e96648812dc3f44669", "d2416edba67840e699b064f17125e6fb071cae153227a8e8ca0a6c1c7596095e"
        ];

        let expected_results = vec![
            vec![false, false],
            vec![false, false]
        ];

        run_heuristic_test(&FutureReusedAddressChange, txids, expected_results, true, false)
    }
}