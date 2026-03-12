from __future__ import annotations

import html
import re
from typing import Any, Dict, Iterable, List

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from normalizer import tokenize

QObj = Dict[str, Any]


class QuestionCard(QFrame):
    def __init__(self, question: QObj, query: str = "") -> None:
        super().__init__()
        self.setObjectName("questionCard")
        self.setFrameShape(QFrame.StyledPanel)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(10)

        meta = QLabel(self._meta_text(question))
        meta.setObjectName("metaLabel")
        meta.setTextFormat(Qt.RichText)
        meta.setWordWrap(True)
        outer.addWidget(meta)

        body = QLabel(self._highlight_text(question.get("question", ""), query))
        body.setWordWrap(True)
        body.setTextFormat(Qt.RichText)
        body.setTextInteractionFlags(Qt.TextSelectableByMouse)
        body_font = QFont("DejaVu Sans Mono", 11)
        body.setFont(body_font)
        body.setObjectName("questionBody")
        outer.addWidget(body)

    @staticmethod
    def _meta_text(question: QObj) -> str:
        chapters = ", ".join(question.get("chapter", [])) or "N/A"
        return (
            f"<b>Marks:</b> {html.escape(str(question.get('mark', 'N/A')))}"
            f" &nbsp;&nbsp; <b>Paper:</b> {html.escape(str(question.get('paper_type', 'N/A')))}"
            f" &nbsp;&nbsp; <b>Section:</b> {html.escape(str(question.get('section', 'N/A')))}"
            f"<br><b>Chapter:</b> {html.escape(chapters)}"
        )

    @staticmethod
    def _highlight_text(text: str, query: str) -> str:
        escaped = html.escape(text)
        tokens = sorted(set(tokenize(query)), key=len, reverse=True)
        if not tokens:
            return escaped.replace("\n", "<br>")

        pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in tokens) + r")\b", re.IGNORECASE)
        highlighted = pattern.sub(
            r"<span style='background-color:#f4c95d;color:#111111;border-radius:3px;'>\1</span>",
            escaped,
        )
        return highlighted.replace("\n", "<br>")


class QuestionListPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("questionListPanel")
        self.setFrameShape(QFrame.StyledPanel)

        self.search_input = QLabel()
        self.search_bar = _SearchBar()
        self.search_button = QPushButton("Search")
        self.show_all_button = QPushButton("Show All Filtered Questions")
        self.list_widget = QListWidget()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        controls.addWidget(self.search_bar, 1)
        controls.addWidget(self.search_button)
        controls.addWidget(self.show_all_button)
        layout.addLayout(controls)

        self.list_widget.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.list_widget.setSpacing(10)
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.list_widget, 1)

    def set_questions(self, questions: Iterable[QObj], query: str = "") -> None:
        self.list_widget.clear()
        for question in questions:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, question)
            card = QuestionCard(question, query=query)
            item.setSizeHint(card.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, card)

        if self.list_widget.count():
            self.list_widget.setCurrentRow(0)

    def selected_question(self) -> QObj | None:
        item = self.list_widget.currentItem()
        if item is None:
            return None
        return item.data(Qt.UserRole)


class _SearchBar(QWidget):
    def __init__(self) -> None:
        super().__init__()
        from PySide6.QtWidgets import QLineEdit, QVBoxLayout

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a question to find similar")
        self.input.setClearButtonEnabled(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.input)

    def text(self) -> str:
        return self.input.text()

    def setFocus(self) -> None:  # type: ignore[override]
        self.input.setFocus()
