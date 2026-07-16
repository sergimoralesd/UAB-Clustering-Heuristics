use std::fmt::{self};
use serde::Deserialize;


#[derive(Debug)]
pub enum TestError {
    MissingTxid(String),
    MissingRawTx(String),
    MissingBlockHeight(String),
    MissingPreviousTxs(String),
    MissingFutureTxs(String),

}

impl fmt::Display for TestError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TestError::MissingTxid(err) => write!(f, "missing txid: {err}"),
            TestError::MissingRawTx(err) => write!(f, "missing raw tx: {err}"),
            TestError::MissingBlockHeight(err) => write!(f, "missing block height: {err}"),
            TestError::MissingPreviousTxs(err) => write!(f, "missing prev txs: {err}"),
            TestError::MissingFutureTxs(err) => write!(f, "missing future txs: {err}"),

        }
    }
}

#[derive(Debug)]
pub enum TxError {
    Hex(String),
    Decode(String),
    MismatchNumberInputs(String),
    MismatchNumberOutputs(String),
    MissingPreviousTxs(String),
    MissingFutureTxs(String),
    InvalidPrevTx(String),
    InvalidFutureTx(String),
    UnrecognizedScript(String),
    MalformedScript(String),
}

impl fmt::Display for TxError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TxError::Hex(err) => write!(f, "failed to decode the transaction hex: {err}"),
            TxError::Decode(err) => write!(f, "failed to deserialize the transaction: {err}"),
            TxError::MismatchNumberInputs(err) => write!(f, "not enough inputs provided: {err}"),
            TxError::MismatchNumberOutputs(err) => write!(f, "not enough outputs provided: {err}"),
            TxError::MissingPreviousTxs(err) => write!(f, " previous transactions not imported: {err}"),
            TxError::MissingFutureTxs(err) => write!(f, "future transactions not imported: {err}"),
            TxError::InvalidPrevTx(err) => write!(f, "invalid previous transaction provided: {err}"),
            TxError::InvalidFutureTx(err) => write!(f, "invalid futures transaction provided: {err}"),
            TxError::UnrecognizedScript(err) => write!(f, "unrecognized scriptPubKey: {err}"),
            TxError::MalformedScript(err) => write!(f, "malformed scriptSig: {err}"),
        }
    }
}

#[derive(Debug)]
pub enum HeuristicError {
    PreviousTxNotImported(String),
    FutureTxsNotImported(String),
    ReplacementNotImported(String),
    InconsistentInputsAddressesTypes(String),
    BlockHeightNotImported(String),
    NotApplicable(String),
}

impl fmt::Display for HeuristicError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            HeuristicError::PreviousTxNotImported(err) => write!(f, "previous transactions not imported: {err}"),
            HeuristicError::FutureTxsNotImported(err) => write!(f, "future transactions not imported: {err}"),
            HeuristicError::InconsistentInputsAddressesTypes(err) => write!(f, "many inputs addresses types: {err}"),
            HeuristicError::BlockHeightNotImported(err) => write!(f, "block height not imported: {err}"),
            HeuristicError::NotApplicable(err) => write!(f, "the transaction does not meet the requirements for the 
            heuristic: {err}"),
            HeuristicError::ReplacementNotImported(err) => write!(f, "missing replacement transaction: {err}"),

        }
    }
}
#[derive(Debug)]
pub enum ApiError {
    UnableToFetch(String),
}

impl fmt::Display for ApiError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ApiError::UnableToFetch(err) => write!(f ,"unable to fetch: {err}"), 
        }
    }
}

impl std::error::Error for TxError {}
impl std::error::Error for HeuristicError {}
impl std::error::Error for ApiError {}
impl std::error::Error for TestError {}


// combined error that wraps both
#[derive(Debug)]
pub enum AppError {
    Tx(TxError),
    Heuristic(HeuristicError),
    Api(ApiError),
    Test(TestError),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::Tx(err) => write!(f, "transaction error: {err}"),
            AppError::Heuristic(err) => write!(f, "heuristic error: {err}"),
            AppError::Api(err) => write!(f, "api error: {err}"),
            AppError::Test(err) => write!(f, "test error: {err}")
        }
    }
}

impl std::error::Error for AppError {}


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

impl From<ApiError> for AppError {
    fn from(err: ApiError) -> Self {
        AppError::Api(err)
    }
}


pub enum InputDataRequirements {
    None,
    Low,
    MediumLow,
    Medium,
    MediumHigh,
    HighIndexed,
    HighNonIndexed
}

impl InputDataRequirements {
    pub fn value(&self) -> u8 {
        match self {
            InputDataRequirements::None => 0,
            InputDataRequirements::Low => 1,
            InputDataRequirements::MediumLow => 2,
            InputDataRequirements::Medium => 3,
            InputDataRequirements::MediumHigh => 4,
            InputDataRequirements::HighIndexed => 5,
            InputDataRequirements::HighNonIndexed => 6,
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct JsonTx {
    pub txid: String,
    pub version: i32,
    pub locktime: u32,
    pub vin: Vec<JsonInput>,
    pub vout: Vec<JsonOutput>,
}

#[derive(Debug, Deserialize)]
pub struct JsonInput {
    pub txid: String,
    pub vout: u32,
    pub scriptsig: String,
    pub sequence: u32,
    #[serde(default)] 
    pub witness: Option<Vec<String>>,  // ← hex encoded witness items
}

#[derive(Debug, Deserialize)]
pub struct JsonOutput {
    pub value: u64,
    pub scriptpubkey: String,  // ← hex encoded
}