import re
from typing import List

_PUNCT_RE = re.compile(r"[^a-z0-9\s]")

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = _PUNCT_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text: str) -> List[str]:
    n = normalize(text)
    if not n:
        return []
    return n.split()
