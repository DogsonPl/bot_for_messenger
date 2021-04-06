import asyncio
import aiosqlite



class Database:
    def __init__(self):
        self.connection = loop.run_until_complete(self.connect_to_db())
        loop.create_task(self.create_database())

    @staticmethod
    async def connect_to_db():
        return await aiosqlite.connect("Bot//data//database.db", check_same_thread=False, isolation_level=None)

    @staticmethod
    async def create_database():
        print("Creating database and all tables...")
        await cursor.execute("""CREATE TABLE IF NOT EXISTS groups_information(
                                    id INTEGER PRIMARY KEY,
                                    group_id INTEGER NOT NULL UNIQUE,
                                    regulations TEXT,
                                    welcome_message TEXT
                                    );""")

        await cursor.execute("""CREATE TABLE IF NOT EXISTS casino_players(
                                    id INTEGER PRIMARY KEY,
                                    user_id INTEGER NOT NULL UNIQUE,
                                    money FLOAT,
                                    take_daily BIT,
                                    daily_strike INTEGER
                                    );""")

        await cursor.execute("""CREATE TABLE IF NOT EXISTS jackpot(
                                    id INTEGER PRIMARY KEY,
                                    tickets INTEGER, 
                                    user_id INTEGER NOT NULL UNIQUE,
                                    FOREIGN KEY(user_id) REFERENCES casino_players(user_id)
                                    );""")


class Cursor(Database):
    def __init__(self):
        super().__init__()

    async def fetch_data(self, query, args=None):
        cursor_ = await self.connection.execute(query, args)
        data = await cursor_.fetchall()
        await cursor_.close()
        return data

    async def execute(self, query, args=None):
        await self.connection.execute(query, args)


loop = asyncio.get_event_loop()
cursor = Cursor()
