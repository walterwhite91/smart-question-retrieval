import json
from typing import Any, Dict, List, Tuple

AnswerObj = Dict[str, Any]

def load_dataset(path: str) -> List[AnswerObj]:
    """
    Supports:
    - .json  => list of objects OR single object
    - .jsonl => one object per line
    Adds: _id (int)
    """
    if path.endswith(".jsonl"):
        rows: List[AnswerObj] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
    elif path.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            rows = data
        else:
            rows = [data]
    else:
        raise ValueError("Dataset must be .json or .jsonl")

    # Assign internal IDs
    for i, obj in enumerate(rows):
        obj["_id"] = i

    return rows
