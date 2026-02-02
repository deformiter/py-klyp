from klyp.database_manager import DatabaseManager
from klyp.logger import Logger

class SettingsManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = Logger().logger
        self.defaults = {
            'main_hotkey': 'ctrl+shift+`',
            'history_limit': '15' # Added this line
        }

    def get_setting(self, key: str) -> str:
        """
        Retrieves a setting from the database.
        Returns the default value if the key is not found.
        """
        try:
            query = "SELECT value FROM settings WHERE key = ?"
            result = self.db_manager.fetch_one(query, (key,))
            if result:
                return result['value']
            else:
                default_value = self.defaults.get(key)
                if default_value is not None:
                    self.set_setting(key, default_value)
                    return default_value
                return ""
        except Exception as e:
            self.logger.error(f"Error getting setting '{key}': {e}")
            return self.defaults.get(key, "")

    def set_setting(self, key: str, value: str):
        """
        Saves a setting to the database (inserts or updates).
        """
        try:
            query = """
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """
            self.db_manager.execute_query(query, (key, value))
            self.logger.info(f"Successfully set setting: {key} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting setting '{key}': {e}")
            return False
