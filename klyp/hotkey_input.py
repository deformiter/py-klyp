from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt

class HotkeyInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Click here and press a key combination")

    def keyPressEvent(self, event: QKeyEvent):
        event.accept()
        key = event.key()

        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return

        if key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            self.clear()
            return
            
        modifiers = event.modifiers()
        mod_str = ""

        if modifiers & Qt.KeyboardModifier.ControlModifier:
            mod_str += "ctrl+"
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            mod_str += "shift+"
        if modifiers & Qt.KeyboardModifier.AltModifier:
            mod_str += "alt+"
        
        key_str = Qt.Key(key).name.lower()
        if key_str.startswith("key_"):
            key_str = key_str[4:]
            
        self.setText(mod_str + key_str)