use crate::tx::Tx;
use crate::types::{JsonTx, TxError, AppError, ApiError};

pub fn get_txs_by_address(addr: String) -> Result<Vec<Tx>, AppError> {
    let url = format!(
        "https://mempool.space/api/address/{}/txs/chain",
        addr
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

pub fn get_historical_price(block_height: usize, currency: String) -> Result<f32, AppError> {
    let block_hash_url = format!("https://mempool.space/api/block-height/{block_height}");
    let block_hash = reqwest::blocking::get(&block_hash_url)
        .map_err(|e| ApiError::UnableToFetch(e.to_string()))?
        .text()
        .map_err(|e| AppError::Api(ApiError::UnableToFetch(e.to_string())))?
        .trim()
        .to_owned();

    let block_url = format!("https://mempool.space/api/block/{block_hash}");
    let block_json: serde_json::Value = reqwest::blocking::get(&block_url)
        .map_err(|e| AppError::Api(ApiError::UnableToFetch(e.to_string())))?
        .json()
        .map_err(|e| AppError::Tx(TxError::Decode(e.to_string())))?;

    let timestamp = block_json["timestamp"]
        .as_u64()
        .ok_or_else(|| AppError::Tx(TxError::Decode("missing block timestamp".to_string())))?;

    
    let price_url = format!("https://mempool.space/api/v1/historical-price?currency={currency}&timestamp={timestamp}");

    let price_json: serde_json::Value = reqwest::blocking::get(&price_url)
        .map_err(|e| AppError::Api(ApiError::UnableToFetch(e.to_string())))?
        .json()
        .map_err(|e| AppError::Tx(TxError::Decode(e.to_string())))?;

    let price = price_json["prices"]
        .as_array()
        .and_then(|prices| prices.first())
        .and_then(|first| first.get(currency.as_str()))
        .and_then(|value| value.as_f64())
        .ok_or_else(|| AppError::Api(ApiError::UnableToFetch("missing historical price".to_string())))?;

    Ok(price as f32)
}
