from .database import cursor


async def insert_into_daily(user_fb_id, strike, coins_to_give):
    await cursor.execute("""INSERT INTO casino_players(user_fb_id, money, take_daily, daily_strike)
                            VALUES(%s, %s, '1', %s) AS new_values
                            ON DUPLICATE KEY
                            UPDATE money = new_values.money, take_daily = new_values.take_daily, 
                                   daily_strike = new_values.daily_strike;""", (user_fb_id, coins_to_give, strike))


async def insert_into_user_money(user_fb_id, money):
    await cursor.execute("""INSERT INTO casino_players(user_fb_id, money)
                            VALUES(%s, %s) AS new_values
                            ON DUPLICATE KEY
                            UPDATE money = new_values.money;""", (user_fb_id, money))


async def add_jackpot_tickets(user_fb_id, tickets):
    await cursor.execute("""INSERT INTO jackpot(user_fb_id, tickets)
                            VALUES(%s, %s) AS new_values
                            ON DUPLICATE KEY
                            UPDATE tickets = new_values.tickets;""", (user_fb_id, tickets))


async def register_casino_user(user_fb_id, money, fb_name):
    await cursor.execute("""INSERT INTO casino_players(user_fb_id, money, fb_name)
                            VALUES(%s, %s, %s)""", (user_fb_id, money, fb_name))


async def reset_jackpot_label():
    await cursor.execute("""DELETE FROM jackpot;""")


async def reset_casino_daily_label():
    await cursor.execute("""UPDATE casino_players
                            SET daily_strike = 1 
                            WHERE take_daily = 0;""")
    await cursor.execute("""UPDATE casino_players
                            SET take_daily = 0;""")


async def fetch_info_if_user_got_today_daily(user_fb_id):
    try:
        data = await cursor.fetch_data("""SELECT take_daily, daily_strike FROM casino_players
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))
        got_daily = data[0][0]
        strike = data[0][1]
    except IndexError:
        got_daily = 0
        strike = 1
    return got_daily, strike


async def fetch_top_three_players():
    try:
        top_users = await cursor.fetch_data("""SELECT user_fb_id, money FROM casino_players
                                               ORDER BY money DESC LIMIT 3;""")
        return top_users
    except IndexError:
        return []


async def fetch_user_money(user_fb_id):
    try:
        data = await cursor.fetch_data("""SELECT money FROM casino_players
                                          WHERE user_fb_id = %s;""", (user_fb_id,))
        user_money = data[0][0]
    except IndexError:
        user_money = 0
    if user_money is None:
        user_money = 0
    return user_money


async def fetch_tickets_number():
    data = await cursor.fetch_data("""SELECT SUM(tickets) FROM jackpot;""")
    return data[0][0]


async def fetch_user_tickets(user_fb_id):
    try:
        data = await cursor.fetch_data("""SELECT tickets FROM jackpot
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))

        data = data[0][0]
    except IndexError:
        data = 0
    return data


async def fetch_all_jackpot_data_to_make_draw():
    data = await cursor.fetch_data("""SELECT user_fb_id, tickets FROM jackpot;""")
    return data
