import aiosqlite
import aioschedule
import asyncio


class InsertIntoDatabase:

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def __await__(self):
        return self.__aenter__().__await__()

    @staticmethod
    async def insert_group_regulations(group_id, regulations):
        await CONNECTION.execute("""INSERT INTO groups_information(group_id, regulations) 
                                    VALUES(?, ?)
                                    ON CONFLICT (group_id) DO
                                    UPDATE SET regulations=excluded.regulations;""", (group_id, regulations))

    @staticmethod
    async def insert_welcome_messages(group_id, welcome_message):
        await CONNECTION.execute("""INSERT INTO groups_information(group_id, welcome_message) 
                                    VALUES(?, ?)
                                    ON CONFLICT (group_id) DO
                                    UPDATE SET welcome_message=excluded.welcome_message;""", (group_id, welcome_message))

    @staticmethod
    async def insert_into_daily_strike(user_id, strike):
        await CONNECTION.execute("""INSERT INTO casino_players(user_id, daily_strike)
                                    VALUES(?, ?)
                                    ON CONFLICT (user_id) DO
                                    UPDATE SET daily_strike=excluded.daily_strike;""", (user_id, strike))

    @staticmethod
    async def insert_into_user_money(user_id, money):
        await CONNECTION.execute("""INSERT INTO casino_players(user_id, money)
                                    VALUES(?, ?)
                                    ON CONFLICT (user_id) DO
                                    UPDATE SET money = excluded.money;""", (user_id, money))

    @staticmethod
    async def insert_into_daily(user_id):
        await CONNECTION.execute("""INSERT INTO casino_players(user_id, take_daily)
                                    VALUES(?, 1)
                                    ON CONFLICT (user_id) DO
                                    UPDATE SET take_daily = excluded.take_daily;""", (user_id,))

    @staticmethod
    async def reset_daily():
        print("Daily has been reset...")
        await CONNECTION.execute("""UPDATE casino_players
                                    SET daily_strike = 1 
                                    WHERE take_daily = 0;""")
        await CONNECTION.execute("""UPDATE casino_players
                                    SET take_daily = 0;""")


class GetInfoFromDatabase:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def __await__(self):
        return self.__aenter__().__await__()

    @staticmethod
    async def fetch_group_regulations(group_id):
        cursor = await CONNECTION.execute("""SELECT regulations FROM groups_information
                                             WHERE group_id = ?;""", (group_id,))
        data = await cursor.fetchall()
        await cursor.close()
        return data

    @staticmethod
    async def fetch_welcome_message(group_id):
        cursor = await CONNECTION.execute("""SELECT welcome_message FROM groups_information
                                             WHERE group_id = ?;""", (group_id,))
        data = await cursor.fetchall()
        await cursor.close()
        return data

    @staticmethod
    async def fetch_info_if_user_got_today_daily(user_id):
        cursor = await CONNECTION.execute("""SELECT take_daily, daily_strike FROM casino_players
                                             WHERE user_id = ?;""", (user_id,))
        data = await cursor.fetchall()
        await cursor.close()
        return data

    @staticmethod
    async def fetch_top_three_players():
        cursor = await CONNECTION.execute("""SELECT user_id, money FROM casino_players
                                             ORDER BY money DESC LIMIT 3;""")
        data = await cursor.fetchall()
        await cursor.close()
        return data

    @staticmethod
    async def fetch_user_money(user_id):
        cursor = await CONNECTION.execute("""SELECT money FROM casino_players
                                             WHERE user_id = ?;""", (user_id,))
        data = await cursor.fetchall()
        await cursor.close()
        return data


class CreateTablesIfNotExists:
    async def async_init(self):
        await self.create_group_info_database()
        await self.create_casino_players_database()

    def __await__(self):
        return self.async_init().__await__()

    @staticmethod
    async def create_group_info_database():
        print("Creating group info database if not exists...")
        await CONNECTION.execute("""CREATE TABLE IF NOT EXISTS groups_information(
                                    id INTEGER PRIMARY KEY,
                                    group_id INTEGER NOT NULL UNIQUE,
                                    regulations TEXT,
                                    welcome_message TEXT
                                    );""")

    @staticmethod
    async def create_casino_players_database():
        print("Creating casino_players if not exists...")
        await CONNECTION.execute("""CREATE TABLE IF NOT EXISTS casino_players(
                                    id INTEGER PRIMARY KEY,
                                    user_id INTEGER NOT NULL UNIQUE,
                                    money FLOAT,
                                    take_daily BIT,
                                    daily_strike INTEGER
                                    );""")


async def restarting_daily_in_db():
    aioschedule.every().day.at("23:00").do(InsertIntoDatabase().reset_daily)
    while True:
        loop.create_task(aioschedule.run_pending())
        await asyncio.sleep(60)


loop = asyncio.get_event_loop()
CONNECTION = loop.run_until_complete(aiosqlite.connect("Bot//data//database.db", check_same_thread=False, isolation_level=None))
loop.create_task(CreateTablesIfNotExists().async_init())
loop.create_task(restarting_daily_in_db())
