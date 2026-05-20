
fn main() {
    let script_hex = "41048f41cf5017db935e297a66b02796a1c377dc2eb790d61ea1dc4c9137a2fb1c9863032339d228ab424a5e4848673f176f58c8108673bc356cba69f68cb40629b5ac";
    let bytes = hex::decode(script_hex).unwrap();
    let script = bitcoin::Script::from(bytes);
    let bytes = script.as_bytes();
    
    println!("bytes len: {}", bytes.len());
    println!("last byte: {:x}", bytes.last().unwrap());
    
    let pubkey_bytes = if bytes.len() >= 2 {
        &bytes[1..bytes.len() - 1]
    } else {
        &[]
    };
    
    use bitcoin::hashes::{hash160, Hash};
    let hash = hash160::Hash::hash(pubkey_bytes);
    println!("hash: {:?}", hash);
}
