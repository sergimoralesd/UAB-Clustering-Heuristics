use bitcoin::Network::Bitcoin;

use crate::AppError;
use crate::Heuristic;
use crate::types::TestError;
use crate::InputDataRequirements;
use crate::Tx;

fn extract_raw_tx<'a>(dict: &'a serde_json::Value, context: &str) -> Result<&'a str, AppError> {
    dict.get("raw")
        .and_then(|v| v.as_str())
        .ok_or(AppError::Test(TestError::MissingRawTx(
            format!("could not retrieve raw tx from {}", context)
        )))
}

fn extract_block_height(dict: &serde_json::Value, context: &str) -> Result<usize, AppError> {
    dict.get("block_height")
        .and_then(|v| v.as_u64())
        .map(|bh| bh as usize)
        .ok_or(AppError::Test(TestError::MissingBlockHeight(
            format!("could not retrieve block height from {}", context)
        )))
}

fn extract_replacement<'a>(dict: &'a serde_json::Value,context: &str) -> Result<&'a str, AppError> {
    dict.get("replacement")
        .and_then(|v| v.as_str())
        .ok_or(AppError::Test(TestError::MissingReplacementTxs(
            format!("could not retrieve replacement raw tx from {}", context)
        )))
}

fn extract_tx_array<'a>(dict: &'a serde_json::Value, key: &str, context: &str) -> Result<&'a Vec<serde_json::Value>, AppError> {
    dict.get(key)
        .and_then(|v| v.as_array())
        .ok_or(AppError::Test(TestError::MissingRawTx(
            format!("could not retrieve {} from {}", key, context)
        )))
}

fn build_tx_from_dict(dict: &serde_json::Value, block_height_needed: bool, replacement_needed: bool, context: &str) -> Result<Tx, AppError> {
    let raw = extract_raw_tx(dict, context)?;
    let mut tx = Tx::from_raw(raw, Bitcoin)?;  // ← build directly from raw

    if block_height_needed {
        let block_height = extract_block_height(dict, context)?;
        tx.import_block_height(block_height);
    }

    if replacement_needed {
        let replacement_raw = extract_replacement(dict, context)?;
        let _ = tx.import_replacement_tx(replacement_raw.to_string());
    }

    Ok(tx)
}

fn build_prev_txs(tx_dict: &serde_json::Value, block_height_needed: bool) -> Result<Vec<Tx>, AppError> {
    extract_tx_array(tx_dict, "previous_transactions", "tx")?
        .iter()
        .map(|prev_tx_dict| build_tx_from_dict(prev_tx_dict, block_height_needed, false, "prev_tx"))
        .collect()
}

fn build_fut_txs(tx_dict: &serde_json::Value, block_height_needed: bool, with_previous_txs: bool) -> Result<Vec<Tx>, AppError> {
    extract_tx_array(tx_dict, "future_transactions", "tx")?
        .iter()
        .map(|fut_tx_dict| {
            let mut fut_tx = build_tx_from_dict(fut_tx_dict, block_height_needed, false, "future_tx")?;

            if with_previous_txs {
                let fut_prev_txs = build_prev_txs(fut_tx_dict, block_height_needed)?;
                fut_tx.import_previous_txs(fut_prev_txs)
                    .map_err(AppError::Tx)?;
            }

            Ok(fut_tx)
        })
        .collect()
}

fn build_tx(tx_dict: &serde_json::Value, req: &InputDataRequirements, block_height_needed: bool, replacement_needed: bool) -> Result<Tx, AppError> {
    let mut tx = build_tx_from_dict(&tx_dict, block_height_needed, replacement_needed, "tx")?;

    match req {
        InputDataRequirements::None => {},

        InputDataRequirements::Low => {
            tx.import_previous_txs(build_prev_txs(&tx_dict, block_height_needed)?)
                .map_err(AppError::Tx)?;
        },

        InputDataRequirements::MediumLow => {
            tx.import_future_txs(build_fut_txs(&tx_dict, block_height_needed, false)?)
                .map_err(AppError::Tx)?;
        },

        InputDataRequirements::Medium => {
            tx.import_previous_txs(build_prev_txs(&tx_dict, block_height_needed)?)
                .map_err(AppError::Tx)?;
            tx.import_future_txs(build_fut_txs(&tx_dict, block_height_needed, false)?)
                .map_err(AppError::Tx)?;
        },

        InputDataRequirements::MediumHigh => {
            tx.import_previous_txs(build_prev_txs(&tx_dict, block_height_needed)?)
                .map_err(AppError::Tx)?;
            tx.import_future_txs(build_fut_txs(&tx_dict, block_height_needed, true)?)
                .map_err(AppError::Tx)?;
        },

        InputDataRequirements::HighIndexed => {
            tx.import_previous_txs(build_prev_txs(&tx_dict, block_height_needed)?)
                .map_err(AppError::Tx)?;
            tx.import_future_txs(build_fut_txs(&tx_dict, block_height_needed, true)?)
                .map_err(AppError::Tx)?;
        },

        InputDataRequirements::HighNonIndexed => {
            if !replacement_needed {
                tx.import_previous_txs(build_prev_txs(&tx_dict, block_height_needed)?)
                    .map_err(AppError::Tx)?;
                tx.import_future_txs(build_fut_txs(&tx_dict, block_height_needed, true)?)
                    .map_err(AppError::Tx)?;
            }
        }
    }

    Ok(tx)
}

pub fn run_heuristic_test<H: Heuristic>(heuristic: &H, txids: Vec<&str>, expected_results: Vec<Vec<bool>>, needs_block_height: bool, needs_replacement: bool) -> Result<(), AppError> {
    let tx_file = std::fs::File::open("tests/data/sampled_transactions.json")
        .expect("JSON file was not found");
    let dict_txs: serde_json::Value = serde_json::from_reader(tx_file)
        .expect("JSON was not well-formatted");

    for (txid, expected_result) in txids.iter().zip(expected_results.iter()) {
        let tx_dict = dict_txs
            .get(txid)
            .ok_or(AppError::Test(TestError::MissingTxid(
                format!("missing txid: {}", txid)
            )))?;

        let tx = build_tx(tx_dict, &heuristic.input_data_requirements(), needs_block_height, needs_replacement)?;

        match heuristic.apply(&tx) {
            Err(err) => println!("[{}] Error on {}: {}", heuristic.name(), txid, err),
            Ok(res) => assert_eq!(
                res, *expected_result,
                "[{}] failed for txid: {}",
                heuristic.name(), txid
            ),
        }
    }

    Ok(())
}