import json, os

def save_neuro_unit(record, path="data/exports/neuro_unit.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    return path
