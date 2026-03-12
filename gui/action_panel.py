from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout


class ActionPanel(QFrame):
    copy_selected_requested = Signal()
    copy_all_requested = Signal()
    export_txt_requested = Signal()
    export_json_requested = Signal()
    open_folder_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("actionPanel")
        self.setFrameShape(QFrame.StyledPanel)

        self.copy_selected_button = QPushButton("Copy Selected Question")
        self.copy_all_button = QPushButton("Copy All Filtered Questions")
        self.export_txt_button = QPushButton("Export Filtered Questions -> TXT")
        self.export_json_button = QPushButton("Export Filtered Questions -> JSON")
        self.open_folder_button = QPushButton("Open Dataset Folder")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(self.copy_selected_button)
        layout.addWidget(self.copy_all_button)
        layout.addWidget(self.export_txt_button)
        layout.addWidget(self.export_json_button)
        layout.addWidget(self.open_folder_button)
        layout.addStretch(1)

        self.copy_selected_button.clicked.connect(self.copy_selected_requested.emit)
        self.copy_all_button.clicked.connect(self.copy_all_requested.emit)
        self.export_txt_button.clicked.connect(self.export_txt_requested.emit)
        self.export_json_button.clicked.connect(self.export_json_requested.emit)
        self.open_folder_button.clicked.connect(self.open_folder_requested.emit)
