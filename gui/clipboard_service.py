from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Sequence

from PySide6.QtGui import QGuiApplication

QObj = Dict[str, Any]


class ClipboardService:
    @staticmethod
    def _dataset_shape(question: QObj) -> QObj:
        return {k: v for k, v in question.items() if k != "_id"}

    @staticmethod
    def copy_text(text: str) -> None:
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)

    @staticmethod
    def format_question(question: QObj) -> str:
        chapters = ", ".join(question.get("chapter", [])) or "N/A"
        return (
            f"[Subject: {question.get('subject', 'N/A')}]\n"
            f"[Chapter: {chapters}]\n"
            f"[Marks: {question.get('mark', 'N/A')}]\n\n"
            f"Question: {question.get('question', '').strip()}"
        )

    @staticmethod
    def format_bulk(questions: Sequence[QObj]) -> str:
        lines = []
        for i, question in enumerate(questions, start=1):
            lines.append(f"Q{i}. {question.get('question', '').strip()}")
        return "\n\n".join(lines)

    @staticmethod
    def export_txt(path: str | Path, questions: Sequence[QObj]) -> None:
        output = []
        for i, question in enumerate(questions, start=1):
            chapters = ", ".join(question.get("chapter", [])) or "N/A"
            output.append(
                f"Q{i}\n"
                f"Subject: {question.get('subject', 'N/A')}\n"
                f"Chapter: {chapters}\n"
                f"Marks: {question.get('mark', 'N/A')}\n"
                f"Paper Type: {question.get('paper_type', 'N/A')}\n"
                f"Section: {question.get('section', 'N/A')}\n\n"
                f"{question.get('question', '').strip()}\n"
            )
        Path(path).write_text("\n" + ("\n" + ("-" * 72) + "\n").join(output), encoding="utf-8")

    @staticmethod
    def export_json(path: str | Path, questions: Iterable[QObj]) -> None:
        Path(path).write_text(
            json.dumps(
                [ClipboardService._dataset_shape(question) for question in questions],
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
