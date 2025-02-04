import aiosqlite
import os
from typing import List, Dict, Any


class MessageDatabase:
    def __init__(self, db_path: str = "db/messages.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """ 
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    author_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            await db.commit()

    async def add_message(
        self, channel_id: int, message_id: int, author_id: int, content: str
    ):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO messages (channel_id, message_id, author_id, content) VALUES (?, ?, ?, ?)",
                (channel_id, message_id, author_id, content),
            )
            await db.commit()

            # Keep only last 150 messages per channel
            await db.execute(
                """
                DELETE FROM messages 
                WHERE channel_id = ? 
                AND id NOT IN (
                    SELECT id FROM messages 
                    WHERE channel_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 150
                )
            """,
                (channel_id, channel_id),
            )
            await db.commit()

    async def get_channel_history(
        self, channel_id: int, limit: int = 150
    ) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM messages 
                WHERE channel_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
                """,
                (channel_id, limit),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
