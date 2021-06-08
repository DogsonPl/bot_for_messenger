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
    await cursor.execute("""INSERT INTO jackpot(user_fb_id, tickets)
                            VALUES(%s, %s) AS new_values
                            ON DUPLICATE KEY
                            UPDATE tickets = new_values.tickets;""", (user_fb_id, tickets))


async def register_casino_user(user_fb_id, fb_name):
    try:
        await cursor.execute("""INSERT INTO casino_players(user_fb_id, fb_name, money, take_daily, daily_strike)
                                VALUES(%s, %s, 0, 0, 0);""", (user_fb_id, fb_name))
        return "✅ Pomyślnie się zarejestrowano. Jest możliwa integracja ze stroną www (https://dogson.ovh)"
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


async def reset_old_confirmations_emails():
    await cursor.execute("""DELETE FROM pending_emails_confirmations
                            WHERE creation_time < NOW() - INTERVAL 1 HOUR;""")


async def new_email_confirmation(user_fb_id, email, code):
    try:
        await cursor.execute("""INSERT INTO pending_emails_confirmations(user_fb_id, email, confirmation_code)
                                VALUES(%s, %s, %s);""", (user_fb_id, email, code))
        return False
    except pymysql.IntegrityError:
        return True


async def get_user_email(user_fb_id):
    email, = await cursor.fetch_data("""SELECT email FROM casino_players 
                            WHERE user_fb_id=%s;""", (user_fb_id,))
    return email


async def check_email_confirmation(user_fb_id, code):
    data = await cursor.fetch_data("""SELECT user_fb_id, email, confirmation_code FROM pending_emails_confirmations
                                      WHERE (user_fb_id=%s) AND (confirmation_code=%s);""", (user_fb_id, code))
    if len(data) == 1:
        try:
            await cursor.execute("""UPDATE casino_players
                                    INNER JOIN pending_emails_confirmations 
                                    ON casino_players.user_fb_id = pending_emails_confirmations.user_fb_id
                                    SET casino_players.email = pending_emails_confirmations.email
                                    WHERE (casino_players.user_fb_id = %s) AND (pending_emails_confirmations.confirmation_code = %s)
                                    ;""", (user_fb_id, code))
            return "✅ Twój nowy email został ustawiony (jeśli wcześniej użyłeś komendy !register)"
        except pymysql.err.IntegrityError:
            email = data[0][1]
            user_fb_name, = await cursor.fetch_data("""SELECT fb_name FROM casino_players WHERE user_fb_id=%s;""", (user_fb_id,))
            user_fb_name = user_fb_name[0]
            await cursor.execute("""UPDATE casino_players SET user_fb_id = NULL WHERE user_fb_id=%s;""", (user_fb_id,))
            await cursor.execute("""UPDATE casino_players SET user_fb_id = %s, fb_name = %s
                                    WHERE email= %s;""", (user_fb_id, user_fb_name, email))
            return "✅ Połączono się z twoim kontem na stronie"
        finally:
            await cursor.execute("""DELETE FROM pending_emails_confirmations
                                    WHERE user_fb_id=%s;""", (user_fb_id,))

    else:
        return "🚫 Zły kod"


async def fetch_info_if_user_got_today_daily(user_fb_id):
    try:
        data = await cursor.fetch_data("""SELECT take_daily, daily_strike, money FROM casino_players
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))
        got_daily, strike, money = data[0]
    except IndexError:
        return "", "", ""
    return got_daily, strike, money


async def fetch_top_three_players():
    top_users = await cursor.fetch_data("""SELECT casino_players.fb_name, login_user.username, casino_players.money 
                                           FROM casino_players
                                           LEFT JOIN login_user ON casino_players.user_id = login_user.id
                                           ORDER BY money DESC LIMIT 3;""")
    return top_users


async def fetch_user_money(user_fb_id):
    try:
        data = await cursor.fetch_data("""SELECT money FROM casino_players
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))
        user_money, = data[0]
    except IndexError:
        user_money = "💡 Użyj polecenia !register żeby móc się bawić w kasyno. Wszystkie dogecoiny są sztuczne"
    return user_money


async def fetch_tickets_number():
    data = await cursor.fetch_data("""SELECT SUM(tickets) FROM jackpot;""")
    return data[0][0]


async def fetch_user_tickets(user_fb_id):
    try:
        data = await cursor.fetch_data("""SELECT tickets FROM jackpot
                                          INNER JOIN casino_players ON jackpot.player_id=casino_players.id
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))
        data = data[0][0]
    except IndexError:
        data = 0
    return data


async def fetch_all_jackpot_data_to_make_draw():
    data = await cursor.fetch_data("""SELECT user_fb_id, tickets FROM jackpot;""")
    return data
