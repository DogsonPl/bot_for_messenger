import asyncio
import aiomysql
from ..parse_config import get_database_config
import pymysql


class Database:
    def __init__(self):
        self.pool_connection = loop.run_until_complete(self.connect_to_db())
        loop.create_task(self.create_database())

    @staticmethod
    async def connect_to_db():
        host, user, password, database_name, port = await get_database_config()
        print()
        try:
            pool_connection = await aiomysql.create_pool(host=host, user=user, password=password, port=int(port),
                                                         autocommit=True, db=database_name)
        except pymysql.err.OperationalError:
            raise Exception(f"Have you installed mysql on your computer and created database '{database_name}'?")
        return pool_connection

    @staticmethod
    async def create_database():
        print("Creating database and all tables...")

        await cursor.execute("""CREATE TABLE IF NOT EXISTS groups_information(
                                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                group_id VARCHAR(20) NOT NULL UNIQUE,
                                regulations TEXT,
                                welcome_message TEXT
                                );""")

        await cursor.execute("""CREATE TABLE IF NOT EXISTS casino_players(
                                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                user_id VARCHAR(20) NOT NULL UNIQUE,
                                money FLOAT,
                                take_daily BOOLEAN,
                                daily_strike SMALLINT
                                );""")

        await cursor.execute("""CREATE TABLE IF NOT EXISTS jackpot(
                                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                tickets INTEGER, 
                                user_id VARCHAR(20) NOT NULL UNIQUE,
                                FOREIGN KEY(user_id) REFERENCES casino_players(user_id)
                                    );""")


class Cursor(Database):
    def __init__(self):
        super().__init__()

    async def fetch_data(self, query, args=None):
        async with self.pool_connection.acquire() as connection:
            cursor_ = await connection.cursor()
            await cursor_.execute(query, args)
            data = await cursor_.fetchall()
        return data

    async def execute(self, query, args=None):
        async with self.pool_connection.acquire() as connection:
            cur = await connection.cursor()
            await cur.execute(query, args)


loop = asyncio.get_event_loop()
cursor = Cursor()
