use bitcoin::consensus::{deserialize, serialize};
use bitcoin::{Address, Network, Script, Transaction};
use pyo3::exceptions::{PyAssertionError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList, PyString, PyType};

#[pyclass]
pub struct Tx {
    tx: Transaction,
    previous_txids: Option<Vec<String>>,
    futures_txids: Option<Vec<String>>,
    previous_txs: Option<Vec<PyObject>>,
    future_txs: Option<Vec<Option<PyObject>>>,
}

impl Tx {
    fn parse_raw(raw: &[u8]) -> PyResult<Transaction> {
        deserialize(raw).map_err(|e| PyValueError::new_err(format!("Invalid raw tx: {e}")))
    }

    fn py_raw_to_vec(raw_tx: &PyAny) -> PyResult<Vec<u8>> {
        if let Ok(s) = raw_tx.extract::<&str>() {
            return hex::decode(s)
                .map_err(|e| PyValueError::new_err(format!("Invalid hex tx: {e}")));
        }
        if let Ok(pybytes) = raw_tx.downcast::<PyBytes>() {
            return Ok(pybytes.as_bytes().to_vec());
        }
        Err(PyValueError::new_err(
            "raw_tx must be bytes or hex string",
        ))
    }

    fn addr_from_script(script: &Script) -> Option<String> {
        if let Ok(addr) = Address::from_script(script, Network::Bitcoin) {
            return Some(addr.to_string());
        }

        let bytes = script.as_bytes();
        // Mimic Python's script_pubkey[1:-1] unconditionally
        let pubkey_bytes = if bytes.len() >= 2 {
            &bytes[1..bytes.len() - 1]
        } else {
            &[]
        };

        use bitcoin::hashes::{hash160, Hash};
        let hash = hash160::Hash::hash(pubkey_bytes);
        let payload = bitcoin::util::address::Payload::PubkeyHash(bitcoin::PubkeyHash::from_hash(hash));
        let addr = bitcoin::Address {
            network: Network::Bitcoin,
            payload,
        };
        Some(addr.to_string())
    }

    fn get_prev_txs(&self) -> PyResult<&Vec<PyObject>> {
        self.previous_txs
            .as_ref()
            .ok_or_else(|| PyAssertionError::new_err("Call import_previous_txs first"))
    }
}

#[pymethods]
impl Tx {
    #[new]
    #[pyo3(signature = (base_tx_raw=None, previous_txids=None, futures_txids=None))]
    fn new(
        base_tx_raw: Option<&PyAny>,
        previous_txids: Option<Vec<String>>,
        futures_txids: Option<Vec<String>>,
    ) -> PyResult<Self> {
        let tx = if let Some(raw_obj) = base_tx_raw {
            let raw = Self::py_raw_to_vec(raw_obj)?;
            Self::parse_raw(&raw)?
        } else {
            return Err(PyValueError::new_err("base_tx_raw is required"));
        };

        Ok(Self {
            tx,
            previous_txids,
            futures_txids,
            previous_txs: None,
            future_txs: None,
        })
    }

    #[classmethod]
    #[pyo3(signature = (raw_tx, network="bitcoin"))]
    fn from_raw(_cls: &PyType, raw_tx: &PyAny, network: &str) -> PyResult<Self> {
        if network != "bitcoin" {
            return Err(PyValueError::new_err("Only bitcoin network is supported"));
        }
        let raw = Self::py_raw_to_vec(raw_tx)?;
        let tx = Self::parse_raw(&raw)?;
        Ok(Self {
            tx,
            previous_txids: None,
            futures_txids: None,
            previous_txs: None,
            future_txs: None,
        })
    }

    #[classmethod]
    #[pyo3(signature = (txid, network="bitcoin"))]
    fn from_txid(_cls: &PyType, py: Python<'_>, txid: &str, network: &str) -> PyResult<Self> {
        if network != "bitcoin" {
            return Err(PyValueError::new_err("Only bitcoin network is supported"));
        }

        let utils = py.import("uab_heuristics.utils")?;
        let raw = utils.getattr("get_raw_tx_from_id")?.call1((txid,))?;
        let raw_bytes = if let Ok(s) = raw.extract::<&str>() {
            hex::decode(s)
                .map_err(|e| PyValueError::new_err(format!("Invalid hex tx from txid: {e}")))?
        } else if let Ok(b) = raw.downcast::<PyBytes>() {
            b.as_bytes().to_vec()
        } else {
            return Err(PyValueError::new_err(
                "get_raw_tx_from_id must return hex string or bytes",
            ));
        };

        let tx = Self::parse_raw(&raw_bytes)?;
        Ok(Self {
            tx,
            previous_txids: None,
            futures_txids: None,
            previous_txs: None,
            future_txs: None,
        })
    }

