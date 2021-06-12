import requests
from decimal import Decimal, getcontext
from bs4 import BeautifulSoup
from .sql import handling_casino_sql
from .parse_config import django_password


getcontext().prec = 20

DJANGO_PASSWORD = django_password


async def take_daily(event):
    response = requests.post("http://127.0.0.1:8000/casino/set_daily_fb",
                             data={"fb_user_id": event.author.id, "django_password": django_password})
    message = response.json()
    return message["message"]


async def make_bet(event):
    message_values = event.message.text.split()
    try:
        bet_money = abs(float(message_values[1]))
        percent_to_win = abs(int(message_values[2]))
    except (ValueError, IndexError):
        return "🚫 Wygląd komendy: !bet x y, gdzie x to liczba monet które obstawiasz a y to % na wygraną"

    response = requests.post("http://127.0.0.1:8000/casino/bet_fb",
                             data={"fb_user_id": event.author.id, "bet_money": bet_money,
                                   "percent_to_win": percent_to_win, "django_password": django_password})
    response = response.json()
    message = BeautifulSoup(response["message"], "html.parser")
    return message.text


async def make_tip(event):
    try:
        mention = event.message.mentions[0]
        money_to_give = abs(float(event.message.text.split()[1]))
    except (IndexError, ValueError, TypeError):
        return "🚫 Wygląd komendy: !tip liczba_monet oznaczenie_osoby"

    sender_money = await handling_casino_sql.fetch_user_money(event.author.id)
    try:
        if sender_money < money_to_give:
            return "🚫 Nie masz wystarczająco pieniędzy"
    except TypeError:
        return "💡 Użyj polecenia !register żeby móc się bawić w kasyno. Wszystkie dogecoiny są sztuczne"

    receiver_money = await handling_casino_sql.fetch_user_money(mention.thread_id)
    try:
        receiver_money += Decimal(money_to_give)
    except TypeError:
        return "🚫 Osoba której chcesz dać dogi nie użyła nigdy komendy register"
    sender_money -= Decimal(money_to_give)
    await handling_casino_sql.insert_into_user_money(event.author.id, sender_money)
    await handling_casino_sql.insert_into_user_money(int(mention.thread_id), receiver_money)
    return f"✅ Wysłano {money_to_give} do drugiej osoby :)"


async def buy_jackpot_ticket(event):
    try:
        tickets_to_buy = abs(int(event.message.text.split()[1]))
    except (IndexError, ValueError, TypeError):
        return "🚫 Wygląd komendy: !jackpotbuy liczba_biletów"
    response = requests.post("http://127.0.0.1:8000/casino/jackpot_buy_fb",
                             data={"user_fb_id": event.author.id, "tickets": tickets_to_buy,
                                   "django_password": django_password})
    response = response.json()
    return response["message"]


async def jackpot_info(event):
    ticket_number = await handling_casino_sql.fetch_tickets_number()
    user_tickets = await handling_casino_sql.fetch_user_tickets(event.author.id)
    last_jackpot_data = await handling_casino_sql.get_last_jackpot_results()
    last_winner = last_jackpot_data[0] if last_jackpot_data[0] else last_jackpot_data[1]
    last_prize = last_jackpot_data[2]
    return ticket_number, user_tickets, last_prize, last_winner
