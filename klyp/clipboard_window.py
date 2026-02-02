from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QMenu, QMessageBox, QAbstractItemView, QLabel
from PySide6.QtCore import Qt, QCoreApplication, QPoint
from PySide6.QtGui import QKeyEvent, QAction

from klyp.hotkey_input import HotkeyInput

class SnippetListWidget(QListWidget):
    def __init__(self, parent_window: 'ClipboardWindow'):
        super().__init__(parent_window)
        self.clipboard_window = parent_window
        self.paste_manager = self.clipboard_window.paste_manager
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def _show_context_menu(self, pos: QPoint):
        selected_items = self.selectedItems()
        if not selected_items:
            return

        context_menu = QMenu(self)
        
        if len(selected_items) == 1:
            item = selected_items[0]
            edit_action = context_menu.addAction("Edit")
            edit_action.triggered.connect(lambda: self.clipboard_window._edit_snippet(item))
            
            snippet_data = item.data(Qt.ItemDataRole.UserRole)
            is_pinned = snippet_data.get('is_pinned', 0)
            pin_action_text = "Unpin" if is_pinned else "Pin"
            pin_action = context_menu.addAction(pin_action_text)
            pin_action.triggered.connect(lambda: self.clipboard_window._pin_snippet(item))
            context_menu.addSeparator()

        delete_action_text = f"Delete {len(selected_items)} Item(s)"
        delete_action = context_menu.addAction(delete_action_text)
        delete_action.triggered.connect(self.clipboard_window._delete_selected_snippets)
        
        context_menu.exec(self.mapToGlobal(pos))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_C and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            selected_items = self.selectedItems()
            if selected_items:
                item = selected_items[0]
                snippet_data = item.data(Qt.ItemDataRole.UserRole)
                if snippet_data and 'content' in snippet_data:
                    self.paste_manager.paste_text(snippet_data['content'])
                    event.accept()
                    return
        elif event.key() == Qt.Key.Key_Delete:
            self.clipboard_window._delete_selected_snippets()
            event.accept()
            return
        
        super().keyPressEvent(event)


class ClipboardWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.paste_manager = parent.paste_manager
        self.is_currently_visible = False
        self.setWindowTitle("KLYP - Clipboard")
        self.setGeometry(100, 100, 350, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.snippet_list_widget = SnippetListWidget(self)
        self.snippet_list_widget.itemActivated.connect(self._on_snippet_activated)
        main_layout.addWidget(self.snippet_list_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.add_button = QPushButton("Add New Snippet")
        self.add_button.clicked.connect(self.add_snippet)
        button_layout.addWidget(self.add_button)
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_button)
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.exit_app)
        button_layout.addWidget(self.exit_button)
        main_layout.addLayout(button_layout)

        version_layout = QHBoxLayout()
        version_layout.addStretch()
        version_label = QLabel("KLYP v0.01 developed by Alex Amos")
        version_label.setStyleSheet("font-size: 8pt; color: gray;")
        version_layout.addWidget(version_label)
        main_layout.addLayout(version_layout)

    def _on_snippet_activated(self, item):
        snippet_data = item.data(Qt.ItemDataRole.UserRole)
        if snippet_data and 'content' in snippet_data:
            self.paste_manager.paste_text(snippet_data['content'])

    def _edit_snippet(self, item):
        snippet_data = item.data(Qt.ItemDataRole.UserRole)
        if snippet_data:
            self.parent_app.show_snippet_editor(snippet_data)

    def _delete_selected_snippets(self):
        selected_items = self.snippet_list_widget.selectedItems()
        if not selected_items:
            return
        reply = QMessageBox.question(self, 'Delete Snippets', 
                                     f"Are you sure you want to delete {len(selected_items)} snippet(s)?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                snippet_data = item.data(Qt.ItemDataRole.UserRole)
                if snippet_data:
                    self.parent_app.snippet_manager.delete_snippet(snippet_data['id'])
            self.refresh_snippets(self.parent_app.snippet_manager.get_all_snippets())

    def _pin_snippet(self, item):
        snippet_data = item.data(Qt.ItemDataRole.UserRole)
        if not snippet_data: return
        new_status = not snippet_data.get('is_pinned', 0)
        if self.parent_app.snippet_manager.update_pin_status(snippet_data['id'], new_status):
            self.refresh_snippets(self.parent_app.snippet_manager.get_all_snippets())
        else:
            QMessageBox.critical(self, "Error", "Failed to update pin status.")

    def refresh_snippets(self, snippets: list):
        self.snippet_list_widget.clear()
        if not snippets:
            self.snippet_list_widget.addItem("No snippets found.")
            return
        for snippet in snippets:
            label = snippet['label']
            if snippet['is_pinned']:
                label = f"* {label}"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, dict(snippet))
            self.snippet_list_widget.addItem(item)

    def add_snippet(self):
        if self.parent_app:
            self.parent_app.show_snippet_editor()

    def open_settings(self):
        if self.parent_app:
            self.parent_app.show_settings_window()

    def exit_app(self):
        self.close()

    def closeEvent(self, event):
        self.hide()
        self.is_currently_visible = False
        event.ignore()