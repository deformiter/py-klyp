from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import QCoreApplication

from klyp.logger import Logger

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None, icon=None):
        super().__init__(icon, parent)
        self.logger = Logger().logger
        self.parent_app = parent
        self._create_context_menu()
        self.activated.connect(self._on_tray_icon_activated)

    def _create_context_menu(self):
        menu = QMenu()
        self.open_action = menu.addAction("Open Clipboard")
        self.open_action.triggered.connect(self.parent_app.show_clipboard_window)
        self.settings_action = menu.addAction("Settings")
        self.settings_action.triggered.connect(self.parent_app.show_settings_window)
        menu.addSeparator()
        self.quit_action = menu.addAction("Quit")
        self.quit_action.triggered.connect(QCoreApplication.quit)
        self.setContextMenu(menu)

    def _on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.parent_app.show_clipboard_window()
