import aiosqlite
from typing import Optional, List, Tuple


class SqlliteDatabase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: str):
        self._db_path = db_path

    @classmethod
    def get_instance(cls, db_path: str) -> Optional["SqlliteDatabase"]:
        if cls._instance is None:
            cls(db_path)
        return cls._instance

    async def initialize(self):
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS Locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    lat REAL NOT NULL,
                    lon REAL NOT NULL,
                    UNIQUE(user_id, name)
                    )
                """
            )
            await db.commit()

    async def add_location(
        self, name: str, user_id: int, lat: float, lon: float
    ) -> bool:
        async with aiosqlite.connect(self._db_path) as db:
            try:
                await db.execute(
                    "INSERT INTO Locations (name, user_id, lat, lon) VALUES (?, ?, ?, ?)",
                    (name, user_id, lat, lon),
                )
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def delete_location(self, name: str, user_id: int) -> bool:
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                "DELETE FROM Locations WHERE user_id = ? AND name = ?", (user_id, name)
            )
            await db.commit()
            return cursor.rowcount > 0

    async def get_user_locations(self, user_id: int) -> List[str]:
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM Locations WHERE user_id = ?", (user_id,)
            )
            locations = await cursor.fetchall()
            return [loc[0] for loc in locations]

    async def get_limit_user_locations(self, user_id: int, limit: int) -> List[List[str]]:
        user_locations = await self.get_user_locations(user_id)

        result = []
        for i in range(0, len(user_locations), limit):
            chunk = user_locations[i:i + limit]
            result.append(chunk)
        return result

    async def get_location_coordinates(
        self, name: str, user_id: int
    ) -> Optional[Tuple[float, float]]:
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                "SELECT lat, lon FROM Locations WHERE user_id = ? AND name = ?",
                (user_id, name),
            )
            result = await cursor.fetchone()
            return result if result else None
