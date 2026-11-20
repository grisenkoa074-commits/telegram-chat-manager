import aiosqlite
from datetime import datetime, timedelta


class Database:
    def __init__(self, path):
        self.path = path
        self.db = None

    async def connect(self):
        self.db = await aiosqlite.connect(self.path)
        self.db.row_factory = aiosqlite.Row

        await self.db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            rank INTEGER DEFAULT 0,
            PRIMARY KEY(chat_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS settings (
            chat_id INTEGER,
            key TEXT,
            value TEXT,
            PRIMARY KEY(chat_id, key)
        );

        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            by_id INTEGER,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS rules (
            chat_id INTEGER PRIMARY KEY,
            text TEXT
        );

        CREATE TABLE IF NOT EXISTS accepted_rules (
            chat_id INTEGER,
            user_id INTEGER,
            PRIMARY KEY(chat_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        await self.db.commit()

    async def close(self):
        if self.db:
            await self.db.close()

    async def save_user(self, chat_id, user):
        await self.db.execute("""
        INSERT INTO users(chat_id,user_id,username,first_name)
        VALUES(?,?,?,?)
        ON CONFLICT(chat_id,user_id) DO UPDATE SET
        username=excluded.username,
        first_name=excluded.first_name
        """, (chat_id, user.id, user.username, user.first_name))
        await self.db.commit()

    async def record_activity(self, chat_id, user_id):
        await self.db.execute(
            "INSERT INTO activity(chat_id,user_id) VALUES(?,?)",
            (chat_id, user_id)
        )
        await self.db.commit()

    async def get_activity(self, chat_id, user_id, days=7):
        since = (datetime.utcnow() - timedelta(days=days-1)).strftime(
            "%Y-%m-%d 00:00:00"
        )
        cur = await self.db.execute("""
        SELECT DATE(created_at) AS day, COUNT(*) AS total
        FROM activity
        WHERE chat_id=? AND user_id=? AND created_at>=?
        GROUP BY DATE(created_at)
        ORDER BY day
        """, (chat_id, user_id, since))
        rows = await cur.fetchall()

        result = {}
        for i in range(days):
            day = (datetime.utcnow().date() -
                   timedelta(days=days-1-i)).isoformat()
            result[day] = 0

        for row in rows:
            result[row["day"]] = row["total"]

        return result

    async def get_total_activity(self, chat_id, user_id):
        cur = await self.db.execute(
            "SELECT COUNT(*) AS n FROM activity WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        )
        return (await cur.fetchone())["n"]

    async def get_rank(self, chat_id, user_id):
        cur = await self.db.execute(
            "SELECT rank FROM users WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        )
        row = await cur.fetchone()
        return int(row["rank"]) if row else 0

    async def set_rank(self, chat_id, user_id, rank):
        await self.db.execute("""
        INSERT INTO users(chat_id,user_id,rank)
        VALUES(?,?,?)
        ON CONFLICT(chat_id,user_id) DO UPDATE SET rank=excluded.rank
        """, (chat_id, user_id, rank))
        await self.db.commit()

    async def setting(self, chat_id, key, default="off"):
        cur = await self.db.execute(
            "SELECT value FROM settings WHERE chat_id=? AND key=?",
            (chat_id, key)
        )
        row = await cur.fetchone()
        return row["value"] if row else default

    async def set_setting(self, chat_id, key, value):
        await self.db.execute("""
        INSERT INTO settings(chat_id,key,value)
        VALUES(?,?,?)
        ON CONFLICT(chat_id,key) DO UPDATE SET value=excluded.value
        """, (chat_id, key, value))
        await self.db.commit()

    async def set_rules(self, chat_id, text):
        await self.db.execute("""
        INSERT INTO rules(chat_id,text) VALUES(?,?)
        ON CONFLICT(chat_id) DO UPDATE SET text=excluded.text
        """, (chat_id, text))
        await self.db.commit()

    async def get_rules(self, chat_id):
        cur = await self.db.execute(
            "SELECT text FROM rules WHERE chat_id=?", (chat_id,)
        )
        row = await cur.fetchone()
        return row["text"] if row else "Правила пока не установлены."

    async def add_warning(self, chat_id, user_id, by_id, reason):
        await self.db.execute("""
        INSERT INTO warnings(chat_id,user_id,by_id,reason)
        VALUES(?,?,?,?)
        """, (chat_id, user_id, by_id, reason))
        await self.db.commit()

        cur = await self.db.execute(
            "SELECT COUNT(*) AS n FROM warnings WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        )
        return (await cur.fetchone())["n"]

    async def warning_count(self, chat_id, user_id):
        cur = await self.db.execute(
            "SELECT COUNT(*) AS n FROM warnings WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        )
        return (await cur.fetchone())["n"]

    async def clear_warnings(self, chat_id, user_id):
        await self.db.execute(
            "DELETE FROM warnings WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        )
        await self.db.commit()

    async def remove_warning(self, chat_id, user_id):
        cur = await self.db.execute("""
        SELECT id FROM warnings
        WHERE chat_id=? AND user_id=?
        ORDER BY id DESC LIMIT 1
        """, (chat_id, user_id))

        row = await cur.fetchone()

        if row:
            await self.db.execute(
                "DELETE FROM warnings WHERE id=?", (row["id"],)
            )
            await self.db.commit()

        return bool(row)
