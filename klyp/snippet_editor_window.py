from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
from klyp.logger import Logger
from klyp.hotkey_input import HotkeyInput

class SnippetEditorWindow(QDialog):
    def __init__(self, parent=None, snippet=None):
        super().__init__(parent)
        self.parent_app = parent
        self.snippet = snippet
        self.logger = Logger().logger
        self.setWindowTitle("KLYP - Snippet Editor")
        self.setMinimumWidth(400)
        self._setup_ui()
        self._load_snippet_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel("Label:"))
        self.label_input = QLineEdit()
        main_layout.addWidget(self.label_input)
        main_layout.addWidget(QLabel("Content:"))
        self.content_input = QTextEdit()
        main_layout.addWidget(self.content_input)
        main_layout.addWidget(QLabel("Tags (comma-separated):"))
        self.tags_input = QLineEdit()
        main_layout.addWidget(self.tags_input)
        main_layout.addWidget(QLabel("Group:"))
        self.group_input = QLineEdit()
        main_layout.addWidget(self.group_input)
        main_layout.addWidget(QLabel("Quick-Paste Hotkey:"))
        self.hotkey_input = HotkeyInput()
        main_layout.addWidget(self.hotkey_input)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_snippet)
        button_layout.addWidget(self.save_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

    def _load_snippet_data(self):
        if self.snippet:
            self.setWindowTitle("KLYP - Edit Snippet")
            self.label_input.setText(self.snippet.get('label', ''))
            self.content_input.setText(self.snippet.get('content', ''))
            self.tags_input.setText(self.snippet.get('tags', ''))
            self.group_input.setText(self.snippet.get('group_name', ''))
            self.hotkey_input.setText(self.snippet.get('hotkey') or '')
        else:
            self.setWindowTitle("KLYP - Add New Snippet")

    def _save_snippet(self):
        label = self.label_input.text().strip()
        content = self.content_input.toPlainText().strip()
        tags = self.tags_input.text().strip()
        group_name = self.group_input.text().strip()
        hotkey = self.hotkey_input.text().strip().lower() or None

        if not label or not content:
            QMessageBox.warning(self, "Input Error", "Label and Content cannot be empty.")
            return

        if self.snippet:
            success = self.parent_app.snippet_manager.update_snippet(
                self.snippet['id'], label, content, tags, group_name, hotkey
            )
            if success:
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update snippet.")
        else:
            snippet_id = self.parent_app.snippet_manager.add_snippet(
                label, content, tags, group_name, hotkey
            )
            if snippet_id != -1:
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to add snippet.")