    #[classmethod]
    fn from_json(_cls: &PyType, _filename: &str, _network: &str) -> PyResult<Self> {
        Err(PyRuntimeError::new_err("from_json is not implemented"))
    }

    #[classmethod]
    fn from_psbt(_cls: &PyType, _psbt: &PyAny, _network: &str) -> PyResult<Self> {
        Err(PyRuntimeError::new_err("from_psbt is not implemented"))
    }

    #[pyo3(signature = (prev_txs=None, network="bitcoin"))]
    fn import_previous_txs(&mut self, py: Python<'_>, prev_txs: Option<&PyAny>, network: &str) -> PyResult<()> {
        if self.previous_txs.is_some() {
            return Ok(());
        }
        if network != "bitcoin" {
            return Err(PyValueError::new_err("Only bitcoin network is supported"));
        }

        if let Some(prev) = prev_txs {
            let list: Vec<PyObject> = prev.extract()?;
            self.previous_txs = Some(list);
            return Ok(());
        }

        let txids = if let Some(ids) = &self.previous_txids {
            ids.clone()
        } else {
            self.tx
                .input
                .iter()
                .map(|i| i.previous_output.txid.to_string())
                .collect::<Vec<_>>()
        };

        let mut built = Vec::with_capacity(txids.len());
        for prev_txid in txids {
            let prev_obj = Self::from_txid(py.get_type::<Tx>(), py, &prev_txid, network)?;
            built.push(Py::new(py, prev_obj)?.into_py(py));
        }
        self.previous_txs = Some(built);
        Ok(())
    }

    #[pyo3(signature = (future_txs=None, future_txids=None, network="bitcoin"))]
    fn import_future_txs(
        &mut self,
        py: Python<'_>,
        future_txs: Option<&PyAny>,
        future_txids: Option<Vec<String>>,
        network: &str,
    ) -> PyResult<()> {
        if self.future_txs.is_some() {
            return Ok(());
        }
        if network != "bitcoin" {
            return Err(PyValueError::new_err("Only bitcoin network is supported"));
        }

        if let Some(futures) = future_txs {
            let list: Vec<Option<PyObject>> = futures.extract()?;
            self.future_txs = Some(list);
            return Ok(());
        }

        let ids = if let Some(v) = future_txids {
            v
        } else if let Some(v) = &self.futures_txids {
            v.clone()
        } else {
            return Err(PyValueError::new_err(
                "Include future txs_ids to compute the future_txs",
            ));
        };

        let mut slots: Vec<Option<PyObject>> = vec![None; self.output_count()];
        let self_txid = self.txid();

        for future_id in ids {
            let future_obj = Self::from_txid(py.get_type::<Tx>(), py, &future_id, network)?;
            let future_py = Py::new(py, future_obj)?;
            let future_ref = future_py.borrow(py);
            for txin in &future_ref.tx.input {
                if txin.previous_output.txid.to_string() == self_txid {
                    let n = txin.previous_output.vout as usize;
                    if n < slots.len() {
                        slots[n] = Some(future_py.clone().into_py(py));
                    }
                }
            }
        }

        self.future_txs = Some(slots);
        Ok(())
    }

    #[getter]
    fn txid(&self) -> String {
        self.tx.txid().to_string()
    }

    #[getter]
    fn size(&self) -> usize {
        serialize(&self.tx).len()
    }

    #[getter]
    fn weight(&self) -> usize {
        self.tx.weight()
    }

    #[getter]
    fn vsize(&self) -> f64 {
        self.tx.vsize() as f64
    }

    #[getter]
    fn input_count(&self) -> usize {
        self.tx.input.len()
    }

    #[getter]
    fn output_count(&self) -> usize {
        self.tx.output.len()
    }

    #[getter]
    fn outputs_values(&self) -> Vec<u64> {
        self.tx.output.iter().map(|o| o.value).collect()
    }

    #[getter]
    fn outputs_script_pub_key(&self) -> Vec<String> {
        self.tx
            .output
            .iter()
            .map(|o| hex::encode(o.script_pubkey.as_bytes()))
            .collect()
    }

    #[getter]
    fn outputs_scriptPubKey(&self) -> Vec<String> {
        self.outputs_script_pub_key()
    }

    #[getter]
    fn outputs_addresses(&self) -> Vec<Option<String>> {
        self.tx
            .output
            .iter()
            .map(|o| Self::addr_from_script(&o.script_pubkey))
            .collect()
    }

