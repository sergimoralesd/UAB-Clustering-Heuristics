use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct BackdatingChange;

impl Heuristic for BackdatingChange {
    fn name(&self) -> String {
        return "BackdatingChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::HighIndexed
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, true, false)?;

        let actual_is_backdating: bool = is_backdated(tx);

        let possible_change: Vec<bool> = tx.future_txs().unwrap()
        .iter()
        .map(|future_tx| actual_is_backdating == is_backdated(&future_tx))
        .collect();

        Ok(possible_change)
    }
}

pub fn is_backdated(tx: &Tx) -> bool {
    const LOCKTIME_THRESHOLD: u32 = 500000000;
    let actual_uses_blockheight: bool = tx.locktime() < LOCKTIME_THRESHOLD && tx.locktime() != 0;

    if ! actual_uses_blockheight {
        return false;
    }

    for prev_tx in tx.previous_txs().unwrap() {
        let prev_uses_blockheight: bool = prev_tx.locktime() < LOCKTIME_THRESHOLD;

        if actual_uses_blockheight != prev_uses_blockheight {
            continue;
        }

        if tx.locktime() < prev_tx.locktime() {
            return true;
        }
    }

    let block_height: u32 = tx.block_height().unwrap() as u32;

    if tx.locktime() >= block_height - 100 && tx.locktime() < block_height {
        return true;
    }

    return false
}



#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::build_tx;
    use crate::types::TestError;
    

    #[test]
    fn test_backdating_heuristic() -> Result<(),AppError> {
        let tx_file = std::fs::File::open("tests/data/sampled_transactions.json")
            .expect("JSON file was not formatted correctly");
        let dict_txs: serde_json::Value = serde_json::from_reader(tx_file)
            .expect("JSON was not well-formatted");

        let txids = vec![
            "d2416edba67840e699b064f17125e6fb071cae153227a8e8ca0a6c1c7596095e", 
            "b0b82fbdbfa3c91410de17256c21c96100303bf96ddad2f5108b2b5805721fde", "a023fd2441e2fc973ba5670283492f8f4df1c7b8cc5825464caacc568b2ac97e"
        ];

        let expected_results = vec![
            vec![true, false],
            vec![true, true],
            vec![false, true]
        ];


        for (txid, expected_result) in txids.iter().zip(expected_results) {
            let tx_dict = match dict_txs.get(txid) {
                None => return Err(AppError::Test(TestError::MissingTxid(format!("missing tx")))),
                Some(tx) => tx
            };

            let tx = build_tx(tx_dict, &BackdatingChange.input_data_requirements(), true)?;

            match BackdatingChange.apply(&tx) {
                Err(err) => println!("Error: {}", err.to_string()),
                Ok(res) => assert_eq!(res, expected_result)
            };
        }

        Ok(())

    }
}