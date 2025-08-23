import logging
import sqlite3
import os

logger = logging.getLogger(__name__)
# Use environment variable for DB path, with fallback to local path
DB_PATH = os.environ.get("DB_PATH", "state.db")


class StateDB:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.create_table()
        logger.info(f"StateDB initialized with database at {db_path}")

    def create_table(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS announced_first_bloods (
                    challenge_id INTEGER PRIMARY KEY
                )
            """
            )
        logger.debug("Database table created/verified")

    def is_announced(self, challenge_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM announced_first_bloods WHERE challenge_id=?", (challenge_id,)
        )
        result = cur.fetchone() is not None
        logger.debug(f"Challenge {challenge_id} announced status: {result}")
        return result

    def mark_announced(self, challenge_id):
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO announced_first_bloods (challenge_id) VALUES (?)",
                (challenge_id,),
            )
        logger.debug(f"Marked challenge {challenge_id} as announced")
