//! Heuristics on a transaction with an OP_RETURN output.
//!
//! The transaction is a Bitcoin Knots payment from the wallet fingerprinting
//! testbed: two P2PKH inputs (9,629,840 and 13,950,205 sats), output 0 is the
//! change (P2PKH, 1,775,988 sats), output 1 the payment (P2TR, 21,803,223
//! sats) and output 2 a 25-byte OP_RETURN. An OP_RETURN has no address, and
//! the heuristics that turn outputs into addresses used to fail on the whole
//! transaction; it is never the change, so it is now flagged false and the
//! other outputs are still judged.

use bitcoin::Network;

use crate::tx::Tx;
use crate::types::AppError;

use super::{AddressTypeChange, ConsistentAddressTypeChange, Heuristic, OptimalChange, PresentReusedAddressChange};

const TX: &str = "020000000216938316aefcab02376dc7eb65587ec058d6625ae185e36fba9d2fa9d233a061000000006a473044022043bd7dedff1e0221b088776b3b894775f057374b06bd12b7714bf5a4555ac7c4022048e68804092b6b3be15f78656fbf92d2acac066b8a28d4cd9ddeacb5aa8717cb012102b0abc134a9ae3406c974b7984faf6a0e531d7bcd1c0703ba3d915ea656af6c76fdffffffaa7f258ae7912a3698772d8de1552bce87b68b2f12eac52a75a5d1a8f58421fb010000006a473044022021b56e7d1c443c65c6798a6275adf91c11a2dd37680016c0295d30fbbbf22a4702201f2a13dd4e7110017ef8450ff5a565f472f97287e966a6017c12071f85f4baa00121022c98adc18c36ae2d867ad752036f550206416288a533417e4657b778c0aadc37fdffffff0374191b00000000001976a91488d87dc9d0bafc7f5b944c8abf5f017a2d12dd6a88acd7b04c010000000022512052c899d9db40e10f8a34ee9c9c7afaed31a94788599ac1f314e1cacce03a41cf00000000000000001b6a1957616c6c657446696e6765727072696e74696e675374756479ea120000";

const PREV_TXS: [&str; 2] = [
    "0200000001c275084f97b493720e2330f2658267dbe6c2ac497dc2299b58d020d915da8e4e010000006a47304402207587997cf66e8a691d0c93644155c8f62c9de5dc8b94db6615e564be991f3ddf022042c165c561df0be3739fe804ad343c863c8a129d20931dba039a6e8e56c57b750121023c6ad67beee7d0b9a41f6a95a57970bd77116e75f43db61df9b03cbed3d66750fdffffff0290f09200000000001976a914fa826ac214cd0fa53c0730b5b6047839f70bb8f988ac550901000000000022002051f35105c0e1fa037eef60a8678bc10ad4cc1c948644e0c29265153ed214b481e9120000",
    "0200000001c1f0396cb9ecf9076ddf81bb8fce6d3556929bbeeaf2b27159b2d92e7ce06ad0010000006a473044022030bc4ed6bc94758640a4062878a8ccb960bbd1b15405812589c028728ff16057022023d42543e0e50df61f19bfa0aa56e8cc772d9dbc09444ae34d1208bc4146e253012103a224c665e90bb27d53e160b4f0d3e0b42513a8265cb95fefba01237655c1bc4afdffffff02a45900000000000017a914008673c323e3c7ca0a3eb63054861edb820216eb87fddcd400000000001976a9148cf2812c8036c8114db22e671344f06ca2ace2dc88ac9b120000",
];

fn tx() -> Result<Tx, AppError> {
    let mut tx = Tx::from_raw(TX, Network::Bitcoin).map_err(AppError::Tx)?;
    let prev = PREV_TXS
        .iter()
        .map(|raw| Tx::from_raw(raw, Network::Bitcoin))
        .collect::<Result<Vec<Tx>, _>>()
        .map_err(AppError::Tx)?;
    tx.import_previous_txs(prev).map_err(AppError::Tx)?;
    Ok(tx)
}

#[test]
fn the_op_return_output_is_recognised() -> Result<(), AppError> {
    assert_eq!(tx()?.outputs_are_op_return(), vec![false, false, true]);
    Ok(())
}

#[test]
fn address_type_flags_the_change_and_not_the_op_return() -> Result<(), AppError> {
    assert_eq!(AddressTypeChange.apply(&tx()?)?, vec![true, false, false]);
    assert_eq!(ConsistentAddressTypeChange.apply(&tx()?)?, vec![true, false, false]);
    Ok(())
}

#[test]
fn present_reuse_does_not_fail_on_the_op_return() -> Result<(), AppError> {
    assert_eq!(PresentReusedAddressChange.apply(&tx()?)?, vec![false, false, false]);
    Ok(())
}

#[test]
fn optimal_change_counts_only_the_outputs_with_value() -> Result<(), AppError> {
    // Two value outputs and an OP_RETURN: applicable. The change is smaller
    // than every input, the payment is not.
    assert_eq!(OptimalChange.apply(&tx()?)?, vec![true, false, false]);
    Ok(())
}
