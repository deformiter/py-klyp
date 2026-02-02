from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from klyp.logger import Logger

class ClipboardMonitor(QObject):
    new_clipboard_text = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger().logger
        self.clipboard = QApplication.clipboard()
        self._last_text = self._get_clipboard_text()
        self.clipboard.dataChanged.connect(self.on_clipboard_changed)
        self.logger.info("Clipboard monitor connected to dataChanged signal.")

    def _get_clipboard_text(self) -> str:
        try:
            mime_data = self.clipboard.mimeData()
            if mime_data.hasText():
                return mime_data.text()
        except Exception as e:
            self.logger.warning(f"Could not read text from clipboard: {e}")
        return ""

    def on_clipboard_changed(self):
        current_text = self._get_clipboard_text()
        if not current_text:
            return
        if current_text != self._last_text:
            self.logger.info("New clipboard text detected via dataChanged signal.")
            self._last_text = current_text
            self.new_clipboard_text.emit(current_text)

    def update_last_text(self, text: str):
        self._last_text = text

    def start(self):
        pass

    def stop(self):
        try:
            self.clipboard.dataChanged.disconnect(self.on_clipboard_changed)
            self.logger.info("Clipboard monitor disconnected from dataChanged signal.")
        except RuntimeError:
            pass
