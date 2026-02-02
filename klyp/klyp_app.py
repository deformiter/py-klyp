import sys
import os
import functools
from PIL import Image, ImageDraw

from PySide6.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from klyp.logger import Logger
from klyp.database_manager import DatabaseManager
from klyp.system_tray import SystemTrayIcon
from klyp.clipboard_window import ClipboardWindow
from klyp.snippet_manager import SnippetManager
from klyp.hotkey_manager import HotkeyManager
from klyp.snippet_editor_window import SnippetEditorWindow
from klyp.paste_manager import PasteManager
from klyp.settings_manager import SettingsManager
from klyp.settings_window import SettingsWindow
from klyp.clipboard_monitor import ClipboardMonitor

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

ICON_PATH = resource_path("res/klyp_icon.png")

def create_placeholder_icon_if_needed(icon_path):
    if not os.path.exists(icon_path):
        # When running as a bundled exe, we can't create files this way.
        # The file should be included by PyInstaller's --add-data flag.
        # This function will now primarily be for dev mode.
        try:
            Logger().logger.info("Attempting to create placeholder icon for dev mode.")
            os.makedirs(os.path.dirname(icon_path), exist_ok=True)
            img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.text((16, 10), "K", fill="black")
            img.save(icon_path, "PNG")
        except Exception as e:
            # This error is expected in bundled mode, so we can log it as debug.
            Logger().logger.debug(f"Could not create placeholder icon (this is expected in EXE mode): {e}")

class KlypApp(QMainWindow):
    show_clipboard_signal = Signal()
    paste_signal = Signal(str) # New signal for thread-safe pasting

    def __init__(self):
        super().__init__()
        self.logger = Logger().logger
        self.db_manager = DatabaseManager()
        self.settings_manager = SettingsManager(self.db_manager)
        self.snippet_manager = SnippetManager(self.db_manager)
        self.hotkey_manager = HotkeyManager()
        self.clipboard_monitor = ClipboardMonitor(self)
        
        # Pass paste_signal to PasteManager
        self.paste_manager = PasteManager(None, self.clipboard_monitor)
        
        self.clipboard_window = ClipboardWindow(self)
        self.settings_window = SettingsWindow(self)
        
        self.paste_manager.app_window = self.clipboard_window
        
        create_placeholder_icon_if_needed(ICON_PATH)
        self.setWindowTitle("KLYP")
        
        icon = QIcon(ICON_PATH)
        if icon.isNull():
            self.logger.warning(f"Failed to load window icon from {ICON_PATH}.")
        self.setWindowIcon(icon)
        
        self.show_clipboard_signal.connect(self.show_clipboard_window)
        # Connect the new paste signal to its handler
        self.paste_signal.connect(self.paste_manager.paste_text)

        self.clipboard_monitor.new_clipboard_text.connect(self._handle_new_clipboard_text)
        
        self._add_test_snippets_if_empty()
        self._register_global_hotkeys()
        self.clipboard_monitor.start()
        
        self.logger.info("Initializing SystemTrayIcon...")
        try:
            self.tray_icon = SystemTrayIcon(self, icon)
            self.tray_icon.show()
        except Exception as e:
            self.logger.error(f"Failed to create or show SystemTrayIcon: {e}")
            self.show()
            return
            
        self.hide()
        self.logger.info("KlypApp initialized.")

    def _add_test_snippets_if_empty(self):
        try:
            if not self.snippet_manager.get_all_snippets():
                self.snippet_manager.add_snippet(
                    label="Sample Snippet",
                    content="This is a sample snippet.",
                    hotkey="ctrl+shift+1"
                )
        except Exception as e:
            self.logger.error(f"Failed to add sample snippets: {e}")

    def _register_global_hotkeys(self):
        self.hotkey_manager.unregister_all()
        main_hotkey = self.settings_manager.get_setting('main_hotkey')
        self.hotkey_manager.register_hotkey(main_hotkey, self._emit_show_clipboard_signal)
        try:
            for snippet in self.snippet_manager.get_all_snippets():
                if snippet['hotkey']:
                    # Hotkey callback now emits the paste_signal
                    callback = functools.partial(self.paste_signal.emit, snippet['content'])
                    self.hotkey_manager.register_hotkey(snippet['hotkey'], callback)
        except Exception as e:
            self.logger.error(f"Failed to register snippet hotkeys: {e}")

    def _emit_show_clipboard_signal(self):
        self.show_clipboard_signal.emit()

    def show_clipboard_window(self):
        if self.clipboard_window.is_currently_visible:
            self.clipboard_window.hide()
            self.clipboard_window.is_currently_visible = False
        else:
            try:
                self.clipboard_window.refresh_snippets(self.snippet_manager.get_all_snippets())
                self.clipboard_window.show()
                self.clipboard_window.is_currently_visible = True
                self.clipboard_window.activateWindow()
                self.clipboard_window.raise_()
            except Exception as e:
                self.logger.error(f"Failed to show clipboard window: {e}")

    def _handle_new_clipboard_text(self, text: str):
        if not text.strip(): return
        lines = text.strip().split('\n')
        label = lines[0]
        if len(label) > 50: label = label[:47] + "..."
        snippet_id = self.snippet_manager.add_snippet(label=label, content=text.strip())
        if snippet_id != -1:
            try:
                limit = int(self.settings_manager.get_setting('history_limit'))
                self.snippet_manager.enforce_history_limit(limit)
            except (ValueError, TypeError):
                self.snippet_manager.enforce_history_limit(15)
            if self.clipboard_window.is_currently_visible:
                self.clipboard_window.refresh_snippets(self.snippet_manager.get_all_snippets())

    def show_settings_window(self):
        self.hotkey_manager.unregister_all()
        self.settings_window.exec()
        self._register_global_hotkeys()
        
    def show_snippet_editor(self, snippet=None):
        self.hotkey_manager.unregister_all()
        editor = SnippetEditorWindow(self, snippet)
        if editor.exec() == SnippetEditorWindow.Accepted:
            self.clipboard_window.refresh_snippets(self.snippet_manager.get_all_snippets())
        self._register_global_hotkeys()

    def closeEvent(self, event):
        self.clipboard_monitor.stop()
        self.hotkey_manager.unregister_all()
        self.tray_icon.hide()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return -1
    app.setQuitOnLastWindowClosed(False)
    klyp_app = KlypApp()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
