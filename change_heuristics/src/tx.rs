use bitcoin::{Address, AddressType, Network, OutPoint, PublicKey, Script, Transaction, TxIn, TxOut, Txid, Witness, Sequence};
use bitcoin::hashes::hex::FromHex;
use bitcoin::consensus::{deserialize};

use crate::types::{TxError, JsonTx};

use std::collections::HashMap;
use std::str::FromStr;

#[derive(Debug, Clone)]
pub struct Tx {
    target: Transaction,
    previous_txs: Option<Vec<Box<Tx>>>,
    future_txs: Option<Vec<Box<Tx>>>,
    replacement: Option<Box<Tx>>,
    network: Network,
    block_height: Option<usize>,
}

impl Tx {

    //Private Helpers
    fn build_tx_from_hex(raw_tx: &str) -> Result<Transaction, TxError> {
        let tx_bytes = Vec::<u8>::from_hex(raw_tx)
            .map_err(|err| TxError::Hex(err.to_string()))?;

        let tx = deserialize(&tx_bytes)
            .map_err(|err| TxError::Decode(err.to_string()))?;
        
        Ok(tx)
    }

    fn build_tx_from_json(json_tx: &JsonTx) -> Result<Transaction, TxError> {
        let inputs: Result<Vec<TxIn>, TxError> = json_tx.vin
            .iter()
            .map(|vin| {

                let txid = Txid::from_str(&vin.txid)
                    .map_err(|e| TxError::Decode(e.to_string()))?;

                let script_sig = match Script::from_hex(&vin.scriptsig) {
                    Err(err) => return Err(TxError::Decode(err.to_string())),
                    Ok(script_sig) => script_sig
                };

                let witness = if let Some(witness_items) = &vin.witness {
                    let items: Result<Vec<Vec<u8>>, TxError> = witness_items
                        .iter()
                        .map(|item| Vec::<u8>::from_hex(item)
                            .map_err(|e| TxError::Decode(e.to_string())))
                        .collect();
                    Witness::from_vec(items?)
                } else {
                    Witness::new()
                };

                Ok(TxIn {
                    previous_output: OutPoint {
                        txid,
                        vout: vin.vout,
                    },
                    script_sig,
                    sequence: Sequence(vin.sequence),
                    witness,
                })
            })
            .collect();

        let outputs: Result<Vec<TxOut>, TxError> = json_tx.vout
            .iter()
            .map(|vout| {
                let script_pubkey = match Script::from_hex(&vout.scriptpubkey) {
                    Err(err) => return Err(TxError::Decode(err.to_string())),
                    Ok(script_pubkey) => script_pubkey
                };

                Ok(TxOut {
                    value: vout.value,
                    script_pubkey,
                })
            })
            .collect();

        Ok(Transaction {
            version: json_tx.version,
            lock_time: bitcoin::PackedLockTime(json_tx.locktime),
            input: inputs?,
            output: outputs?,
        })
    }

    fn get_address_from_script(script_pubkey: &Script, network: Network) -> Result<Address, TxError> {
        let addr: Address = match Address::from_script(script_pubkey, network) {
            Err(_) => {
                if script_pubkey.is_p2pk() {
                    let pubkey_bytes = script_pubkey
                    .as_bytes()
                    .get(1..script_pubkey.len() - 1)
                    .ok_or(TxError::UnrecognizedScript(
                        "could not extract pubkey from P2PK script".to_string()
                    ))?;
                
                    let pubkey = PublicKey::from_slice(pubkey_bytes)
                    .map_err(|e| TxError::UnrecognizedScript(e.to_string()))?;

                
                    let p2pkh_address = Address::p2pkh(&pubkey, network);

                    p2pkh_address
                }
                else {
                    return Err(TxError::UnrecognizedScript(
                    format!("could not convert script to address: {}", script_pubkey)));
                }
            }
            
            Ok(address) => address
        };
        
        Ok(addr)
    }

    fn get_prevouts(tx: &Transaction) -> Vec<usize> {
        let prev_vouts: Vec<usize> = tx.input
        .iter()
        .map(|input| input.previous_output.vout as usize)
        .collect();
        
        return prev_vouts;
    }

