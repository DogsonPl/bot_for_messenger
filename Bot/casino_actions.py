import random as rd
import requests
from decimal import Decimal, getcontext
from dataclasses import dataclass
from typing import Tuple, List, Union

import fbchat

from .sql import handling_casino_sql
from .parse_config import django_password
from .task_scheduler import last_jackpot_data


getcontext().prec = 20

DJANGO_PASSWORD: str = django_password


async def take_daily(event: fbchat.MessageEvent) -> str:
    response = requests.post("http://127.0.0.1:8000/casino/set_daily_fb",
                             data={"fb_user_id": event.author.id, "django_password": django_password})
    message = response.json()
    return message["message"]


async def make_bet(event: fbchat.MessageEvent) -> str:
    message_values = event.message.text.split()
    try:
        bet_money = abs(float(message_values[1].replace(",", ".")))
        percent_to_win = abs(int(message_values[2]))
    except (ValueError, IndexError):
        return "🚫 Wygląd komendy: !bet x y, gdzie x to liczba monet które obstawiasz a y to % na wygraną"

    response = requests.post("http://127.0.0.1:8000/casino/bet_fb",
                             data={"fb_user_id": event.author.id, "bet_money": bet_money,
                                   "percent_to_win": percent_to_win, "django_password": django_password})
    response = response.json()
    message = response["message"].replace("<strong>", "").replace("</strong>.", "")
    return message


async def make_tip(event: fbchat.MessageEvent) -> str:
    try:
        mention = event.message.mentions[0]
        money_to_give = abs(Decimal(event.message.text.split()[1].replace(",", ".")))
    except (IndexError, ValueError, TypeError):
        return "🚫 Wygląd komendy: !tip liczba_monet oznaczenie_osoby"

    sender_money = await handling_casino_sql.fetch_user_money(event.author.id)
    try:
        if sender_money < money_to_give:
            return "🚫 Nie masz wystarczająco pieniędzy"
    except TypeError:
        return sender_money

    receiver_money = await handling_casino_sql.fetch_user_money(mention.thread_id)
    try:
        receiver_money += money_to_give
    except TypeError:
        return "🚫 Osoba której chcesz dać dogi nie użyła nigdy komendy !register"
    sender_money -= money_to_give
    await handling_casino_sql.insert_into_user_money(event.author.id, sender_money)
    await handling_casino_sql.insert_into_user_money(mention.thread_id, receiver_money)
    return f"✅ Wysłano {money_to_give} do drugiej osoby :)"


async def buy_jackpot_ticket(event: fbchat.MessageEvent) -> str:
    try:
        tickets_to_buy = abs(int(event.message.text.split()[1]))
    except (IndexError, ValueError, TypeError):
        return "🚫 Wygląd komendy: !jackpotbuy liczba_biletów"
    response = requests.post("http://127.0.0.1:8000/casino/jackpot_buy_fb",
                             data={"user_fb_id": event.author.id, "tickets": tickets_to_buy,
                                   "django_password": django_password})
    response = response.json()
    return response["message"]


@dataclass
class JackpotInfo:
    ticket_number: int
    user_tickets: int
    last_prize: int
    last_winner: str


async def jackpot_info(event: fbchat.MessageEvent) -> JackpotInfo:
    ticket_number = await handling_casino_sql.fetch_tickets_number()
    user_tickets = await handling_casino_sql.fetch_user_tickets(event.author.id)
    return JackpotInfo(ticket_number, user_tickets, last_jackpot_data.last_prize, last_jackpot_data.last_winner)


async def make_new_duel(duel_creator: str, wage: Decimal, opponent: str) -> str:
    duel_creator_money = await handling_casino_sql.fetch_user_money(duel_creator)
    try:
        duel_creator_money = Decimal(duel_creator_money)
    except ValueError:
        return duel_creator_money
    if duel_creator_money < wage:
        message = f"🚫 Nie masz wystarczająco monet (Posiadasz ich: {'%.2f' % duel_creator_money})"
    else:
        message, created = await handling_casino_sql.create_duel(duel_creator, wage, opponent)
        if created:
            duel_creator_money -= wage
            await handling_casino_sql.insert_into_user_money(duel_creator, duel_creator_money)
    return message


async def play_duel(accepting_person_fb_id: str) -> Tuple[str, Union[List[fbchat.Mention], None]]:
    mention = None
    accepting_person_fb_id_money = await handling_casino_sql.fetch_user_money(accepting_person_fb_id)
    try:
        accepting_person_fb_id_money = Decimal(accepting_person_fb_id_money)
    except ValueError:
        return accepting_person_fb_id_money, mention
    duel_data = await handling_casino_sql.fetch_duel_info(accepting_person_fb_id)
    if len(duel_data) == 0:
        message = "🚫 Nie masz żadnych zaproszeń do gry"
    else:
        wage, duel_creator, opponent = duel_data[0]
        if accepting_person_fb_id_money < wage:
            message = f"🚫 Nie masz wystarczająco pieniędzy (Stawka: {wage}, ty posiadasz {'%.2f' % accepting_person_fb_id_money} dogecoinów)"
        else:
            await handling_casino_sql.insert_into_user_money(accepting_person_fb_id,
                                                             accepting_person_fb_id_money-Decimal(wage))
            winner = rd.choice([duel_creator, opponent])
            winner_money = await handling_casino_sql.fetch_user_money(winner)
            winner_money += Decimal(wage*2)
            await handling_casino_sql.insert_into_user_money(winner, winner_money)
            message = f"✨ Osoba która wygrała {'%.2f' % float(wage*2)} dogecoinów"
            mention = [fbchat.Mention(thread_id=winner, offset=0, length=45)]
            await handling_casino_sql.delete_duels(duel_creator)
    return message, mention


async def discard_duel(fb_id: str) -> str:
    await handling_casino_sql.delete_duels(fb_id, True)
    return "💥 Usunięto twoje gry"


async def buy_scratch_card(event: fbchat.MessageEvent) -> str:
    response = requests.post("http://127.0.0.1:8000/casino/buy_scratch_card_fb",
                             data={"user_fb_id": event.author.id, "django_password": django_password})
    message = response.json()
    return message["message"]


async def shop(event: fbchat.MessageEvent, item_id: str) -> str:
    response = requests.post("http://127.0.0.1:8000/casino/shop_fb",
                             data={"user_fb_id": event.author.id, "django_password": django_password,
                                   "item_id": item_id})
    message = response.json()
    return message["message"]


async def make_slots_game(event: fbchat.MessageEvent) -> str:
    response = requests.post("http://127.0.0.1:8000/casino/slots_fb",
                             data={"user_fb_id": event.author.id, "django_password": django_password})
    message = response.json()
    return message["message"]


async def register(event: fbchat.MessageEvent, user: fbchat.UserData) -> str:
    response = requests.post("http://127.0.0.1:8000/casino/create_account",
                             data={"fb_name": user.name, "user_fb_id": event.author.id,
                                   "django_password": django_password})
    message = response.json()["message"]
    return message


async def connect_mail(event: fbchat.MessageEvent, email: str) -> str:
    response = requests.post("http://127.0.0.1:8000/casino/connect_mail_with_fb",
                             data={"django_password": django_password, "user_fb_id": event.author.id, "email": email})
    message = response.json()["message"]
    return message


async def get_spotify_data(event: fbchat.MessageEvent) -> str:
    response = requests.post("http://127.0.0.1:8000/casino/get_spotify_data",
                             data={"django_password": django_password, "user_fb_id": event.author.id})
    message = response.json()["message"]
    return message
