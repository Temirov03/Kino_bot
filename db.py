import sqlite3


class DatabaseConf:
    def __init__(self, db_file="db.sqlite3"):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def set_db_tables(self):
        with self.connection:
            self.cursor.execute(
                "CREATE TABLE video_code ("
                "video_id TEXT,"
                "video_code TEXT,"
                "video_text TEXT)"
            )


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def check_video_code(self, video_code):
        with self.connection:
            result = self.cursor.execute(f"SELECT video_code FROM video_code WHERE video_code = (?)", (video_code,))
            result = result.fetchone()
            result = result[0] if result is not None else 0
            return result

    def get_video_by_code(self, video_code):
        with self.connection:
            result = self.cursor.execute(f"SELECT video_id, video_text FROM video_code WHERE video_code = (?)", (video_code,))
            result = result.fetchone()
            result = result if result is not None else 0
            return result

    def set_video_by_code(self, video_code, video_id, video_text):
        with self.connection:
            self.cursor.execute(f"INSERT INTO video_code (video_code, video_id, video_text) VALUES(?, ?, ?)",
                                (video_code, video_id, video_text))
