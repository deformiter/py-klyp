import sqlite3
from klyp.database_manager import DatabaseManager
from klyp.logger import Logger

class SnippetManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = Logger().logger

    def add_snippet(self, label: str, content: str, tags: str = "", group_name: str = "", hotkey: str = None) -> int:
        try:
            hotkey = hotkey if hotkey else None
            query = "INSERT INTO snippets (label, content, tags, group_name, hotkey) VALUES (?, ?, ?, ?, ?)"
            cursor = self.db_manager.execute_query(query, (label, content, tags, group_name, hotkey))
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            self.logger.error(f"Error adding snippet '{label}': {e}")
            return -1
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while adding snippet '{label}': {e}")
            return -1

    def get_all_snippets(self) -> list:
        try:
            query = "SELECT * FROM snippets ORDER BY is_pinned DESC, created_at DESC"
            snippets = self.db_manager.fetch_all(query)
            return snippets if snippets else []
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while fetching all snippets: {e}")
            return []

    def update_snippet(self, snippet_id: int, label: str, content: str, tags: str, group_name: str, hotkey: str = None) -> bool:
        try:
            hotkey = hotkey if hotkey else None
            query = "UPDATE snippets SET label = ?, content = ?, tags = ?, group_name = ?, hotkey = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            self.db_manager.execute_query(query, (label, content, tags, group_name, hotkey, snippet_id))
            return True
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while updating snippet ID {snippet_id}: {e}")
            return False

    def delete_snippet(self, snippet_id: int) -> bool:
        try:
            query = "DELETE FROM snippets WHERE id = ?"
            self.db_manager.execute_query(query, (snippet_id,))
            return True
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while deleting snippet ID {snippet_id}: {e}")
            return False

    def update_pin_status(self, snippet_id: int, is_pinned: bool) -> bool:
        try:
            query = "UPDATE snippets SET is_pinned = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            self.db_manager.execute_query(query, (int(is_pinned), snippet_id))
            return True
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while updating pin status for snippet ID {snippet_id}: {e}")
            return False

    def enforce_history_limit(self, limit: int):
        try:
            query = "SELECT id FROM snippets WHERE is_pinned = 0 AND (hotkey IS NULL OR hotkey = '') ORDER BY created_at ASC"
            results = self.db_manager.fetch_all(query)
            
            if not results or len(results) <= limit:
                return

            num_to_delete = len(results) - limit
            ids_to_delete = [row['id'] for row in results[:num_to_delete]]

            if ids_to_delete:
                self.logger.info(f"History limit ({limit}) exceeded. Deleting {num_to_delete} oldest unpinned snippet(s).")
                placeholders = ', '.join('?' for _ in ids_to_delete)
                delete_query = f"DELETE FROM snippets WHERE id IN ({placeholders})"
                self.db_manager.execute_query(delete_query, ids_to_delete)
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while enforcing history limit: {e}")
