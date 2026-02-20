from typing import Dict, Set, Any
from normalizer import tokenize

AnswerObj = Dict[str, Any]

class InvertedIndex:
    ##token -> set(question_ids)
    def __init__(self) -> None:
        self.index: Dict[str, Set[int]] = {}

    def build(self, dataset: list[AnswerObj]) -> None:
        for obj in dataset:
            qid = int(obj["_id"])
            tokens = tokenize(obj.get("question", ""))

            # include keywords too
            keywords = obj.get("keywords") or []
            if isinstance(keywords, list):
                for kw in keywords:
                    if isinstance(kw, str):
                        tokens += tokenize(kw)

            for t in set(tokens):
                self.index.setdefault(t, set()).add(qid)

    def candidates(self, query_tokens: list[str]) -> Set[int]:
        out: Set[int] = set()
        for t in set(query_tokens):
            ids = self.index.get(t)
            if ids:
                out |= ids
        return out
