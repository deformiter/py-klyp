import keyboard
from klyp.logger import Logger

class HotkeyManager:
    def __init__(self):
        self.logger = Logger().logger
        
    def register_hotkey(self, hotkey_str: str, callback):
        try:
            keyboard.add_hotkey(hotkey_str, callback, suppress=False)
            self.logger.info(f"Successfully registered hotkey: {hotkey_str}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register hotkey '{hotkey_str}'. Error: {e}")
            return False

    def unregister_all(self):
        try:
            keyboard.remove_all_hotkeys()
            self.logger.info("All hotkeys have been unregistered.")
        except Exception as e:
            self.logger.debug(f"A non-fatal error occurred while unregistering hotkeys: {e}")