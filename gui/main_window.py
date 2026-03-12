from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QWidget,
    QHBoxLayout,
)

from gui.action_panel import ActionPanel
from gui.clipboard_service import ClipboardService
from gui.filter_panel import FilterPanel
from gui.question_list import QuestionListPanel
from gui.search_controller import FilterState, SearchController


class MainWindow(QMainWindow):
    def __init__(self, dataset_path: str | None = None) -> None:
        super().__init__()
        base_dir = Path(__file__).resolve().parents[1]
        self.controller = SearchController(dataset_path or (base_dir / "dataset.json"))
        self.current_state = FilterState()
        self.filtered_questions = []
        self.visible_questions = []

        self.filter_panel = FilterPanel()
        self.question_panel = QuestionListPanel()
        self.action_panel = ActionPanel()

        self.count_label = QLabel("Loaded Questions: 0")
        self.scope_label = QLabel("Scope: -")
        self.chapter_label = QLabel("Chapters: All")

        self._build_ui()
        self._connect_signals()
        self._apply_theme()
        self._populate_initial_filters()
        self._load_questions()

    def _build_ui(self) -> None:
        self.setWindowTitle("Smart Question Retrieval System")
        self.resize(1600, 900)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.filter_panel)
        splitter.addWidget(self.question_panel)
        splitter.addWidget(self.action_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([320, 880, 320])

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(splitter)
        self.setCentralWidget(central)

        status = QStatusBar()
        status.addWidget(self.count_label)
        status.addPermanentWidget(self.scope_label)
        status.addPermanentWidget(self.chapter_label)
        self.setStatusBar(status)

        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.question_panel.search_bar.setFocus)
        QShortcut(QKeySequence("Ctrl+C"), self, activated=self._copy_selected)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self._export_txt)

    def _connect_signals(self) -> None:
        self.filter_panel.selection_changed.connect(self._refresh_filter_options)
        self.filter_panel.load_requested.connect(self._load_questions)
        self.question_panel.search_button.clicked.connect(self._run_search)
        self.question_panel.show_all_button.clicked.connect(self._show_all_filtered)
        self.question_panel.search_bar.input.returnPressed.connect(self._run_search)

        self.action_panel.copy_selected_requested.connect(self._copy_selected)
        self.action_panel.copy_all_requested.connect(self._copy_all)
        self.action_panel.export_txt_requested.connect(self._export_txt)
        self.action_panel.export_json_requested.connect(self._export_json)
        self.action_panel.open_folder_requested.connect(self._open_dataset_folder)

    def _populate_initial_filters(self) -> None:
        self.filter_panel.set_semesters(self.controller.get_semesters())
        self._refresh_filter_options()

    def _refresh_filter_options(self) -> None:
        semester = self._selected_semester()
        subjects = self.controller.get_subjects(semester)
        self.filter_panel.set_subjects(subjects)

        subject = self.filter_panel.subject_combo.currentText().strip()
        self.filter_panel.set_chapters(self.controller.get_chapters(semester, subject))
        paper_types = self.controller.get_paper_types(semester, subject)
        self.filter_panel.set_paper_types(paper_types)

        paper_type = self.filter_panel.paper_combo.currentText().strip()
        self.filter_panel.set_sections(
            self.controller.get_sections(semester, subject, paper_type)
        )

    def _load_questions(self) -> None:
        self.current_state = self.filter_panel.current_state()
        self.filtered_questions = self.controller.filter_questions(self.current_state)
        self.visible_questions = list(self.filtered_questions)
        self.question_panel.set_questions(self.visible_questions)
        self.question_panel.search_bar.input.clear()
        self._update_status()

    def _run_search(self) -> None:
        query = self.question_panel.search_bar.text().strip()
        self.visible_questions = self.controller.search_questions(
            query=query,
            filtered_questions=self.filtered_questions,
        )
        self.question_panel.set_questions(self.visible_questions, query=query)
        self._update_status(search_query=query)

    def _show_all_filtered(self) -> None:
        self.visible_questions = list(self.filtered_questions)
        self.question_panel.set_questions(self.visible_questions)
        self._update_status()

    def _copy_selected(self) -> None:
        question = self.question_panel.selected_question()
        if question is None:
            self._show_info("No question selected.")
            return
        ClipboardService.copy_text(ClipboardService.format_question(question))
        self.statusBar().showMessage("Selected question copied to clipboard.", 3000)

    def _copy_all(self) -> None:
        if not self.filtered_questions:
            self._show_info("No filtered questions available.")
            return
        ClipboardService.copy_text(ClipboardService.format_bulk(self.filtered_questions))
        self.statusBar().showMessage("All filtered questions copied to clipboard.", 3000)

    def _export_txt(self) -> None:
        if not self.filtered_questions:
            self._show_info("No filtered questions available.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Filtered Questions to TXT",
            str(self.controller.dataset_folder / "filtered_questions.txt"),
            "Text Files (*.txt)",
        )
        if path:
            ClipboardService.export_txt(path, self.filtered_questions)
            self.statusBar().showMessage(f"Exported TXT to {path}", 4000)

    def _export_json(self) -> None:
        if not self.filtered_questions:
            self._show_info("No filtered questions available.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Filtered Questions to JSON",
            str(self.controller.dataset_folder / "filtered_questions.json"),
            "JSON Files (*.json)",
        )
        if path:
            ClipboardService.export_json(path, self.filtered_questions)
            self.statusBar().showMessage(f"Exported JSON to {path}", 4000)

    def _open_dataset_folder(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.controller.dataset_folder)))

    def _update_status(self, search_query: str = "") -> None:
        self.count_label.setText(
            f"Loaded Questions: {len(self.visible_questions)} / {len(self.filtered_questions)}"
        )

        scope_parts = [
            f"Semester {self.current_state.semester}" if self.current_state.semester else "Semester -",
            self.current_state.subject or "Subject -",
        ]
        if self.current_state.filter_mode == "paper_section":
            scope_parts.append(self.current_state.paper_type or "Paper -")
            scope_parts.append(
                f"Section {self.current_state.section}" if self.current_state.section else "Section -"
            )
        elif self.current_state.filter_mode == "chapter":
            scope_parts.append("Chapter wise")
        else:
            scope_parts.append("All")
        if search_query:
            scope_parts.append(f"Search: {search_query}")
        self.scope_label.setText("Scope: " + " | ".join(scope_parts))

        chapter_text = ", ".join(self.current_state.chapters) if self.current_state.chapters else "All"
        self.chapter_label.setText(f"Chapters: {chapter_text}")

    def _selected_semester(self) -> int | None:
        text = self.filter_panel.semester_combo.currentText().strip()
        return int(text) if text else None

    def _show_info(self, message: str) -> None:
        QMessageBox.information(self, "Smart Question Retrieval", message)

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background-color: #141821;
                color: #e8edf3;
                font-size: 13px;
            }
            QFrame#filterPanel, QFrame#questionListPanel, QFrame#actionPanel {
                background-color: #1b2230;
                border: 1px solid #293244;
                border-radius: 14px;
            }
            QFrame#questionCard {
                background-color: #20293a;
                border: 1px solid #33415c;
                border-radius: 12px;
            }
            QLabel#metaLabel {
                color: #9fb3c8;
            }
            QLabel#questionBody {
                color: #f4f7fb;
                line-height: 1.45;
            }
            QComboBox, QListWidget, QLineEdit {
                background-color: #0f1420;
                border: 1px solid #3a475f;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 2px;
            }
            QPushButton {
                background-color: #2d6cdf;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3a7aec;
            }
            QPushButton:pressed {
                background-color: #1f59c6;
            }
            QStatusBar {
                background-color: #111620;
                color: #c8d4e3;
            }
            QGroupBox {
                border: 1px solid #33415c;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            """
        )


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Smart Question Retrieval System")
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow(dataset_path=sys.argv[1] if len(sys.argv) > 1 else None)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
