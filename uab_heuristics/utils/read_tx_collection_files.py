from pathlib import Path
import json

def get_collection_tx(filename, heuristics):
    path = Path(filename)
    with path.open("r") as f:
        data = json.load(f)
    
    txs_selected = []
    for heuristic in heuristics:
        for txs in data[heuristic]:
            txs_selected.append((txs["tx_id"], txs["tx_raw"]))
    return txs_selected