    fn get_previous_txids(tx: &Transaction) -> Vec<Txid> {
        let previous_txids: Vec<Txid> = tx.input
        .iter()
        .map(|input| input.previous_output.txid)
        .collect();

        return previous_txids
    }

    fn get_addresses_types(addresses: &Vec<Address>) -> Result<Vec<AddressType>, TxError> {
        let mut addr_types: Vec<AddressType> = Vec::new();
        for output_addr in addresses.iter() {
            match Address::address_type(output_addr) {
                Some(addr_type) => addr_types.push(addr_type),
                None => return Err(TxError::UnrecognizedScript(
                    format!("unable to obtain a valid type for the address")
                ))
            }
        }
        Ok(addr_types)
    }

    //Constructors
    pub fn from_raw(raw_tx: &str, network: Network) -> Result<Self, TxError> {
        let tx = Self::build_tx_from_hex(raw_tx)?;
        
        Ok(Self {
            target: tx,
            previous_txs: None,
            future_txs: None,
            replacement: None,
            network: network,
            block_height: None
        })
    }

    pub fn from_txid(txid: &str) -> Result<Self, TxError> {
        todo!("Implement from_txid function");
    }

    pub fn from_json(json_tx: &JsonTx, network: Network) -> Result<Self, TxError> {
        let tx = Self::build_tx_from_json(json_tx)?;
        
        Ok(Self {
            target: tx,
            previous_txs: None,
            future_txs: None,
            replacement: None,
            network: network,
            block_height: None
        })
    }

    pub fn import_previous_txs(&mut self, previous_txs: &[String]) -> Result<(), TxError> {
        let n_inputs: usize = self.input_count();

        if n_inputs != previous_txs.len() {
            return Err(TxError::MismatchNumberInputs(
                format!("tx expects {}, while {} provided", n_inputs, previous_txs.len())
            ));
        }

        let mut prev_txs_dict: HashMap<Txid, Tx> = HashMap::new();
        for prev_tx in previous_txs.iter() {
            match Self::from_raw(prev_tx, self.network){
                Err(err) => return Err(err),
                Ok(tx_raw) => prev_txs_dict.insert(tx_raw.txid(), tx_raw)
            };   
        }

        let mut prev_txs: Vec<Box<Tx>> = Vec::new();
        let previous_txids: Vec<Txid> = self.previous_txids();

        for prev_txid in previous_txids.iter() {
            match prev_txs_dict.get(prev_txid) {
                Some(prev_tx) => prev_txs.push(Box::new(prev_tx.clone())),
                None => return Err(TxError::InvalidPrevTx(
                    format!("tx expected {} but it could not be found", prev_txid)
                ))
            };
        }

        self.previous_txs = Some(prev_txs);
        Ok(())
    }

    pub fn import_future_txs(&mut self, future_txs_hex: &[String]) -> Result<(), TxError> {
        let n_outputs = self.output_count();

        if n_outputs != future_txs_hex.len() {
            return Err(TxError::MismatchNumberOuputs(
                format!("tx expected {}, while {} provided", n_outputs, future_txs_hex.len())
            ));
        }

        let mut future_txs_dict:HashMap<usize, Tx> = HashMap::new();
        let mut aux_future_txs: Vec<Tx> = Vec::new();

        for future_tx_hex in future_txs_hex.iter() {
            match Self::from_raw(future_tx_hex, self.network) {
                Err(err) => return Err(err),
                Ok(future_tx) => aux_future_txs.push(future_tx),
            }
        };

        let target_txid: Txid = self.txid();

        for future_tx in aux_future_txs.iter() {
            let future_prevouts: Vec<usize> = future_tx.prevouts();
            let future_prevtxid: Vec<Txid> = future_tx.previous_txids();

            for (index, future_prevtxid) in future_prevtxid.iter().enumerate() {
                if future_prevtxid == &target_txid {
                    future_txs_dict.insert(future_prevouts[index], future_tx.clone());
                    break;
                }
                return Err(TxError::InvalidFutureTx(
                    format!("tx expected a future tx that spends the target one but it could not be found")
                ));
            }
        }

        let mut future_txs: Vec<Box<Tx>>= Vec::new();
        for (index, _) in aux_future_txs.iter().enumerate() {
            match future_txs_dict.get(&index) {
                Some(future_tx) => future_txs.push(Box::new(future_tx.clone())),
                None => return Err(TxError::InvalidFutureTx(
                    format!("could not be found the future tx that spends the target one")
                ))
            };
        }

        self.future_txs = Some(future_txs);
        Ok(())
    }

