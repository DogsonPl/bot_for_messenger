from .database import cursor


async def insert_into_daily(user_id, strike, coins_to_give):
    await cursor.execute("""INSERT INTO casino_players(user_id, money, take_daily, daily_strike)
                              VALUES(?, ?, 1, ?)
                              ON CONFLICT (user_id) DO
                              UPDATE SET take_daily = excluded.take_daily, money = excluded.money, 
                                         daily_strike = excluded.daily_strike;""", (user_id, coins_to_give, strike))


async def insert_into_user_money(user_id, money):
    await cursor.execute("""INSERT INTO casino_players(user_id, money)
                            VALUES(?, ?)
                            ON CONFLICT (user_id) DO
                            UPDATE SET money = excluded.money;""", (user_id, money))


async def add_jackpot_tickets(user_id, tickets):
    await cursor.execute("""INSERT INTO jackpot(user_id, tickets)
                            VALUES(?, ?)
                            ON CONFLICT (user_id) DO
                            UPDATE SET tickets = excluded.tickets;""", (user_id, tickets))


async def reset_jackpot_label():
    await cursor.execute("""DELETE FROM jackpot;""")


async def fetch_info_if_user_got_today_daily(user_id):
    try:
        data = await cursor.fetch_data("""SELECT take_daily, daily_strike FROM casino_players
                                          WHERE user_id = ?;""", (user_id,))
        got_daily = data[0][0]
        strike = data[0][1]
    except IndexError:
        got_daily = 0
        strike = 1
    return got_daily, strike


async def fetch_top_three_players():
    try:
        top_users = await cursor.fetch_data("""SELECT user_id, money FROM casino_players
                                               ORDER BY money DESC LIMIT 3;""")
        return top_users
    except IndexError:
        return []


async def fetch_user_money(user_id):
    try:
        data = await cursor.fetch_data("""SELECT money FROM casino_players
                                          WHERE user_id = ?;""", (user_id,))
        user_money = data[0][0]
    except IndexError:
        user_money = 0
    if user_money is None:
        user_money = 0
    return user_money


async def fetch_tickets_number():
    data = await cursor.fetch_data("""SELECT SUM(tickets) FROM jackpot;""")
    return data[0][0]


async def fetch_user_tickets(user_id):
    try:
        data = await cursor.fetch_data("""SELECT tickets FROM jackpot
                                          WHERE user_id = ?;""", (user_id,))

        data = data[0][0]
    except IndexError:
        data = 0
    return data


async def fetch_all_jackpot_data_to_make_draw():
    data = await cursor.fetch_data("""SELECT user_id, tickets FROM jackpot;""")
    return data
