import pymysql
from .database import cursor


async def insert_into_user_money(user_fb_id, money):
    await cursor.execute("""UPDATE casino_players 
                            SET money = %s
                            WHERE user_fb_id = %s;""", (money, user_fb_id))


async def register_casino_user(user_fb_id, fb_name):
    try:
        await cursor.execute("""INSERT INTO casino_players(user_fb_id, fb_name, money, take_daily, daily_strike, won_bets, lost_bets, today_won_money, today_lost_money, total_bets, today_scratch_profit, last_time_scratch)
                                VALUES(%s, %s, 0, 0, 0, 0, 0, 0, 0, 0, 0, %s);""", (user_fb_id, fb_name, None))
        return "✅ Pomyślnie się zarejestrowano. Jest możliwa integracja ze stroną www (https://dogson.ovh). Po więcej informacji napisz !strona"
    except pymysql.IntegrityError:
        return "🚫 Masz już założone konto"


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
    email = await cursor.fetch_data("""SELECT email FROM casino_players 
                            WHERE user_fb_id=%s;""", (user_fb_id,))
    try:
        email = email[0][0]
    except IndexError:
        email = False
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
            await cursor.execute("""UPDATE casino_players SET user_fb_id = NULL, money = 0 
                                    WHERE user_fb_id=%s;""", (user_fb_id,))
            await cursor.execute("""UPDATE casino_players SET user_fb_id = %s, fb_name = %s
                                    WHERE email= %s;""", (user_fb_id, user_fb_name, email))
            return "✅ Połączono się z twoim kontem na stronie"
        finally:
            await cursor.execute("""DELETE FROM pending_emails_confirmations
                                    WHERE user_fb_id=%s;""", (user_fb_id,))

    else:
        return "🚫 Zły kod"


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


async def get_last_jackpot_results():
    data, = await cursor.fetch_data("""SELECT username, fb_name, prize FROM jackpots_results
                                      INNER JOIN casino_players ON jackpots_results.winner_id=casino_players.id
                                      LEFT JOIN login_user ON casino_players.user_id=login_user.id
                                      ORDER BY jackpots_results.id DESC
                                      LIMIT 1;""")
    return data


async def fetch_tickets_number():
    data = await cursor.fetch_data("""SELECT SUM(tickets) FROM jackpot;""")
    data = data[0][0]
    if data is None:
        data = 0
    return data


async def fetch_user_tickets(user_fb_id):
    try:
        data = await cursor.fetch_data("""SELECT tickets FROM jackpot
                                          INNER JOIN casino_players ON jackpot.player_id=casino_players.id
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))
        data = data[0][0]
    except IndexError:
        data = 0
    return data


async def fetch_user_stats(user_fb_id):
    try:
        data = await cursor.fetch_data("""SELECT won_bets, lost_bets, today_won_money, today_lost_money, today_scratch_profit FROM casino_players
                                           WHERE user_fb_id = %s;""", (user_fb_id,))
        won_bets, lost_bets, today_won_money, today_lost_money, today_scratch_profit = data[0]
    except (ValueError, IndexError):
        won_bets, lost_bets, today_won_money, today_lost_money, today_scratch_profit = "No data", "No data", "No data", "No data", "No data"
    return won_bets, lost_bets, today_won_money, today_lost_money, today_scratch_profit


async def create_duel(duel_creator, wage, opponent):
    try:
        await cursor.execute("""INSERT INTO duels(wage, duel_creator, opponent)
                                VALUES(%s, %s, %s);""", (wage, duel_creator, opponent))
        message = "🕛 Oczekiwanie na akceptacje gry... (twój przeciwnik musi wpisać !duel akceptuj)"
    except pymysql.IntegrityError:
        message = """🚫 Możesz tworzyć jedną grę jednocześnie, jeśli chcesz ją anulować napisz !duel odrzuć. 
Również osoba z która chcesz grać nie może mieć żadnych gier w trakcie"""
    return message


async def fetch_duel_info(opponent):
    data = await cursor.fetch_data("""SELECT wage, duel_creator, opponent FROM duels
                                      WHERE opponent = %s;""", (opponent,))
    return data


async def delete_duels(fb_id, give_money_back=False):
    if give_money_back:
        await cursor.execute("""UPDATE casino_players
                                INNER JOIN duels wage ON casino_players.user_fb_id = duel_creator
                                SET money = money+wage;""")
    await cursor.execute("""DELETE FROM duels
                            WHERE duel_creator = %s OR opponent = %s;""", (fb_id, fb_id))
