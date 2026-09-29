from decimal import Decimal
from typing import Union, List, Tuple, Callable, Optional
from dataclasses import dataclass

import pymysql

from .database import cursor


class _NotEnoughMoney(Exception):
    pass


def to_money(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


async def insert_into_user_money(user_fb_id: str, money: Decimal):
    await cursor.execute("""UPDATE casino_players 
                            SET money = %s
                            WHERE user_fb_id = %s;""", (money, user_fb_id))




async def transfer_money(sender: str, receiver: str, amount: Decimal) -> bool:
    rows = await cursor.execute("""UPDATE casino_players s
                                   JOIN casino_players r ON r.user_fb_id = %s
                                   SET s.money = s.money - %s,
                                       r.money = r.money + %s
                                   WHERE s.user_fb_id = %s
                                     AND s.user_fb_id <> r.user_fb_id
                                     AND s.money >= %s;""",
                                (receiver, amount, amount, sender, amount))
    return rows == 1


async def try_charge(user_fb_id: str, amount: Decimal) -> bool:
    rows = await cursor.execute("""UPDATE casino_players
                                   SET money = money - %s
                                   WHERE user_fb_id = %s AND money >= %s;""",
                                (amount, user_fb_id, amount))
    return rows == 1


async def add_money(user_fb_id: str, amount: Decimal):
    await cursor.execute("""UPDATE casino_players
                            SET money = money + %s
                            WHERE user_fb_id = %s;""", (amount, user_fb_id))


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


async def check_email_confirmation(user_fb_id: str, code: int) -> Union[str, bool]:
    data = await cursor.fetch_data("""SELECT user_fb_id, email, confirmation_code FROM pending_emails_confirmations
                                      WHERE (user_fb_id=%s) AND (confirmation_code=%s);""", (user_fb_id, code))
    if len(data) == 1:
        await cursor.execute("""DELETE FROM pending_emails_confirmations
                                WHERE user_fb_id=%s;""", (user_fb_id,))
        return data[0][1]  # return: email
    else:
        return False


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



async def create_duel_paid(creator: str, wage: Decimal, opponent: str) -> str:
    try:
        async with cursor.transaction() as tx:
            await tx.execute("""INSERT INTO duels(wage, duel_creator, opponent)
                                VALUES(%s, %s, %s);""", (wage, creator, opponent))
            stored = await tx.fetch_data("""SELECT wage FROM duels
                                            WHERE duel_creator = %s;""", (creator,))
            real_wage = to_money(stored[0][0])
            charged = await tx.execute("""UPDATE casino_players
                                          SET money = money - %s
                                          WHERE user_fb_id = %s AND money >= %s;""",
                                       (real_wage, creator, real_wage))
            if charged != 1:
                raise _NotEnoughMoney
            return "ok"
    except _NotEnoughMoney:
        return "no_money"
    except pymysql.IntegrityError:
        return "exists"


async def settle_duel(acceptor: str,
                      pick_winner: Callable[[str, str], str]) -> Tuple[str, Optional[Decimal], Optional[str]]:
    async with cursor.transaction() as tx:
        duels = await tx.fetch_data("""SELECT wage, duel_creator, opponent FROM duels
                                       WHERE opponent = %s FOR UPDATE;""", (acceptor,))
        if not duels:
            return "no_duel", None, None
        wage, creator, opponent = duels[0]
        wage = to_money(wage)

        charged = await tx.execute("""UPDATE casino_players SET money = money - %s
                                      WHERE user_fb_id = %s AND money >= %s;""",
                                   (wage, acceptor, wage))
        if charged != 1:
            return "no_money", wage, None

        await tx.execute("DELETE FROM duels WHERE duel_creator = %s;", (creator,))
        winner = pick_winner(creator, opponent)
        await tx.execute("""UPDATE casino_players SET money = money + %s
                            WHERE user_fb_id = %s;""", (wage * 2, winner))
        return "ok", wage, winner


async def fetch_duel_info(opponent: str):
    data = await cursor.fetch_data("""SELECT wage, duel_creator, opponent FROM duels
                                      WHERE opponent = %s;""", (opponent,))
    return data


async def delete_duels(fb_id: str, give_money_back=False):
    async with cursor.transaction() as tx:
        rows = await tx.fetch_data("""SELECT wage FROM duels
                                      WHERE duel_creator = %s FOR UPDATE;""", (fb_id,))
        if give_money_back and rows:
            await tx.execute("""UPDATE casino_players SET money = money + %s
                                WHERE user_fb_id = %s;""", (to_money(rows[0][0]), fb_id))
        await tx.execute("""DELETE FROM duels
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
