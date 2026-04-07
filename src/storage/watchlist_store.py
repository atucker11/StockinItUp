import aiosqlite

from ..config import settings


class WatchlistStore:
    def __init__(self) -> None:
        self.path = str(settings.sqlite_path_obj)

    async def init(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS watchlists (
                    guild_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    PRIMARY KEY (guild_id, user_id, symbol)
                )
                '''
            )
            await db.commit()

    async def add(self, guild_id: int, user_id: int, symbol: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO watchlists (guild_id, user_id, symbol) VALUES (?, ?, ?)",
                (str(guild_id), str(user_id), symbol),
            )
            await db.commit()

    async def remove(self, guild_id: int, user_id: int, symbol: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "DELETE FROM watchlists WHERE guild_id = ? AND user_id = ? AND symbol = ?",
                (str(guild_id), str(user_id), symbol),
            )
            await db.commit()

    async def list_for_user(self, guild_id: int, user_id: int) -> list[str]:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "SELECT symbol FROM watchlists WHERE guild_id = ? AND user_id = ? ORDER BY symbol",
                (str(guild_id), str(user_id)),
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
