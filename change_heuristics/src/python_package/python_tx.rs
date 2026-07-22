pub(crate) use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use crate::tx::Tx as RustTx;
use crate::types::TxError;


fn py_error(err: TxError) -> PyErr {
    PyValueError::new_err(err.to_string())
}

fn parse_network(network: &str) -> PyResult<bitcoin::Network> {
    match network.to_lowercase().as_str() {
        "bitcoin" => Ok(bitcoin::Network::Bitcoin),
        "testnet" => Ok(bitcoin::Network::Testnet),
        "signet" => Ok(bitcoin::Network::Signet),
        "regtest" => Ok(bitcoin::Network::Regtest),
        _ => Err(PyValueError::new_err(format!("unsupported network: {network}"))),
    }
}

#[pyclass]
pub struct PyTx {
    pub(crate) inner: RustTx,
}

#[pymethods]
impl PyTx {
    #[new]
    #[pyo3(signature = (raw_tx, network = "bitcoin"))]
    fn new(raw_tx: &str, network: &str) -> PyResult<Self> {
        let inner = RustTx::from_raw(raw_tx, parse_network(network)?)
            .map_err(py_error)?;
        Ok(Self { inner })
    }

    #[staticmethod]
    #[pyo3(signature = (raw_tx, network = "bitcoin"))]
    fn from_raw(raw_tx: &str, network: &str) -> PyResult<Self> {
        Self::new(raw_tx, network)
    }

    fn txid(&self) -> String {
        self.inner.txid().to_string()
    }

    fn size(&self) -> usize {
        self.inner.size()
    }
    fn weight(&self) -> usize {
        self.inner.weight()
    }
    fn vsize(&self) -> f32 {
        self.inner.vsize()
    }
    
    fn input_count(&self) -> usize {
        self.inner.input_count()
    }
    fn output_count(&self) -> usize {
        self.inner.output_count()
    }

    fn outputs_values(&self) -> Vec<u64> {
        self.inner.outputs_values()
    }
    fn inputs_values(&self) -> PyResult<Vec<u64>> {
        self.inner.inputs_values().map_err(py_error)
    }
    
    fn outputs_addresses(&self) -> PyResult<Vec<String>> {
        self.inner.outputs_addresses()
            .map_err(py_error)
            .map(|addrs| addrs.into_iter().map(|a| a.to_string()).collect())
    }
    fn inputs_addresses(&self) -> PyResult<Vec<String>> {
        self.inner.inputs_addresses()
            .map_err(py_error)
            .map(|addrs| addrs.into_iter().map(|a| a.to_string()).collect())
    }
    
    fn outputs_types(&self) -> PyResult<Vec<String>> {
        self.inner.outputs_types()
            .map_err(py_error)
            .map(|types| types.into_iter().map(|t| format!("{t:?}")).collect())
    }
    fn inputs_types(&self) -> PyResult<Vec<String>> {
        self.inner.inputs_types()
            .map_err(py_error)
            .map(|types| types.into_iter().map(|t| format!("{t:?}")).collect())
    }

    fn prevouts(&self) -> Vec<usize> {
        self.inner.prevouts()
    }

    fn previous_txids(&self) -> Vec<String> {
        self.inner.previous_txids().into_iter().map(|txid| txid.to_string()).collect()
    }

    fn is_segwit(&self) -> bool {
        self.inner.is_segwit()
    }

    fn signals_rbf(&self) -> bool {
        self.inner.signals_rbf()
    }

    fn version(&self) -> i32 {
        self.inner.version()
    }

    fn locktime(&self) -> u32 {
        self.inner.locktime()
    }

    fn absolute_fee(&self) -> PyResult<u64> {
        self.inner.absolute_fee().map_err(py_error)
    }
    fn relative_fee(&self) -> PyResult<f32> {
        self.inner.relative_fee().map_err(py_error)
    }

    fn previous_txs(&self) -> Vec<String> {
        self.inner.previous_txs()
            .map(|txs| txs.iter().map(|tx| tx.txid().to_string()).collect())
            .unwrap_or_default()
    }

    fn future_txs(&self) -> Vec<String> {
        self.inner.future_txs()
            .map(|txs| txs.iter().map(|tx| tx.txid().to_string()).collect())
            .unwrap_or_default()
    }

    fn block_height(&self) -> Option<usize> {
        self.inner.block_height()
    }

    fn replacement(&self) -> Option<String> {
        self.inner.replacement().map(|tx| tx.txid().to_string())
    }

    fn outputs_scriptpubkeys(&self) -> Vec<String> {
        self.inner.outputs_scriptpubkeys()
            .into_iter()
            .map(|script| script.to_string())
            .collect()
    }

    fn inputs_scriptsig(&self) -> Vec<String> {
        self.inner.inputs_scriptsig()
            .into_iter()
            .map(|script| script.to_string())
            .collect()
    }

    fn inputs_witness(&self) -> Vec<Vec<String>> {
        self.inner.inputs_witness()
            .into_iter()
            .map(|witness| {
                witness
                    .to_vec()
                    .into_iter()
                    .map(|item| hex::encode(item))
                    .collect()
            })
            .collect()
    }

    fn import_previous_txs(&mut self, previous_txs: Vec<Py<PyAny>>, py: Python<'_>) -> PyResult<()> {
        let txs: Vec<RustTx> = previous_txs
            .into_iter()
            .map(|tx| {
                let tx_ref = tx.bind(py).extract::<PyRef<'_, PyTx>>()?;
                Ok(tx_ref.inner.clone())
            })
            .collect::<PyResult<Vec<_>>>()?;

        self.inner.import_previous_txs(txs).map_err(py_error)?;
        Ok(())
    }

    fn import_future_txs(&mut self, future_txs: Vec<Py<PyAny>>, py: Python<'_>) -> PyResult<()> {
        let txs: Vec<RustTx> = future_txs
            .into_iter()
            .map(|tx| {
                let tx_ref = tx.bind(py).extract::<PyRef<'_, PyTx>>()?;
                Ok(tx_ref.inner.clone())
            })
            .collect::<PyResult<Vec<_>>>()?;

        self.inner.import_future_txs(txs).map_err(py_error)?;
        Ok(())
    }

    fn import_block_height(&mut self, block_height: usize) {
        self.inner.import_block_height(block_height);
    }

    fn import_replacement_tx(&mut self, replacement: &str) -> PyResult<()> {
        self.inner.import_replacement_tx(replacement.to_string()).map_err(py_error)?;
        Ok(())
    }
}