    #[getter]
    fn previous_txid(&self) -> Vec<String> {
        self.tx
            .input
            .iter()
            .map(|i| i.previous_output.txid.to_string())
            .collect()
    }

    #[getter]
    fn prevouts(&self) -> Vec<String> {
        self.tx
            .input
            .iter()
            .map(|i| format!("{}:{}", i.previous_output.txid, i.previous_output.vout))
            .collect()
    }

    #[getter]
    fn locktime(&self) -> u32 {
        self.tx.lock_time.into()
    }

    #[getter]
    fn version(&self) -> i32 {
        self.tx.version
    }

    #[getter]
    fn inputs_sequence(&self) -> Vec<u32> {
        self.tx
            .input
            .iter()
            .map(|i| i.sequence.to_consensus_u32())
            .collect()
    }

    #[getter]
    fn inputs_scriptSig(&self) -> Vec<String> {
        self.tx
            .input
            .iter()
            .map(|i| hex::encode(i.script_sig.as_bytes()))
            .collect()
    }

    #[getter]
    fn inputs_witness(&self) -> Vec<Vec<String>> {
        self.tx
            .input
            .iter()
            .map(|i| i.witness.iter().map(hex::encode).collect())
            .collect()
    }

    #[getter]
    fn is_segwit(&self) -> bool {
        self.tx.input.iter().any(|i| !i.witness.is_empty())
    }

