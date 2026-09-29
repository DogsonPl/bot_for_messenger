import random as rd
import requests
from decimal import Decimal, getcontext, ROUND_DOWN
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
        # todo messenger changed api, and no longer return mentions
        receiver_id = event.replied_to.author
        money_to_give = abs(Decimal(event.message.text.split()[1].replace(",", ".")))
        money_to_give = money_to_give.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        if money_to_give <= 0:
            raise ValueError
    except Exception:
        return "🚫 Dzialanie komendy: !tip liczba_monet.\nFacebook namieszal w swoim api, wiec teraz trzeba odpowiedziec na wiadomosc osoby, ktora chce sie obdarowac dogami"

    if await handling_casino_sql.transfer_money(event.author.id, receiver_id, money_to_give):
        return f"✅ Wysłano {money_to_give} do drugiej osoby :)"
    return ("🚫 Nie masz wystarczająco pieniędzy, nie jesteś zarejestrowany, "
            "albo osoba której chcesz dać dogi nie użyła nigdy komendy !register")


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
    try:
        wage = Decimal(wage).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        if wage <= 0:
            raise ValueError
    except Exception:
        return "🚫 Stawka musi być dodatnią liczbą"

    status = await handling_casino_sql.create_duel_paid(duel_creator, wage, opponent)
    if status == "ok":
        return "🕛 Oczekiwanie na akceptacje gry... (twój przeciwnik musi wpisać !duel akceptuj)"
    if status == "no_money":
        return "🚫 Nie masz wystarczająco monet albo nie jesteś zarejestrowany (użyj !register)"
    return """🚫 Możesz tworzyć jedną grę jednocześnie, jeśli chcesz ją anulować napisz !duel odrzuć. 
Również osoba z która chcesz grać nie może mieć żadnych gier w trakcie"""


async def play_duel(accepting_person_fb_id: str) -> Tuple[str, Union[List[fbchat.Mention], None]]:
    status, wage, winner = await handling_casino_sql.settle_duel(
        accepting_person_fb_id, lambda creator, opponent: rd.choice([creator, opponent]))

    if status == "no_duel":
        return "🚫 Nie masz żadnych zaproszeń do gry", None
    if status == "no_money":
        return f"🚫 Nie masz wystarczająco pieniędzy albo nie jesteś zarejestrowany (Stawka: {wage})", None

    message = f"✨ Osoba która wygrała {'%.2f' % float(wage * 2)} dogecoinów"
    mention = [fbchat.Mention(thread_id=winner, offset=0, length=45)]
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
