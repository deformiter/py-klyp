from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSpinBox

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle("KLYP - Settings")
        self.setMinimumWidth(400)

        main_layout = QVBoxLayout(self)

        history_limit_layout = QHBoxLayout()
        history_limit_layout.addWidget(QLabel("Clipboard History Limit:"))
        self.history_limit_spinbox = QSpinBox()
        self.history_limit_spinbox.setRange(1, 999)
        
        try:
            current_limit = int(self.parent_app.settings_manager.get_setting('history_limit'))
            self.history_limit_spinbox.setValue(current_limit)
        except (ValueError, TypeError):
            self.history_limit_spinbox.setValue(15)
            
        history_limit_layout.addWidget(self.history_limit_spinbox)
        history_limit_layout.addStretch()
        main_layout.addLayout(history_limit_layout)

        main_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self._save_settings)
        button_layout.addWidget(ok_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

    def _save_settings(self):
        new_limit = self.history_limit_spinbox.value()
        self.parent_app.settings_manager.set_setting('history_limit', str(new_limit))
        self.accept()
