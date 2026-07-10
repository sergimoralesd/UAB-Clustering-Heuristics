use bitcoin::Address;

use crate::tx::Tx;
use crate::types::{TxError, ApiError, AppError, InputDataRequirements, JsonTx};

use super::Heuristic; 

pub struct PastReusedAddressChange;

impl Heuristic for PastReusedAddressChange {
    fn name(&self) -> &str {
        "PastReusedAddressChange"
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::HighIndexed
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, true);

        let outputs_addresses = tx.outputs_addresses()?;
        let actual_block_height = tx.block_height().unwrap();   

        let mut possible_change: Vec<bool> = vec![false; outputs_addresses.len()];
        for (index, out_addr) in outputs_addresses.iter().enumerate() {
            let all_txs_from_address: Vec<Tx> = get_txs_by_address(out_addr)?;

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

pub fn get_txs_by_address(addr: &Address) -> Result<Vec<Tx>, AppError> {
    let url = format!(
        "https://mempool.space/api/address/{}/txs/chain",
        addr.to_string()
    );

    let response = reqwest::blocking::get(&url)
        .map_err(|e| ApiError::UnableToFetch(e.to_string()))?;

    let raw: serde_json::Value = response.json()
        .map_err(|e| TxError::Decode(e.to_string()))?;

    let result = raw.as_array()
        .ok_or(TxError::Decode("expected array".to_string()))?
        .iter()
        .map(|item| {
            // deserialize into JsonTx
            let json_tx: JsonTx = serde_json::from_value(item.clone())
                .map_err(|e| TxError::Decode(e.to_string()))?;

            // extract block height from raw JSON separately
            let block_height = item["status"]["block_height"]
                .as_u64()
                .map(|bh| bh as usize);

            Ok((json_tx, block_height))
        })
        .collect::<Result<Vec<(JsonTx, Option<usize>)>, TxError>>()?;

    let txs: Vec<Tx> = result
    .iter()
    .map(|(json_tx, block_height)| {
            let mut tx = Tx::from_json(json_tx, bitcoin::Network::Bitcoin)
            .map_err(|e| AppError::Tx(e))?;

            if let Some(bh) = block_height {
                tx.import_block_height(*bh);  
            }
        Ok(tx)
    })
    .collect::<Result<Vec<Tx>, AppError>>()?;

    Ok(txs)
    
}