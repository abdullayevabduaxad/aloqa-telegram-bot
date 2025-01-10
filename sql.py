import aiosqlite

async def init_db():
    async with aiosqlite.connect("database.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            message TEXT NOT NULL
        )
        """)
        await db.commit()

async def save_message(user_id, username, message):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("INSERT INTO messages (user_id, username, message) VALUES (?, ?, ?)",
                         (user_id, username, message))
        await db.commit()

async def get_user_id_from_username(username):
    async with aiosqlite.connect("database.db") as db:
        cursor = await db.execute("SELECT user_id FROM messages WHERE username = ?", (username,))
        row = await cursor.fetchone()
        return row[0] if row else None