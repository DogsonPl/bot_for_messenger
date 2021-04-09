import pymysql
from .database import cursor


async def insert_into_daily(user_fb_id, strike, coins_to_give):
    await cursor.execute("""UPDATE casino_players 
                            SET money = %s, take_daily = '1',  daily_strike = %s
                            WHERE user_fb_id = %s;""", (coins_to_give, strike, user_fb_id))


async def insert_into_user_money(user_fb_id, money):
    await cursor.execute("""UPDATE casino_players 
                            SET money = %s
                            WHERE user_fb_id = %s;""", (money, user_fb_id))


async def add_jackpot_tickets(user_fb_id, tickets):
    await cursor.execute("""UPDATE jackpot 
                            SET tickets = %s
                            WHERE user_fb_id = %s;""", (tickets, user_fb_id))


async def register_casino_user(user_fb_id, fb_name):
    try:
        await cursor.execute("""INSERT INTO casino_players(user_fb_id, fb_name)
                                VALUES(%s, %s)""", (user_fb_id, fb_name))
        return "✅ Zarejestrowano pomyślnie"
    except pymysql.IntegrityError:
        return "🚫 Masz już założone konto"


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
        data = await cursor.fetch_data("""SELECT take_daily, daily_strike, money FROM casino_players
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))
        got_daily, strike, money = data[0]
    except IndexError:
        return "", "", ""
    return got_daily, strike, money


async def fetch_top_three_players():
    top_users = await cursor.fetch_data("""SELECT user_fb_id, money FROM casino_players
                                           ORDER BY money DESC LIMIT 3;""")
    return top_users


async def fetch_user_money(user_fb_id):
    try:
        data = await cursor.fetch_data("""SELECT money FROM casino_players
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))
        user_money, = data[0]
    except IndexError:
        user_money = "💡 Użyj poelcenia !register żeby móc się bawić w kasyno. Wszystkie dogecoiny są sztuczne"
    return user_money


async def fetch_tickets_number():
    data = await cursor.fetch_data("""SELECT SUM(tickets) FROM jackpot;""")
    return data[0]


async def fetch_user_tickets(user_fb_id):
    try:
        data = await cursor.fetch_data("""SELECT tickets FROM jackpot
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))

        data = data[0]
    except IndexError:
        data = 0
    return data


async def fetch_all_jackpot_data_to_make_draw():
    data = await cursor.fetch_data("""SELECT user_fb_id, tickets FROM jackpot;""")
    return data
