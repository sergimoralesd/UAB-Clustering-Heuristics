use std::{collections::HashMap, fs, vec};
use bitcoin::Network::Bitcoin;
use serde_json;
use change_heuristics::{Heuristic, Tx, heuristics::{AddressTypeChange, BackdatingChange, ConsistentAddressTypeChange, FeeAbsoluteChange, FeeRelativeChange, FutureReusedAddressChange, InputOrderChange, LocktimeChange, LowConfirmationValue, LowRChange, MalformedCoinjoinChange, MultisignatureChange, OptimalChange, PastReusedAddressChange, PresentReusedAddressChange, RoundedChange, RoundedFiatChange, SegwitConformChange, SignalRBFChange, SmallerOuputChange, UncompressPublicKeyChange, VersionChange}};

fn deserialize_tx_dict(tx_dict: &serde_json::Value) -> Result<Tx, String> {
    let raw: &str = match tx_dict.get("raw").and_then(|v| v.as_str()) {
        None => return Err(format!("missing raw tx")),
        Some(raw) => raw
    };

    let block_height: usize = match tx_dict.get("block_height").and_then(|v| v.as_u64()) {
        None => return Err(format!("missing block_height")),
        Some(block_height) => block_height as usize
    };

    let mut tx: Tx = match Tx::from_raw(raw, Bitcoin) {
        Err(err) => return Err(err.to_string()),
        Ok(tx) => tx
    };

    tx.import_block_height(block_height);
    Ok(tx)

}

fn build_tx(tx_dict: &serde_json::Value) -> Result<Tx, String>{

    let mut target_tx: Tx = deserialize_tx_dict(tx_dict)?;
    let mut prev_txs: Vec<Tx> = Vec::new();
    let mut fut_txs: Vec<Tx> = Vec::new();


    let previous_txs_dict = match tx_dict.get("previous_transactions")
    .and_then(|v| v.as_array()) {
        None => return Err(format!("missing previous_txs")),
        Some(prev_txs) => prev_txs
    };

    for prev_tx in previous_txs_dict {
        prev_txs.push(deserialize_tx_dict(prev_tx)?);
    }

    let future_txs = match tx_dict.get("future_transactions")
    .and_then(|v| v.as_array()) {
        None => return Err(format!("missing future_transactions")),
        Some(fut_txs) => fut_txs
    };  

    for fut_tx_dict in future_txs {
        let mut fut_tx: Tx = deserialize_tx_dict(fut_tx_dict)?;
        let future_previous_txs = match fut_tx_dict.get("previous_transactions")
        .and_then(|v| v.as_array()) {
            None => return Err(format!("missing future_previous_txs")),
            Some(fut_prev_txs) => fut_prev_txs
        };
        let mut fut_prev_txs: Vec<Tx> = Vec::new();
        for fut_prev_tx in future_previous_txs {
            fut_prev_txs.push(deserialize_tx_dict(fut_prev_tx)?);
        }

        let _ = fut_tx.import_previous_txs(fut_prev_txs)
        .map_err(|err| format!("import_previous_txs from fut_tx failed : {err}"))?;
        
        fut_txs.push(fut_tx);
    }

    let _ = target_tx.import_previous_txs(prev_txs)
    .map_err(|err| format!("import_previous_txs from target_tx failed : {err}"))?;
    let _ = target_tx.import_future_txs(fut_txs)
    .map_err(|err| format!("import_future_txs from target_tx failed : {err}"))?;

    Ok(target_tx)

}   

#[test]
fn test_heuristics() -> Result<(), String> {
    let tx_file = fs::File::open("tests/data/sampled_transactions.json")
        .expect("JSON file was not formatted correctly");
    let tx_dict: serde_json::Value = serde_json::from_reader(tx_file)
        .expect("JSON was not well-formatted");

    let mut txs_dict: HashMap<String, Tx> = HashMap::new();
    if let Some(obj) = tx_dict.as_object() {
    for (key, value) in obj {
        match build_tx(value) {
            Err(err) => return Err(format!("{}:{}", key, err)),    
            Ok(tx) => txs_dict.insert(key.clone(), tx)
            }; 
        };
    }

    let currencies = vec!["USD","EUR", "GBP", "CAD", "CHF", "AUD", "JPY"];

    let mut heuristics: Vec<Box<dyn Heuristic>> = vec![
        Box::new(AddressTypeChange),
        Box::new(BackdatingChange),
        Box::new(ConsistentAddressTypeChange),
        Box::new(FeeAbsoluteChange),
        Box::new(FeeRelativeChange),
        Box::new(FutureReusedAddressChange),
        Box::new(InputOrderChange),
        Box::new(LocktimeChange),
        Box::new(LowConfirmationValue),
        Box::new(LowRChange),
        Box::new(MalformedCoinjoinChange),
        Box::new(MultisignatureChange),
        Box::new(OptimalChange),
        Box::new(PastReusedAddressChange),
        Box::new(PresentReusedAddressChange),
        Box::new(SegwitConformChange),
        Box::new(SignalRBFChange),
        Box::new(SmallerOuputChange),
        Box::new(UncompressPublicKeyChange),
        Box::new(VersionChange),
    ];

    for i in 0..11 {
        heuristics.push(Box::new(RoundedChange::new(i)));
    }
    for i in 0..6 {
        for currency in &currencies {
            heuristics.push(Box::new(RoundedFiatChange::new(i, currency.to_string())));
        }
    }


    let mut results: HashMap<String, HashMap<String, Vec<bool>>> = HashMap::new();
    for heuristic in heuristics {
        let mut heuristic_res: HashMap<String, Vec<bool>> = HashMap::new();
        for (key, value) in &txs_dict {
            match heuristic.apply(&value) {
                Err(err) => {println!("error founded in {}: {}", heuristic.name(), err);},
                Ok(res) => {heuristic_res.insert(key.clone(), res);},
            };
        }
        results.insert(heuristic.name(), heuristic_res);
    }
    
    Ok(())
}


