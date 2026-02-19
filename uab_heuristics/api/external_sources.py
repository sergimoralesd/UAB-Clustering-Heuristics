import requests

templates = ["https://mempool.space/api/tx/{0}/hex", "https://blockchain.info/rawtx/{0}?format=hex"]


def make_request(txid):
    for template in templates:
        url = template.format(txid)
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()

            hex_tx = r.text.strip()
            if not hex_tx:
                raise ValueError(f"Empty response from {url}")

            return hex_tx  # success, return immediately

        except Exception as e:
            # Save last error, continue to next template
            last_error = e
            print(f"Warning: failed to fetch from {url}.")

    # If we get here, all templates failed
    raise RuntimeError(f"All requests failed for txid {txid}.")


