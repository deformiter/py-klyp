import time
from pynput.keyboard import Key, Controller
from PySide6.QtWidgets import QApplication
from klyp.logger import Logger

class PasteManager:
    def __init__(self, app_window=None, clipboard_monitor=None):
        self.logger = Logger().logger
        self.app_window = app_window
        self.keyboard = Controller()
        self.clipboard_monitor = clipboard_monitor

    def paste_text(self, text: str):
        try:
            if self.app_window and self.app_window.is_currently_visible:
                self.app_window.hide()
                self.app_window.is_currently_visible = False

            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            if self.clipboard_monitor:
                self.clipboard_monitor.update_last_text(text)
            
            time.sleep(0.1)

            with self.keyboard.pressed(Key.ctrl):
                self.keyboard.press('v')
                self.keyboard.release('v')
            self.logger.info("Simulated paste command (Ctrl+V).")

        except Exception as e:
            self.logger.error(f"Failed to copy or paste text: {e}")