
def get_address_type(addr):
    if addr[0] == "1":
        return "p2pkh"
    elif addr[0] == "3":
        return "p2sh"
    elif addr[:4] == "bc1q" and len(addr) == 42:
        return "p2wpkh"
    elif addr[:4] == "bc1q" and len(addr) == 62:
        return "p2wsh"
    elif addr[:4] == "bc1p":
        return "p2tr"
    else:
        return None