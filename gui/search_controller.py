from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from loader import load_dataset
from matcher import QuestionSearcher

QObj = Dict[str, Any]


@dataclass(frozen=True)
class FilterState:
    semester: int | None = None
    subject: str = ""
    filter_mode: str = "all"
    chapters: tuple[str, ...] = field(default_factory=tuple)
    paper_type: str = ""
    section: str = ""


class SearchController:
    """Keeps dataset access and filtering independent from the GUI widgets."""

    def __init__(self, dataset_path: str | Path) -> None:
        self.dataset_path = Path(dataset_path).resolve()
        self.dataset: List[QObj] = load_dataset(str(self.dataset_path))
        self._searchers: dict[tuple[int, ...], QuestionSearcher] = {}

    @property
    def dataset_folder(self) -> Path:
        return self.dataset_path.parent

    def get_semesters(self) -> list[int]:
        return sorted({int(q["semester"]) for q in self.dataset if "semester" in q})

    def get_subjects(self, semester: int | None) -> list[str]:
        rows = self._by_semester(semester)
        return sorted({str(q["subject"]) for q in rows if "subject" in q})

    def get_paper_types(self, semester: int | None, subject: str) -> list[str]:
        rows = self._by_subject(self._by_semester(semester), subject)
        return sorted({str(q["paper_type"]) for q in rows if "paper_type" in q})

    def get_sections(
        self,
        semester: int | None,
        subject: str,
        paper_type: str = "",
    ) -> list[str]:
        rows = self._by_subject(self._by_semester(semester), subject)
        if paper_type:
            rows = [q for q in rows if q.get("paper_type") == paper_type]
        return sorted({str(q["section"]) for q in rows if "section" in q})

    def get_chapters(self, semester: int | None, subject: str) -> list[str]:
        rows = self._by_subject(self._by_semester(semester), subject)
        chapters = {
            chapter
            for q in rows
            for chapter in q.get("chapter", [])
            if isinstance(chapter, str)
        }
        return sorted(chapters)

    def filter_questions(self, state: FilterState) -> list[QObj]:
        rows = self._by_subject(self._by_semester(state.semester), state.subject)

        if state.filter_mode == "chapter" and state.chapters:
            selected = set(state.chapters)
            rows = [
                q for q in rows
                if selected.intersection(q.get("chapter", []))
            ]
        elif state.filter_mode == "paper_section":
            if state.paper_type:
                rows = [q for q in rows if q.get("paper_type") == state.paper_type]
            if state.section:
                rows = [q for q in rows if q.get("section") == state.section]

        return list(rows)

    def search_questions(
        self,
        query: str,
        filtered_questions: Sequence[QObj],
        top_k: int = 20,
        threshold: float = 0.2,
    ) -> list[QObj]:
        if not query.strip():
            return list(filtered_questions)

        searcher = self._searcher_for(filtered_questions)
        result = searcher.find_similar_questions(
            query=query,
            top_k=top_k,
            threshold=threshold,
        )
        if not result.get("matched"):
            return []

        by_id = {int(q["_id"]): q for q in filtered_questions}
        return [
            by_id[item["id"]]
            for item in result.get("results", [])
            if item["id"] in by_id
        ]

    def _searcher_for(self, filtered_questions: Sequence[QObj]) -> QuestionSearcher:
        key = tuple(sorted(int(q["_id"]) for q in filtered_questions))
        if key not in self._searchers:
            self._searchers[key] = QuestionSearcher(list(filtered_questions))
        return self._searchers[key]

    def _by_semester(self, semester: int | None) -> Iterable[QObj]:
        if semester is None:
            return self.dataset
        return [q for q in self.dataset if q.get("semester") == semester]

    @staticmethod
    def _by_subject(rows: Iterable[QObj], subject: str) -> list[QObj]:
        if not subject:
            return list(rows)
        return [q for q in rows if q.get("subject") == subject]
