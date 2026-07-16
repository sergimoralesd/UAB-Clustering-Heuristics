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

        // initialize all outputs as false
        let mut possible_change: Vec<bool> = vec![false; outputs_addresses.len()];

        let mut total_blocks_heights: Vec<Vec<usize>> = Vec::new();

        for out_addr in outputs_addresses.iter() {
            let all_txs = get_txs_by_address(out_addr.to_string())?;

            // get block heights excluding current tx
            let mut blocks_heights: Vec<usize> = all_txs
                .iter()
                .filter(|tx_from_addr| tx_from_addr.txid() != tx.txid())
                .filter_map(|tx_from_addr| tx_from_addr.block_height())
                .collect();

            blocks_heights.sort();
            total_blocks_heights.push(blocks_heights);
        }

        // find addresses with future txs
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

        // change = [addr for addr in tx.outputs_addresses if addr not in address_with_future]
        // mark as possible change if address does NOT have future txs
        for (index, out_addr) in outputs_addresses.iter().enumerate() {
            if !addresses_with_future.contains(&&out_addr.to_string()) {
                possible_change[index] = true;
            }
        }

        // only return true if exactly one change found
        let change_count = possible_change.iter().filter(|&&b| b).count();
        if change_count != 1 {
            return Ok(vec![false; outputs_addresses.len()]);
        }

        Ok(possible_change)
    }
}