import requests
import json
import bisect
import random as rd
from decimal import Decimal, getcontext
from bs4 import BeautifulSoup
import aiofiles
from .sql import handling_casino_sql


getcontext().prec = 20

NO_ACCOUNT_MESSAGE = "💡 Użyj polecenia !register żeby móc się bawić w kasyno. Wszystkie dogecoiny są sztuczne"


async def take_daily(event):
    response = requests.post("http://127.0.0.1:8000/casino/set_daily_fb", data={"fb_user_id": event.author.id})
    message = response.json()
    return message["message"]


async def make_bet(event):
    message_values = event.message.text.split()
    try:
        bet_money = abs(float(message_values[1]))
        percent_to_win = abs(int(message_values[2]))
    except (ValueError, IndexError):
        return "🚫 Wygląd komendy: !bet x y, gdzie x to liczba monet które obstawiasz a y to % na wygraną"
    if not 1 <= percent_to_win <= 90:
        return "🚫 Możesz mieć od 1% do 90% na wygraną"
    response = requests.post("http://127.0.0.1:8000/casino/bet_fb",
                             data={"fb_user_id": event.author.id, "bet_money": bet_money, "percent_to_win": percent_to_win})
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
        return NO_ACCOUNT_MESSAGE

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
    return "Ta komenda działa obecnie tylko na https://dogson.ovh"
    """ try:
        tickets_to_buy = abs(int(event.message.text.split()[1]))
    except (IndexError, ValueError, TypeError):
        return "🚫 Wygląd komendy: !jackpotbuy liczba_biletów"
    money = await handling_casino_sql.fetch_user_money(event.author.id)

    try:
        if money < tickets_to_buy:
            return "🚫 Nie masz wystarczająco pieniędzy"
    except TypeError:
        return NO_ACCOUNT_MESSAGE

    tickets = await handling_casino_sql.fetch_user_tickets(event.author.id)
    tickets += tickets_to_buy
    await handling_casino_sql.insert_into_user_money(event.author.id, money-tickets_to_buy)
    await handling_casino_sql.add_jackpot_tickets(event.author.id, tickets)
    return f"✅ Kupiono {tickets_to_buy} biletów"
    """


async def jackpot_info(event):
    return "Ta komenda działa obecnie tylko na https://dogson.ovh", "", "", ""
    """
    ticket_number = await handling_casino_sql.fetch_tickets_number()
    user_tickets = await handling_casino_sql.fetch_user_tickets(event.author.id)
    last_jackpot_results = await get_last_jackpot_results()
    last_prize = last_jackpot_results["last_prize"]
    last_winner = last_jackpot_results["last_winner"]
    return ticket_number, user_tickets, last_prize, last_winner
    """


class DrawJackpotWinner:
    @staticmethod
    async def draw_jackpot_winner():
        users, tickets = zip(*await handling_casino_sql.fetch_all_jackpot_data_to_make_draw())
        total = 0
        try:
            weights = [total := total + i for i in tickets]
        except SyntaxError:
            raise SyntaxError("To run this function, you have to update your python version to 3.8+")
        random = rd.random()*total
        winner_index = bisect.bisect(weights, random)
        winner_id = users[winner_index]
        await save_jackpot_results({"last_winner": winner_id, "last_prize": total})
        user_money = await handling_casino_sql.fetch_user_money(winner_id)
        await handling_casino_sql.insert_into_user_money(winner_id, user_money+total)


LAST_JACKPOT_RESULTS_FILE_PATH = "Bot//data//last_jackpot_results.json"


async def save_jackpot_results(data):
    async with aiofiles.open(LAST_JACKPOT_RESULTS_FILE_PATH, "w") as file:
        await file.write(json.dumps(data))


async def get_last_jackpot_results():
    async with aiofiles.open(LAST_JACKPOT_RESULTS_FILE_PATH, "r") as file:
        data = json.loads(await file.read())
        return data
