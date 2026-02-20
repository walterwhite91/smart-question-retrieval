# matcher.py
from typing import Any, Dict, List
from normalizer import tokenize
from hashmap import ExactMatchIndex
from inverted_index import InvertedIndex

QObj = Dict[str, Any]

def _token_overlap_score(q_tokens: set[str], cand_tokens: set[str]) -> float:
    if not q_tokens:
        return 0.0
    return len(q_tokens & cand_tokens) / len(q_tokens)

class QuestionSearcher:
    def __init__(self, dataset: List[QObj]) -> None:
        self.dataset = dataset
        self.by_id = {int(o["_id"]): o for o in dataset}

        self.exact = ExactMatchIndex()
        self.exact.build(dataset)

        self.inv = InvertedIndex()
        self.inv.build(dataset)

        self.q_tokens = {
            int(o["_id"]): set(tokenize(o.get("question", "")))
            for o in dataset
        }

    def find_similar_questions(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.4
    ) -> Dict[str, Any]:

        # Exact match
        exact = self.exact.get(query)
        if exact:
            return {
                "matched": True,
                "match_type": "exact",
                "results": [{
                    "id": exact["_id"],
                    "question": exact["question"],
                    "score": 1.0,
                    "subject": exact.get("subject"),
                    "semester": exact.get("semester"),
                    "mark": exact.get("mark"),
                    "paper_type": exact.get("paper_type"),
                    "section": exact.get("section"),
                    "family": exact.get("family")
                }]
            }

        # Similar match
        q_tokens = set(tokenize(query))
        candidate_ids = self.inv.candidates(list(q_tokens))

        scored = []
        for cid in candidate_ids:
            score = _token_overlap_score(q_tokens, self.q_tokens[cid])
            if score >= threshold:
                obj = self.by_id[cid]
                scored.append({
                    "id": cid,
                    "question": obj["question"],
                    "score": round(score, 4),
                    "subject": obj.get("subject"),
                    "semester": obj.get("semester"),
                    "mark": obj.get("mark"),
                    "paper_type": obj.get("paper_type"),
                    "section": obj.get("section"),
                    "family": obj.get("family")
                })

        scored.sort(key=lambda x: x["score"], reverse=True)

        if not scored:
            return {"matched": False, "reason": "No similar questions found"}

        return {
            "matched": True,
            "match_type": "similar",
            "results": scored[:top_k]
        }