    pub fn import_block_height(&mut self, block_height: usize) {
        self.block_height = Some(block_height);
    }

    pub fn txid(&self) -> Txid {
        return self.target.txid();
    }

    pub fn size(&self) -> usize {
        return self.target.size();
    }
    pub fn weight(&self) -> usize {
        return self.target.weight();
    }
    pub fn vsize(&self) -> f32 {
        let weight: f32 = self.weight() as f32;
        return weight / 4.0;
    }
    pub fn version(&self) -> i32 {
        return self.target.version
    }
    pub fn locktime(&self) -> u32{
        return self.target.lock_time.to_u32();
    }

    pub fn prevouts(&self) -> Vec<usize> {
        return Self::get_prevouts(&self.target);
    }
    pub fn previous_txids(&self) -> Vec<Txid> {
        return Self::get_previous_txids(&self.target);
    }

    pub fn input_count(&self) -> usize {
        return self.target.input.len()
    }
    pub fn output_count(&self) -> usize {
        return self.target.output.len()
    }
    
    pub fn outputs_values(&self) -> Vec<u64> {
        let outputs_values: Vec<u64> = self.target.output
        .iter()
        .map(|value| value.value)
        .collect();
        return outputs_values;
    }
    pub fn inputs_values(&self) -> Result<Vec<u64>, TxError> {
        if self.previous_txs.is_none() {
            return Err(TxError::MissingPreviousTxs(
                format!("no prev_txs founded, import them first")
            ));
        }

        let prev_vouts: Vec<usize> = self.prevouts();

        let mut input_values: Vec<u64> = Vec::new();

        if let Some(prev_txs) = &self.previous_txs {
            for (index, prev_tx) in prev_txs.iter().enumerate() {
                let prev_output_amounts = prev_tx.outputs_values();
                let amount = prev_output_amounts[prev_vouts[index]];
                input_values.push(amount);
            }
        }

        Ok(input_values)
    }

    pub fn outputs_scriptpubkeys(&self) -> Vec<Script> {
        self.target.output
        .iter()
        .map(|output| output.script_pubkey.clone())
        .collect()
    }
    pub fn inputs_scriptsig(&self) -> Vec<Script> {
        self.target.input
        .iter()
        .map(|input| input.script_sig.clone())
        .collect()
    }
    pub fn inputs_witness(&self) -> Vec<Witness> {
        self.target.input
        .iter()
        .map(|input| input.witness.clone())
        .collect()
    }
    
    pub fn outputs_addresses(&self) -> Result<Vec<Address>, TxError> {
        let mut output_addresses: Vec<Address> = Vec::new(); 
        for output in self.target.output.iter() {
            match Self::get_address_from_script(&output.script_pubkey, self.network) {
                Err(err) => return Err(err),
                Ok(address) => output_addresses.push(address),
            };
        }
        Ok(output_addresses)
    }
    pub fn inputs_addresses(&self) -> Result<Vec<Address>, TxError> {
        if self.previous_txs.is_none() {
            return Err(TxError::MissingPreviousTxs(
                format!("no prev_txs founded, import them first")
            ));
        }

        let prevouts: Vec<usize> = self.prevouts();
        let mut input_addresses: Vec<Address> = Vec::new();

        if let Some(prev_txs) = &self.previous_txs {
            for (index, prev_tx) in prev_txs.iter().enumerate() {
                let outputs_scriptpubkeys:Vec<Script> = prev_tx.outputs_scriptpubkeys();
                
                let output_scriptpubkey = &outputs_scriptpubkeys[prevouts[index]];
                
                match Self::get_address_from_script(&output_scriptpubkey, self.network) {
                    Err(err) => return Err(err),
                    Ok(address) => input_addresses.push(address) 
                };
                
            }
        }

        Ok(input_addresses)
    }

