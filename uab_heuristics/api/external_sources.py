import requests

def make_request(params, templates):
    if not isinstance(params, tuple):
        params = (params,)
    for template in templates:
        url = template.format(*params)
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()

            res = r.text.strip()
            if not res:
                raise ValueError(f"Empty response from {url}")

            return res  # success, return immediately

        except Exception as e:
            # Save last error, continue to next template
            last_error = e
            print(f"Warning: failed to fetch from {url}.")

    # If we get here, all templates failed
    raise RuntimeError(f"All requests failed.")