    #[getter]
    fn previous_txs<'py>(&self, py: Python<'py>) -> PyResult<&'py PyList> {
        let list = self.previous_txs.as_ref().cloned().unwrap_or_default();
        Ok(PyList::new(py, list))
    }

    #[getter]
    fn future_txs<'py>(&self, py: Python<'py>) -> PyResult<&'py PyList> {
        let list = self.future_txs.as_ref().cloned().unwrap_or_default();
        Ok(PyList::new(py, list))
    }

    #[getter]
    fn future_txid<'py>(&self, py: Python<'py>) -> PyResult<&'py PyList> {
        let mut out = Vec::new();
        if let Some(futures) = &self.future_txs {
            for maybe_tx in futures {
                if let Some(tx_obj) = maybe_tx {
                    let txid = tx_obj.as_ref(py).getattr("txid")?;
                    out.push(txid.into_py(py));
                } else {
                    out.push(py.None());
                }
            }
        }
        Ok(PyList::new(py, out))
    }

    #[getter]
    fn inputs_values(&self, py: Python<'_>) -> PyResult<Vec<i64>> {
        let prev_txs = self.get_prev_txs()?;
        let mut values = Vec::with_capacity(self.tx.input.len());

        for (i, txin) in self.tx.input.iter().enumerate() {
            let prev_tx = prev_txs
                .get(i)
                .ok_or_else(|| PyAssertionError::new_err("previous tx list does not match input count"))?;
            let outputs_values = prev_tx.as_ref(py).getattr("outputs_values")?;
            let outputs: Vec<i64> = outputs_values.extract()?;
            let idx = txin.previous_output.vout as usize;
            let value = outputs
                .get(idx)
                .ok_or_else(|| PyAssertionError::new_err("prev output index out of range"))?;
            values.push(*value);
        }

        Ok(values)
    }

    #[getter]
    fn inputs_addresses(&self, py: Python<'_>) -> PyResult<Vec<Option<String>>> {
        let prev_txs = self.get_prev_txs()?;
        let mut addresses = Vec::with_capacity(self.tx.input.len());

        for (i, txin) in self.tx.input.iter().enumerate() {
            let prev_tx = prev_txs
                .get(i)
                .ok_or_else(|| PyAssertionError::new_err("previous tx list does not match input count"))?;
            let scripts_obj = prev_tx.as_ref(py).getattr("outputs_scriptPubKey")?;
            let scripts: Vec<String> = scripts_obj.extract()?;
            let idx = txin.previous_output.vout as usize;
            let script_hex = scripts
                .get(idx)
                .ok_or_else(|| PyAssertionError::new_err("prev output index out of range"))?;

            let script_bytes = hex::decode(script_hex)
                .map_err(|e| PyValueError::new_err(format!("Invalid script hex: {e}")))?;
            let script = Script::from(script_bytes);
            addresses.push(Self::addr_from_script(&script));
        }

        Ok(addresses)
    }

    #[getter]
    fn absolute_fee(&self, py: Python<'_>) -> PyResult<i64> {
        let inputs = self.inputs_values(py)?;
        let input_sum: i64 = inputs.iter().sum();
        let output_sum: i64 = self.tx.output.iter().map(|o| o.value as i64).sum();
        Ok(input_sum - output_sum)
    }

    #[getter]
    fn relative_fee(&self, py: Python<'_>) -> PyResult<i64> {
        let abs = self.absolute_fee(py)?;
        let v = self.vsize();
        if v <= 0.0 {
            return Err(PyRuntimeError::new_err("Invalid vsize"));
        }
        // satoshis per 1000 virtual bytes
        Ok((abs * 1000) / (v as i64)) 
    }

    #[getter]
    fn inputs_types(&self, py: Python<'_>) -> PyResult<Vec<PyObject>> {
        let utils = py.import("uab_heuristics.utils")?;
        let get_address_type = utils.getattr("get_address_type")?;
        let addrs = self.inputs_addresses(py)?;
        let mut out = Vec::with_capacity(addrs.len());
        for addr in addrs {
            if let Some(a) = addr {
                let t = get_address_type.call1((PyString::new(py, &a),))?;
                out.push(t.into_py(py));
            } else {
                out.push(py.None());
            }
        }
        Ok(out)
    }

    #[getter]
    fn outputs_types(&self, py: Python<'_>) -> PyResult<Vec<PyObject>> {
        let utils = py.import("uab_heuristics.utils")?;
        let get_address_type = utils.getattr("get_address_type")?;
        let addrs = self.outputs_addresses();
        let mut out = Vec::with_capacity(addrs.len());
        for addr in addrs {
            if let Some(a) = addr {
                let t = get_address_type.call1((PyString::new(py, &a),))?;
                out.push(t.into_py(py));
            } else {
                out.push(py.None());
            }
        }
        Ok(out)
    }

    fn print_summary(&self, py: Python<'_>) -> PyResult<()> {
        println!("=== Transaction Summary ===");
        println!("TXID: {}", self.txid());
        println!("Size: {} bytes", self.size());
        println!("Virtual Size: {} vbytes", self.vsize());
        println!("Version: {}", self.version());
        println!("Locktime: {}", self.locktime());
        println!("Absolute Fee: {}", self.absolute_fee(py)?);
        println!("Relative Fee: {}", self.relative_fee(py)?);
        Ok(())
    }

    #[getter]
    fn is_segwit_conform(&self, py: Python<'_>) -> PyResult<bool> {
        let witness_types = ["p2wpkh", "p2wsh", "p2tr", "p2sh-p2wpkh"];
        let inputs_types = self.inputs_types(py)?;

        let has_segwit_input = inputs_types.iter().any(|t| {
            t.extract::<String>(py)
                .map(|s| witness_types.contains(&s.as_str()))
                .unwrap_or(false)
        });

        let uses_segwit_serialization = self.is_segwit();

        Ok(has_segwit_input == uses_segwit_serialization)
    }

    #[getter]
    fn has_uncompressed_public_keys(&self, py: Python<'_>) -> PyResult<bool> {
        let inputs_types = self.inputs_types(py)?;
        let prev_txs = self.get_prev_txs();
        
        for (i, txin) in self.tx.input.iter().enumerate() {
            let type_str = if let Some(t) = inputs_types.get(i) {
                if let Ok(s) = t.extract::<String>(py) {
                    s
                } else {
                    continue;
                }
            } else {
                continue;
            };

            if type_str == "p2pkh" {
                let script_sig = &txin.script_sig;
                let instructions: Vec<_> = script_sig.instructions().filter_map(|i| i.ok()).collect();
                if instructions.len() >= 2 {
                    if let bitcoin::blockdata::script::Instruction::PushBytes(bytes) = &instructions[1] {
                        let bytes_slice = bytes;
                        if bytes_slice.len() == 65 && bytes_slice[0] == 0x04 {
                            return Ok(true);
                        }
                    }
                }
            } else if type_str == "p2ms" {
                if let Ok(prev_txs_list) = prev_txs {
                    if let Some(prev_tx) = prev_txs_list.get(i) {
                        if let Ok(outputs_script_pub_key) = prev_tx.bind(py).getattr("outputs_scriptPubKey") {
                            if let Ok(scripts) = outputs_script_pub_key.extract::<Vec<String>>() {
                                let idx = txin.previous_output.vout as usize;
                                if let Some(script_hex) = scripts.get(idx) {
                                    if let Ok(script_bytes) = hex::decode(script_hex) {
                                        let script = Script::from(script_bytes);
                                        for instruction in script.instructions() {
                                            if let Ok(bitcoin::blockdata::script::Instruction::PushBytes(bytes)) = instruction {
                                                let bytes_slice = bytes;
                                                if bytes_slice.len() == 65 && bytes_slice[0] == 0x04 {
                                                    return Ok(true);
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        Ok(false)
    }
}

#[pymodule]
fn rust_tx_core(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<Tx>()?;
    Ok(())
}