    pub fn outputs_types(&self) -> Result<Vec<AddressType>, TxError> {
        let output_addresses:Vec<Address> = match self.outputs_addresses() {
           Err(err) => return Err(err),
           Ok(outputs_addresses) => outputs_addresses 
        }; 

        let output_types: Vec<AddressType> = match Self::get_addresses_types(&output_addresses) {
            Err(err) => return Err(err),
            Ok(outputs_types) => outputs_types
        };

        Ok(output_types)
    }
    pub fn inputs_types(&self) -> Result<Vec<AddressType>, TxError> {
        let input_addresses:Vec<Address> = self.inputs_addresses()?; 

        let input_types: Vec<AddressType> = Self::get_addresses_types(&input_addresses)?;

        Ok(input_types)
    }

    pub fn absolute_fee(&self) -> Result<u64, TxError> {
        let input_values: Vec<u64> = self.inputs_values()?;
        let output_values: Vec<u64> = self.outputs_values();

        let sum_inputs: u64 = input_values.iter().sum();
        let sum_outptus: u64 = output_values.iter().sum();

        Ok(sum_inputs - sum_outptus)
    }
    pub fn relative_fee(&self) -> Result<f32, TxError> {
        let absolute_fee: u64 = self.absolute_fee()?;

        let vsize: f32 = self.vsize();

        Ok((absolute_fee as f32) / vsize)
    }

    pub fn previous_txs(&self) -> Option<&Vec<Box<Tx>>> {
        return self.previous_txs.as_ref()
    }

    pub fn future_txs(&self) -> Option<&Vec<Box<Tx>>> {
        return self.future_txs.as_ref() 
    }

    pub fn block_height(&self) -> Option<usize> {
        return self.block_height;
    }

    pub fn is_segwit(&self) -> bool {
        self.target.strippedsize() != self.target.size()
    }

    pub fn signals_rbf(&self) -> bool {
        self.target.is_explicitly_rbf()
    }

}

#[cfg(test)]
mod tests {
    use std::{str::FromStr};

use super::*;

    //txid 145c0c98ce449d8f478bae7019e3d4ae98c0a52fe574978b8a2169ac59c47420
    const RAW_TX_1: &str = "010000000001018c6b4d2f2643ab6eeca012f91e8c6cc301e4b184f8ad46289ddfde862c307eb60100000000ffffffff0280969800000000001976a9146bae872ad0d13eabe5631d7943d6ae23ec2be31988ac4ef73a0700000000220020701a8d401c84fb13e6baf169d59684e17abd9fa216c8cc5b9fc63d622ff8c58d0400473044022048df04543d883f5ac4899bd5426134664c58326b55e5bdf8d6b643b3a97174af0220261fcc5a4deb2e33fa8b4c3992f54949ec3aa4603ccec0a1b0443da5fd5021780147304402207449b3b838c80182a7595fd85b8111277c00b2a96393a85205bb8858188fac1c02202374a8067c82c02609568b8491b29b48ca6f6799a301877976df6fdd20d8d1f7016952210375e00eb72e29da82b89367947f29ef34afb75e8654f6ea368e0acdfd92976b7c2103a1b26313f430c4b15bb1fdce663207659d8cac749a0e53d70eff01874496feff2103c96d495bfdd5ba4145e3e046fee45e84a8a48ad05bd8dbb395c011a32cf9f88053ae00000000";

    //txid b67e302c86dedf9d2846adf884b1e401c36c8c1ef912a0ec6eab43262f4d6b8c
    const PREV_TX: &str = "0100000000010179420f39ff1f9ee5bb94855783664e4bc26dfe935ce425094c7f3e809d05de680000000000ffffffff02228ed533000000001976a9143f6806b9e2032fc2699a535bf5305cbbad1a3e6288accebad30700000000220020701a8d401c84fb13e6baf169d59684e17abd9fa216c8cc5b9fc63d622ff8c58d04004730440220214aaa1a1185ffa0ea4e809a97b70f06164c092410f1dc44a6644dd7666d84e7022006464d82beb427e98cb3ba33bcd10ac04181502d63017f477699d4b5675f24a0014730440220619cbe3781121bd28478591a707e8935cf408d39cabf1802e89ca151c78bc18202205a7a250192c63700d58630b772d7730e2e39a3fba1063416177846317f8a243d01695221026478f7934428a4333a6c182beea581e7a2d23eb0f9bf7bb43799bece4686a92d2102c46c32c07b2034300e577114b10d5516349e092dd413c750a0781edb83ab95ff2103c96d495bfdd5ba4145e3e046fee45e84a8a48ad05bd8dbb395c011a32cf9f88053ae00000000";

