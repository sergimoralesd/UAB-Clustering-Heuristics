use bitcoin::AddressType;

use crate::tx::Tx;
use crate::types::{AppError, InputDataRequirements};

use super::Heuristic; 

pub struct AddressTypeChange;

impl Heuristic for AddressTypeChange {
    fn name(&self) -> String {
        return "AddressTypeChange".to_string();
    }

    fn input_data_requirements(&self) -> InputDataRequirements {
        InputDataRequirements::Low
    }

    fn apply(&self, tx: &Tx) -> Result<Vec<bool>, AppError> {
        let _ = self.check_requirements(tx, false, false)?;

        let input_types: Vec<AddressType> = tx.inputs_types()?;

        let possible_change: Vec<bool> = tx.outputs_types()?
        .iter()
        .map(|out_type| input_types.contains(out_type))
        .collect();

        Ok(possible_change)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::heuristics::test_utils::build_tx;
    use crate::types::TestError;
    

    #[test]
    fn test_address_type_heuristic() -> Result<(),AppError> {
        let tx_file = std::fs::File::open("tests/data/sampled_transactions.json")
            .expect("JSON file was not formatted correctly");
        let dict_txs: serde_json::Value = serde_json::from_reader(tx_file)
            .expect("JSON was not well-formatted");

        let txids = vec![
            "fe2ead7ab8d6d720f06eb33481e1cecf58066eabd10e2cc9219dd3cd50250664", 
            "ddf89407656fd4ac32e375420f96186c6b54661746d815e96648812dc3f44669", "d2416edba67840e699b064f17125e6fb071cae153227a8e8ca0a6c1c7596095e"
        ];

        let expected_results = vec![
            vec![true, true],
            vec![true, false],
            vec![true, true]
        ];


        for (txid, expected_result) in txids.iter().zip(expected_results) {
            let tx_dict = match dict_txs.get(txid) {
                None => return Err(AppError::Test(TestError::MissingTxid(format!("missing tx")))),
                Some(tx) => tx
            };

            let tx = build_tx(tx_dict, &AddressTypeChange.input_data_requirements(), false)?;

            let res = AddressTypeChange.apply(&tx)?;
            assert_eq!(res, expected_result);
        }

        Ok(())

    }
}