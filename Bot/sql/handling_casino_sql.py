from decimal import Decimal
from typing import Union, List, Tuple
from dataclasses import dataclass

import pymysql

from .database import cursor


async def insert_into_user_money(user_fb_id: str, money: Decimal):
    await cursor.execute("""UPDATE casino_players 
                            SET money = %s
                            WHERE user_fb_id = %s;""", (money, user_fb_id))


async def reset_old_confirmations_emails():
    await cursor.execute("""DELETE FROM pending_emails_confirmations
                            WHERE creation_time < NOW() - INTERVAL 1 HOUR;""")


async def new_email_confirmation(user_fb_id: str, email: str, code: int) -> bool:
    try:
        await cursor.execute("""INSERT INTO pending_emails_confirmations(user_fb_id, email, confirmation_code)
                                VALUES(%s, %s, %s);""", (user_fb_id, email, code))
        return False
    except pymysql.IntegrityError:
        return True


async def get_user_email(user_fb_id: str) -> Union[str, bool]:
    email = await cursor.fetch_data("""SELECT email FROM casino_players 
                                       WHERE user_fb_id=%s;""", (user_fb_id,))
    try:
        email = email[0][0]
    except IndexError:
        email = False
    return email


async def check_email_confirmation(user_fb_id: str, code: int) -> str:
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
            old_player, = await cursor.fetch_data("""SELECT fb_name FROM casino_players WHERE user_fb_id=%s;""", (user_fb_id,))
            user_fb_name, = old_player
            await cursor.execute("""UPDATE casino_players SET user_fb_id = NULL, money = 0 
                                    WHERE user_fb_id=%s;""", (user_fb_id,))
            await cursor.execute("""UPDATE casino_players SET user_fb_id = %s, fb_name = %s
                                    WHERE email = %s;""", (user_fb_id, user_fb_name, email))
            return "✅ Połączono się z twoim kontem na stronie"
        finally:
            await cursor.execute("""DELETE FROM pending_emails_confirmations
                                    WHERE user_fb_id=%s;""", (user_fb_id,))

    else:
        return "🚫 Podano niepoprawny kod"


async def fetch_top_three_players() -> Tuple[List, List]:
    top_users = await cursor.fetch_data("""SELECT casino_players.fb_name, login_user.username, casino_players.money 
                                           FROM casino_players
                                           LEFT JOIN login_user ON casino_players.user_id = login_user.id
                                           ORDER BY money DESC LIMIT 3;""")
    top_legendary_users = await cursor.fetch_data("""SELECT casino_players.fb_name, login_user.username, casino_players.legendary_dogecoins 
                                                     FROM casino_players
                                                     LEFT JOIN login_user ON casino_players.user_id = login_user.id
                                                     ORDER BY legendary_dogecoins DESC LIMIT 3;""")
    return top_users, top_legendary_users


async def fetch_user_money(user_fb_id: str) -> Union[Decimal, str]:
    try:
        data = await cursor.fetch_data("""SELECT money FROM casino_players
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))
        user_money, = data[0]
    except IndexError:
        user_money = "💡 Użyj polecenia !register żeby móc się bawić w kasyno. Wszystkie dogecoiny są sztuczne"
    return user_money


async def fetch_user_all_money(user_fb_id) -> Tuple[Decimal, Decimal]:
    try:
        data = await cursor.fetch_data("""SELECT money, legendary_dogecoins FROM casino_players
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))
        user_money, legendary_dogecoins = data[0]
    except IndexError:
        user_money = "💡 Użyj polecenia !register żeby móc się bawić w kasyno. Wszystkie dogecoiny są sztuczne"
        legendary_dogecoins = None
    return user_money, legendary_dogecoins


@dataclass
class LastJackpotResults:
    username: str
    fb_name: str
    prize: float


async def get_last_jackpot_results() -> LastJackpotResults:
    data, = await cursor.fetch_data("""SELECT username, fb_name, prize FROM jackpots_results
                                      INNER JOIN casino_players ON jackpots_results.winner_id=casino_players.id
                                      LEFT JOIN login_user ON casino_players.user_id=login_user.id
                                      ORDER BY jackpots_results.id DESC
                                      LIMIT 1;""")
    return LastJackpotResults(data[0], data[1], data[2])


async def fetch_tickets_number() -> int:
    data = await cursor.fetch_data("""SELECT SUM(tickets) FROM jackpot;""")
    data = data[0][0]
    if data is None:
        data = 0
    return data


async def fetch_user_tickets(user_fb_id: str) -> int:
    try:
        data = await cursor.fetch_data("""SELECT tickets FROM jackpot
                                          INNER JOIN casino_players ON jackpot.player_id=casino_players.id
                                          WHERE user_fb_id = %s LIMIT 1;""", (user_fb_id,))
        data = data[0][0]
    except IndexError:
        data = 0
    return data


@dataclass
class UserProfile:
    won_bets: int
    lost_bets: int
    today_scratch_bought: int
    best_season: float
    biggest_win: float
    last_season_dogecoins: float
    total_scratch_bought: int
    season_first_place: int
    season_second_place: int
    season_third_place: int
    won_dc: float
    lost_dc: float

async def fetch_user_profil_data(user_fb_id) -> UserProfile:
    try:
        data, = await cursor.fetch_data("""SELECT won_bets, lost_bets, today_scratch_bought, best_season, biggest_win, last_season_dogecoins, total_scratch_bought, season_first_place, season_second_place, season_third_place, won_dc, lost_dc
                                          FROM casino_players
                                          WHERE user_fb_id = %s;""", (user_fb_id,))
    except (ValueError, IndexError):
        data = ["No data" for _ in range(12)]
    return UserProfile(*data)


async def create_duel(duel_creator: str, wage: float, opponent: str) -> Tuple[str, bool]:
    try:
        await cursor.execute("""INSERT INTO duels(wage, duel_creator, opponent)
                                VALUES(%s, %s, %s);""", (wage, duel_creator, opponent))
        message = "🕛 Oczekiwanie na akceptacje gry... (twój przeciwnik musi wpisać !duel akceptuj)"
        created = True
    except pymysql.IntegrityError:
        message = """🚫 Możesz tworzyć jedną grę jednocześnie, jeśli chcesz ją anulować napisz !duel odrzuć. 
Również osoba z która chcesz grać nie może mieć żadnych gier w trakcie"""
        created = False
    return message, created


async def fetch_duel_info(opponent: str):
    data = await cursor.fetch_data("""SELECT wage, duel_creator, opponent FROM duels
                                      WHERE opponent = %s;""", (opponent,))
    return data


async def delete_duels(fb_id: str, give_money_back=False):
    if give_money_back:
        await cursor.execute("""UPDATE casino_players
                                INNER JOIN duels wage ON casino_players.user_fb_id = duel_creator
                                SET money = money+wage;""")
    await cursor.execute("""DELETE FROM duels
                            WHERE duel_creator = %s OR opponent = %s;""", (fb_id, fb_id))


async def fetch_user_achievements(user_fb_id):
    data = await cursor.fetch_data("""SELECT name, description, player_score, achievement_level 
                                      FROM achievements_players_link_table
                                      INNER JOIN achievements
                                      ON achievements_players_link_table.achievement_id=achievements.id
                                      INNER JOIN casino_players 
                                      ON achievements_players_link_table.player_id=casino_players.id 
                                      WHERE user_fb_id = %s;""", (user_fb_id,))
    return data


async def delete_duels_new_season():
    await cursor.execute("""DELETE FROM duels;""")


async def get_shop_items():
    data = await cursor.fetch_data("""SELECT id, cost, description FROM shop;""")
    return data