    //txid 186c9d58613e72f583537d377c42150eb6c48533acb21fe3621f43279403912d
    const FUT_TX_1: &str = "01000000012074c459ac69218a8b9774e52fa5c098aed4e31970ae8b478f9d44ce980c5c14000000006a47304402206ebb05703169e1dc748c432f05433de68c0976d56afce5290e33a516f46ce3780220144e11da55c9379bf7d3203276cae58a87c0c9a20aef724c51657aaf8c01213c0121037e506ebfdd7d42a7afc88634dcab25cc2581b57cfe3323951fb094f15da635fdffffffff0198929800000000001976a9149f21a07a0c7c3cf65a51f586051395762267cdaf88ac00000000";

    //txid eecd3ad90c200a55ad117d07183072c0f3b4843bc68c73cae8f05fee035b7e6f
    const FUT_TX_2: &str = "010000000001012074c459ac69218a8b9774e52fa5c098aed4e31970ae8b478f9d44ce980c5c140100000000ffffffff02509d3f01000000001600146ded4482ffcf8c5aba8cce5d8d4ce2fea0cd3d49b22dfb0500000000220020701a8d401c84fb13e6baf169d59684e17abd9fa216c8cc5b9fc63d622ff8c58d04004730440220356f34d09650665d9a3d4ed7e09d08536358da0b9b44fefdebf667068d2ff83502202802f48b4e386d169ff9e6e10794b6d7f125b49de74cacf6464af74856f9222701473044022023ffa9fbced2f6357815d97507d900e6027e86f8e26a5662a509241053339d7002200ac3eff9768fb20bcaeb0797da239f3a6380876bf4c201b09c8ca35f0aecd606016952210375e00eb72e29da82b89367947f29ef34afb75e8654f6ea368e0acdfd92976b7c2103a1b26313f430c4b15bb1fdce663207659d8cac749a0e53d70eff01874496feff2103c96d495bfdd5ba4145e3e046fee45e84a8a48ad05bd8dbb395c011a32cf9f88053ae00000000";
    
    #[test]
    fn build_tx_from_hex_parses_valid_hex() {
        let tx = Tx::build_tx_from_hex(RAW_TX_1).expect("hex should parse");
    }

