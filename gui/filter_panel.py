from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.search_controller import FilterState


class FilterPanel(QFrame):
    load_requested = Signal()
    selection_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("filterPanel")
        self.setFrameShape(QFrame.StyledPanel)

        self.semester_combo = QComboBox()
        self.subject_combo = QComboBox()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Chapter wise", "Paper & Section wise", "All"])

        self.paper_combo = QComboBox()
        self.section_combo = QComboBox()
        self.chapter_list = QListWidget()
        self.chapter_list.setAlternatingRowColors(True)
        self.chapter_list.setSelectionMode(QListWidget.NoSelection)
        self.chapter_list.setMaximumHeight(220)

        self.load_button = QPushButton("Load Questions")

        self._build_ui()
        self._connect_signals()
        self._update_mode_visibility()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        layout.addWidget(QLabel("Semester"))
        layout.addWidget(self.semester_combo)

        layout.addWidget(QLabel("Subject"))
        layout.addWidget(self.subject_combo)

        layout.addWidget(QLabel("Filter Mode"))
        layout.addWidget(self.mode_combo)

        self.chapter_group = QGroupBox("Chapters")
        chapter_layout = QVBoxLayout(self.chapter_group)
        chapter_layout.setContentsMargins(10, 10, 10, 10)
        chapter_layout.addWidget(self.chapter_list)
        layout.addWidget(self.chapter_group)

        self.paper_group = QGroupBox("Paper Type")
        paper_layout = QVBoxLayout(self.paper_group)
        paper_layout.setContentsMargins(10, 10, 10, 10)
        paper_layout.addWidget(self.paper_combo)
        layout.addWidget(self.paper_group)

        self.section_group = QGroupBox("Section")
        section_layout = QVBoxLayout(self.section_group)
        section_layout.setContentsMargins(10, 10, 10, 10)
        section_layout.addWidget(self.section_combo)
        layout.addWidget(self.section_group)

        layout.addStretch(1)
        layout.addWidget(self.load_button)

    def _connect_signals(self) -> None:
        for combo in (
            self.semester_combo,
            self.subject_combo,
            self.paper_combo,
        ):
            combo.currentIndexChanged.connect(self.selection_changed.emit)

        self.mode_combo.currentIndexChanged.connect(self._update_mode_visibility)
        self.load_button.clicked.connect(self.load_requested.emit)

    def set_semesters(self, semesters: Iterable[int]) -> None:
        self._set_combo_items(self.semester_combo, [str(s) for s in semesters])

    def set_subjects(self, subjects: Iterable[str]) -> None:
        self._set_combo_items(self.subject_combo, list(subjects))

    def set_paper_types(self, paper_types: Iterable[str]) -> None:
        self._set_combo_items(self.paper_combo, list(paper_types))

    def set_sections(self, sections: Iterable[str]) -> None:
        self._set_combo_items(self.section_combo, list(sections))

    def set_chapters(self, chapters: Iterable[str]) -> None:
        self.chapter_list.blockSignals(True)
        self.chapter_list.clear()
        for chapter in chapters:
            item = QListWidgetItem(chapter)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.chapter_list.addItem(item)
        self.chapter_list.blockSignals(False)

    def current_state(self) -> FilterState:
        semester = self.semester_combo.currentText().strip()
        mode_text = self.mode_combo.currentText()
        filter_mode = {
            "Chapter wise": "chapter",
            "Paper & Section wise": "paper_section",
            "All": "all",
        }[mode_text]
        return FilterState(
            semester=int(semester) if semester else None,
            subject=self.subject_combo.currentText().strip(),
            filter_mode=filter_mode,
            chapters=tuple(self.selected_chapters()),
            paper_type=self.paper_combo.currentText().strip(),
            section=self.section_combo.currentText().strip(),
        )

    def selected_chapters(self) -> list[str]:
        chapters = []
        for i in range(self.chapter_list.count()):
            item = self.chapter_list.item(i)
            if item.checkState() == Qt.Checked:
                chapters.append(item.text())
        return chapters

    def _set_combo_items(self, combo: QComboBox, items: list[str]) -> None:
        current = combo.currentText()
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(items)
        if current in items:
            combo.setCurrentText(current)
        combo.blockSignals(False)

    def _update_mode_visibility(self) -> None:
        mode = self.mode_combo.currentText()
        self.chapter_group.setVisible(mode == "Chapter wise")
        self.paper_group.setVisible(mode == "Paper & Section wise")
        self.section_group.setVisible(mode == "Paper & Section wise")
