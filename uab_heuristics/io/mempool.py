import requests

template = "https://mempool.space/api/tx/{0}/hex"

def make_request(txid):
    url = template.format(txid)
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text()
