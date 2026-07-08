use std::fmt::{self};

#[derive(Debug)]
pub enum TxError {
    Hex(String),
    Decode(String),
    MismatchNumberInputs(String),
    MismatchNumberOuputs(String),
    MissingPreviousTxs(String),
    MissingFutureTxs(String),
    InvalidPrevTx(String),
    InvalidFutureTx(String),
    UnrecognizedScript(String),
}

impl fmt::Display for TxError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TxError::Hex(err) => write!(f, "failed to decode the transaction hex: {err}"),
            TxError::Decode(err) => write!(f, "failed to deserialize the transaction: {err}"),
            TxError::MismatchNumberInputs(err) => write!(f, "not enough inputs provided: {err}"),
            TxError::MismatchNumberOuputs(err) => write!(f, "not enough outputs provided: {err}"),
            TxError::MissingPreviousTxs(err) => write!(f, " previous transactions not imported: {err}"),
            TxError::MissingFutureTxs(err) => write!(f, "future transactions not imported: {err}"),
            TxError::InvalidPrevTx(err) => write!(f, "invalid previous transaction provided: {err}"),
            TxError::InvalidFutureTx(err) => write!(f, "invalid futures transaction provided: {err}"),
            TxError::UnrecognizedScript(err) => write!(f, "unrecognized scriptPubKey: {err}"),
        
        }
    }
}

#[derive(Debug)]
pub enum HeuristicError {
    PreviousTxNotImported(String),
    FutureTxsNotImported(String),
    InconsistenInputsAddressesTypes(String),
}

impl fmt::Display for HeuristicError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            HeuristicError::PreviousTxNotImported(err) => write!(f, "previous transactions not imported: {err}"),
            HeuristicError::FutureTxsNotImported(err) => write!(f, "future transactions not imported: {err}"),
            HeuristicError::InconsistenInputsAddressesTypes(err) => write!(f, "many inputs addresses types: {err}"),
        }
    }
}


impl std::error::Error for TxError {}
impl std::error::Error for HeuristicError {}


// combined error that wraps both
#[derive(Debug)]
pub enum AppError {
    Tx(TxError),
    Heuristic(HeuristicError),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::Tx(err)        => write!(f, "transaction error: {err}"),
            AppError::Heuristic(err) => write!(f, "heuristic error: {err}"),
        }
    }
}

impl std::error::Error for AppError {}

// these allow ? to convert automatically
impl From<TxError> for AppError {
    fn from(err: TxError) -> Self {
        AppError::Tx(err)
    }
}

impl From<HeuristicError> for AppError {
    fn from(err: HeuristicError) -> Self {
        AppError::Heuristic(err)
    }
}
