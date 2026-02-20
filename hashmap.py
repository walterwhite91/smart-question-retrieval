from typing import Dict, Optional, Any
from normalizer import normalize

AnswerObj = Dict[str, Any]

class ExactMatchIndex:
    """
    HashMap index:
      key   = normalized question
      value = answer object
    """
    def __init__(self) -> None:
        self.map: Dict[str, AnswerObj] = {}

    def build(self, dataset: list[AnswerObj]) -> None:
        for obj in dataset:
            q = obj.get("question", "")
            nq = normalize(q)
            if nq:  # skip empty
                # if duplicates exist, keep the first one (arbitrary choice)
                self.map.setdefault(nq, obj)

    def get(self, user_question: str) -> Optional[AnswerObj]:
        return self.map.get(normalize(user_question))