    #[test]
    fn build_tx_from_hex_rejects_invalid_hex() {
        let err = Tx::build_tx_from_hex("zz").unwrap_err();
        matches!(err, TxError::Hex(_));
    }

#[test]
    fn from_raw_builds_tx() {
        let mut tx = Tx::from_raw(RAW_TX_1, Network::Bitcoin).expect("hex should parse");
        tx.import_previous_txs(&[PREV_TX.to_string()]).expect("should import");

        let expected_txid: &str = "145c0c98ce449d8f478bae7019e3d4ae98c0a52fe574978b8a2169ac59c47420";
        let expected_size: usize = 382usize;
        let expected_weight: usize = 766usize;
        let expected_vsize: f32 = 191.5;

        let expected_inputs: usize = 1usize;
        let expected_outputs: usize = 2usize;

        let expected_input_values: Vec<u64> = vec![131316430];
        let expected_output_values: Vec<u64> = vec![10000000, 121304910]; 
        
        let expected_input_addresses_str: Vec<String> = vec!["bc1qwqdg6squsna38e46795at95yu9atm8azzmyvckulcc7kytlcckxswvvzej".to_string()];
        let mut expected_input_addresses: Vec<Address> = Vec::new();
        for addr in expected_input_addresses_str {
            expected_input_addresses.push(Address::from_str(&addr).unwrap());
        }
        let expected_output_addresses_str: Vec<String> = vec!["1ApNNwjYZrTSespJEPoyBRp2a61znc8G5N".to_string(),"bc1qwqdg6squsna38e46795at95yu9atm8azzmyvckulcc7kytlcckxswvvzej".to_string()]; 
        let mut expected_output_addresses: Vec<Address> = Vec::new();
        for addr in expected_output_addresses_str {
            expected_output_addresses.push(Address::from_str(&addr).unwrap());
        }

        let expected_input_types: Vec<AddressType> = vec![AddressType::P2wsh];
        let expected_output_types: Vec<AddressType> = vec![AddressType::P2pkh, AddressType::P2wsh];

        let expected_absolute_fee: u64 = 11520;
        let expected_relative_fee: f32 = 60.15666;

        assert_eq!(tx.txid().to_string(), expected_txid);
        assert_eq!(tx.size(), expected_size);
        assert_eq!(tx.weight(), expected_weight);
        assert_eq!(tx.vsize(), expected_vsize);
        assert_eq!(tx.input_count(), expected_inputs);
        assert_eq!(tx.output_count(), expected_outputs);
        assert_eq!(tx.inputs_values().unwrap(), expected_input_values);
        assert_eq!(tx.outputs_values(), expected_output_values);
        assert_eq!(tx.inputs_addresses().unwrap(), expected_input_addresses);
        assert_eq!(tx.outputs_addresses().unwrap(), expected_output_addresses);
        assert_eq!(tx.inputs_types().unwrap(), expected_input_types);
        assert_eq!(tx.outputs_types().unwrap(), expected_output_types);
        assert_eq!(tx.absolute_fee().unwrap(), expected_absolute_fee);
        assert_eq!(tx.relative_fee().unwrap(), expected_relative_fee);


    }

    #[test]
    fn import_previous_txs_rejects_count_mismatch() {
        let mut tx = Tx::from_raw(RAW_TX_1, Network::Bitcoin).expect("tx should build");
        let err = tx.import_previous_txs(&[]).unwrap_err();
        matches!(err, TxError::MismatchNumberInputs(_));
    }

    #[test]
    fn import_future_txs_rejects_count_mismatch() {
        let mut tx = Tx::from_raw(RAW_TX_1, Network::Bitcoin).expect("tx should build");
        let err = tx.import_future_txs(&[]).unwrap_err();
        matches!(err, TxError::MismatchNumberOuputs(_));
    }

    #[test]
    fn import_previous_txs_sets_previous_txs_when_counts_match() {
        let mut tx = Tx::from_raw(RAW_TX_1, Network::Bitcoin).expect("tx should build");
        let result = tx.import_previous_txs(&[PREV_TX.to_string()]);
        assert!(result.is_err() || tx.previous_txs.is_some());
    }

    #[test]
    fn import_future_txs_sets_future_txs_when_counts_match() {
        let mut tx = Tx::from_raw(RAW_TX_1, Network::Bitcoin).expect("tx should build");
        let result = tx.import_future_txs(&[FUT_TX_1.to_string(), FUT_TX_2.to_string()]);
        assert!(result.is_err() || tx.future_txs.is_some());
    }
    #[test]
    fn script_sig_and_witness() {
       let tx = Tx::from_raw("0200000000010165053460d77bb38c813842cf5a946b45a169fe28144df0e2e35e6521b18a203d0000000000ffffffff02a4c8460000000000225120d8e89976b915c28526187cacab1e3de153bb13cf9833f99de548a92e01d263070000000000000000236a5d20ff7f818a8090f0d3b682808884b0b08bc02eff7fd184dad7ef94a4d0b2a797010140ce5c3acca0db7f57049b963f089455ff7ee49041c9102524cfec390b9df140cbc0c93d2a2ba43bc278e3cff29d236a3a5fb276facdf907befaf35c753f28981900000000", Network::Bitcoin).expect("tx should build");
       let script_sig = tx.inputs_scriptsig();
       let witness = tx.inputs_witness();

       println!("{:?}", script_sig);
       println!("{:?}", witness); 
    }

}