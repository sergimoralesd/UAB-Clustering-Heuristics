use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::heuristics::{
    AddressTypeChange, BackdatingChange, ConsistentAddressTypeChange, FeeAbsoluteChange,
    FeeRelativeChange, FutureReusedAddressChange, InputOrderChange, LocktimeChange,
    LowConfirmationValue, LowRChange, MalformedCoinjoinChange, MultisignatureChange,
    OptimalChange, OutputOrderChange, PastReusedAddressChange, PresentReusedAddressChange,
    RBFChange, RoundedChange, RoundedFiatChange, SegwitConformChange, SignalRBFChange,
    SmallerOuputChange, UncompressPublicKeyChange, VersionChange,
};
use crate::types::AppError;

macro_rules! define_simple_heuristic {
    ($py_struct:ident, $rust_ty:ty, $python_name:expr, $ctor:expr) => {
        #[pyclass(name = $python_name)]
        struct $py_struct {
            inner: $rust_ty,
        }

        #[pymethods]
        impl $py_struct {
            #[new]
            fn new() -> Self {
                Self { inner: $ctor }
            }

            fn name(&self) -> String {
                self.inner.name()
            }

            fn input_data_requirements(&self) -> u8 {
                self.inner.input_data_requirements().value()
            }

            fn apply(&self, tx: &PyTx) -> PyResult<Vec<bool>> {
                self.inner.apply(&tx.inner).map_err(py_error)
            }
        }
    };
}

define_simple_heuristic!(PyAddressTypeChange, AddressTypeChange, "AddressTypeChange", AddressTypeChange);
define_simple_heuristic!(PyBackdatingChange, BackdatingChange, "BackdatingChange", BackdatingChange);
define_simple_heuristic!(PyConsistentAddressTypeChange, ConsistentAddressTypeChange, "ConsistentAddressTypeChange", ConsistentAddressTypeChange);
define_simple_heuristic!(PyFeeAbsoluteChange, FeeAbsoluteChange, "FeeAbsoluteChange", FeeAbsoluteChange);
define_simple_heuristic!(PyFeeRelativeChange, FeeRelativeChange, "FeeRelativeChange", FeeRelativeChange);
define_simple_heuristic!(PyFutureReusedAddressChange, FutureReusedAddressChange, "FutureReusedAddressChange", FutureReusedAddressChange);
define_simple_heuristic!(PyInputOrderChange, InputOrderChange, "InputOrderChange", InputOrderChange);
define_simple_heuristic!(PyLocktimeChange, LocktimeChange, "LocktimeChange", LocktimeChange);
define_simple_heuristic!(PyLowConfirmationValue, LowConfirmationValue, "LowConfirmationValue", LowConfirmationValue);
define_simple_heuristic!(PyLowRChange, LowRChange, "LowRChange", LowRChange);
define_simple_heuristic!(PyMalformedCoinjoinChange, MalformedCoinjoinChange, "MalformedCoinjoinChange", MalformedCoinjoinChange);
define_simple_heuristic!(PyMultisignatureChange, MultisignatureChange, "MultisignatureChange", MultisignatureChange);
define_simple_heuristic!(PyOptimalChange, OptimalChange, "OptimalChange", OptimalChange);
define_simple_heuristic!(PyOutputOrderChange, OutputOrderChange, "OutputOrderChange", OutputOrderChange);
define_simple_heuristic!(PyPastReusedAddressChange, PastReusedAddressChange, "PastReusedAddressChange", PastReusedAddressChange);
define_simple_heuristic!(PyPresentReusedAddressChange, PresentReusedAddressChange, "PresentReusedAddressChange", PresentReusedAddressChange);
define_simple_heuristic!(PyRBFChange, RBFChange, "RBFChange", RBFChange);
define_simple_heuristic!(PySegwitConformChange, SegwitConformChange, "SegwitConformChange", SegwitConformChange);
define_simple_heuristic!(PySignalRBFChange, SignalRBFChange, "SignalRBFChange", SignalRBFChange);
define_simple_heuristic!(PySmallerOuputChange, SmallerOuputChange, "SmallerOuputChange", SmallerOuputChange);
define_simple_heuristic!(PyUncompressPublicKeyChange, UncompressPublicKeyChange, "UncompressPublicKeyChange", UncompressPublicKeyChange);
define_simple_heuristic!(PyVersionChange, VersionChange, "VersionChange", VersionChange);

#[pyclass(name = "RoundedChange")]
struct PyRoundedChange {
    inner: RoundedChange,
}

#[pymethods]
impl PyRoundedChange {
    #[new]
    #[pyo3(signature = (precision_parameter = 2))]
    fn new(precision_parameter: u8) -> Self {
        Self { inner: RoundedChange::new(precision_parameter) }
    }

    fn name(&self) -> String {
        self.inner.name()
    }

    fn input_data_requirements(&self) -> u8 {
        self.inner.input_data_requirements().value()
    }

    fn apply(&self, tx: &PyTx) -> PyResult<Vec<bool>> {
        self.inner.apply(&tx.inner).map_err(py_error)
    }
}

#[pyclass(name = "RoundedFiatChange")]
struct PyRoundedFiatChange {
    inner: RoundedFiatChange,
}

#[pymethods]
impl PyRoundedFiatChange {
    #[new]
    #[pyo3(signature = (precision_parameter = 2, currency = "USD"))]
    fn new(precision_parameter: u8, currency: &str) -> Self {
        Self { inner: RoundedFiatChange::new(precision_parameter, currency.to_string()) }
    }

    fn name(&self) -> String {
        self.inner.name()
    }

    fn input_data_requirements(&self) -> u8 {
        self.inner.input_data_requirements().value()
    }

    fn apply(&self, tx: &PyTx) -> PyResult<Vec<bool>> {
        self.inner.apply(&tx.inner).map_err(py_error)
    }
}

#[pymodule]
fn change_heuristics(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTx>()?;
    m.add_class::<PyAddressTypeChange>()?;
    m.add_class::<PyBackdatingChange>()?;
    m.add_class::<PyConsistentAddressTypeChange>()?;
    m.add_class::<PyFeeAbsoluteChange>()?;
    m.add_class::<PyFeeRelativeChange>()?;
    m.add_class::<PyFutureReusedAddressChange>()?;
    m.add_class::<PyInputOrderChange>()?;
    m.add_class::<PyLocktimeChange>()?;
    m.add_class::<PyLowConfirmationValue>()?;
    m.add_class::<PyLowRChange>()?;
    m.add_class::<PyMalformedCoinjoinChange>()?;
    m.add_class::<PyMultisignatureChange>()?;
    m.add_class::<PyOptimalChange>()?;
    m.add_class::<PyOutputOrderChange>()?;
    m.add_class::<PyPastReusedAddressChange>()?;
    m.add_class::<PyPresentReusedAddressChange>()?;
    m.add_class::<PyRBFChange>()?;
    m.add_class::<PyRoundedChange>()?;
    m.add_class::<PyRoundedFiatChange>()?;
    m.add_class::<PySegwitConformChange>()?;
    m.add_class::<PySignalRBFChange>()?;
    m.add_class::<PySmallerOuputChange>()?;
    m.add_class::<PyUncompressPublicKeyChange>()?;
    m.add_class::<PyVersionChange>()?;
    Ok(())
}