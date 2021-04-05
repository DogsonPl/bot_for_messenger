import asyncio
import aiosqlite
from . import daily_actions, create_database


class Database:
    async def fetch_data(self, query, args=None):
        cursor = await CONNECTION.execute(query, args)
        data = await cursor.fetchall()
        await cursor.close()
        return data

    async def execute(self, query, *args):
        await CONNECTION.execute(query, args)


async def get_connection():
    return await aiosqlite.connect("Bot//data//database.db", check_same_thread=False, isolation_level=None)

loop = asyncio.get_event_loop()
CONNECTION = loop.run_until_complete(get_connection())
loop.create_task(create_database.CreateTablesIfNotExists().async_init())
loop.create_task(daily_actions.restarting_daily_in_db())

database = Database()
