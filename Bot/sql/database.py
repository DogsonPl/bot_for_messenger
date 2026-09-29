import asyncio
from contextlib import asynccontextmanager

import aiomysql
import pymysql

from ..parse_config import get_database_config


class Database:
    def __init__(self):
        self.pool_connection = loop.run_until_complete(self.connect_to_db())
        loop.create_task(self.create_database())

    @staticmethod
    async def connect_to_db():
        db_config = await get_database_config()
        try:
            pool_connection = await aiomysql.create_pool(host=db_config.host, user=db_config.user,
                                                         password=db_config.password, port=db_config.port,
                                                         autocommit=True, db=db_config.database_name,
                                                         maxsize=100, loop=loop)
        except pymysql.err.OperationalError:
            raise Exception(f"Have you installed mysql on your computer and created database '{db_config.database_name}'?")
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

        await cursor.execute("""CREATE TABLE IF NOT EXISTS pending_emails_confirmations(
                                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                user_fb_id VARCHAR(20) UNIQUE,
                                email VARCHAR(100),
                                confirmation_code MEDIUMINT,
                                creation_time DATETIME DEFAULT NOW()
                                );""")

        await cursor.execute("""CREATE TABLE IF NOT EXISTS duels(
                                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                wage FLOAT,
                                duel_creator VARCHAR(20) UNIQUE,
                                opponent VARCHAR(20) UNIQUE,
                                creation_time DATETIME DEFAULT NOW()
                                );""")


class Transaction:

    def __init__(self, cur):
        self._cur = cur

    async def fetch_data(self, query, args=None):
        await self._cur.execute(query, args)
        return await self._cur.fetchall()

    async def execute(self, query, args=None) -> int:
        await self._cur.execute(query, args)
        return self._cur.rowcount


class Cursor(Database):
    def __init__(self):
        super().__init__()

    async def fetch_data(self, query, args=None):
        async with self.pool_connection.acquire() as connection:
            async with connection.cursor() as cur:
                await cur.execute(query, args)
                return await cur.fetchall()

    async def execute(self, query, args=None) -> int:
        async with self.pool_connection.acquire() as connection:
            async with connection.cursor() as cur:
                await cur.execute(query, args)
                return cur.rowcount

    @asynccontextmanager
    async def transaction(self):
        async with self.pool_connection.acquire() as connection:
            await connection.begin()
            try:
                async with connection.cursor() as cur:
                    yield Transaction(cur)
                await connection.commit()
            except BaseException:
                await connection.rollback()
                raise


loop = asyncio.get_event_loop()
cursor = Cursor()
