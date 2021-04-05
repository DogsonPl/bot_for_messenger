class CreateTablesIfNotExists:
    async def async_init(self):
        await self.create_group_info_table()
        await self.create_casino_players_table()
        await self.create_jackpot_table()

    def __await__(self):
        return self.async_init().__await__()

    @staticmethod
    async def create_group_info_table():
        print("Creating group info table if not exists...")
        await CONNECTION.execute("""CREATE TABLE IF NOT EXISTS groups_information(
                                    id INTEGER PRIMARY KEY,
                                    group_id INTEGER NOT NULL UNIQUE,
                                    regulations TEXT,
                                    welcome_message TEXT
                                    );""")

    @staticmethod
    async def create_casino_players_table():
        print("Creating casino players table if not exists...")
        await CONNECTION.execute("""CREATE TABLE IF NOT EXISTS casino_players(
                                    id INTEGER PRIMARY KEY,
                                    user_id INTEGER NOT NULL UNIQUE,
                                    money FLOAT,
                                    take_daily BIT,
                                    daily_strike INTEGER
                                    );""")

    @staticmethod
    async def create_jackpot_table():
        print("Creating jackpot table if not exists...")
        await CONNECTION.execute("""CREATE TABLE IF NOT EXISTS jackpot(
                                    id INTEGER PRIMARY KEY,
                                    tickets INTEGER, 
                                    user_id INTEGER NOT NULL UNIQUE,
                                    FOREIGN KEY(user_id) REFERENCES casino_players(user_id)
                                    );""")
