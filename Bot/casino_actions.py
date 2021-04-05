import secrets
import json
import bisect
import random as rd
import aiofiles
from .sql import handling_casino_sql


async def take_daily(event):
    got_daily, strike = await handling_casino_sql.fetch_info_if_user_got_today_daily(event.author.id)
    if got_daily == 1:
        return "🚫 Odebrano już dzisiaj daily"

    try:
        coins_to_give = 10 + (strike/10)
    except TypeError:
        coins_to_give = 11
        strike = 0
    await handling_casino_sql.insert_into_daily(event.author.id, strike + 1, coins_to_give)
    return f"✅ Otrzymano właśnie darmowe {coins_to_give} dogecoinów. Jest to twoje {strike} daily z rzędu"


async def make_bet(event):
    message_values = event.message.text.split()
    try:
        percent_to_win = float(message_values[2])
        bet_money = abs(float(message_values[1]))
    except (ValueError, IndexError):
        return "🚫 Wygląd komendy: !bet x y, gdzie x to liczba monet które obstawiasz a y to % na wygraną"
    if not 1 <= percent_to_win <= 90:
        return "🚫 Możesz mieć od 1% do 90% na wygraną"

    current_money = await handling_casino_sql.fetch_user_money(event.author.id)
    if current_money < bet_money:
        return "🚫 Nie masz wystarczająco dogecoinów"

    lucky_number = secrets.randbelow(101)
    if lucky_number >= percent_to_win:
        current_money = current_money - bet_money
        message = f"📉 Przegrano {bet_money} dogecoinów\nMasz ich obecnie {'%.2f' % current_money}\nWylosowana liczba: {lucky_number}"
    else:
        won_money = ((bet_money / (percent_to_win / 100)) - bet_money)*0.99
        current_money += won_money
        message = f"📈 Wygrano {'%.2f' % won_money} dogecoinów\nMasz ich obecnie {'%.2f' % current_money}\nWylosowana liczba: {lucky_number}"
    await handling_casino_sql.insert_into_user_money(event.author.id, current_money)
    return message


async def make_tip(event):
    try:
        mention = event.message.mentions[0]
        money_to_give = abs(float(event.message.text.split()[1]))
    except (IndexError, ValueError, TypeError):
        return "🚫 Wygląd komendy: !tip liczba_monet oznaczenie_osoby"

    sender_money = await handling_casino_sql.fetch_user_money(event.author.id)
    if sender_money < money_to_give:
        return "🚫 Nie masz wystarczająco pieniędzy"

    receiver_money = await handling_casino_sql.fetch_user_money(mention.thread_id)
    receiver_money += money_to_give
    sender_money -= money_to_give
    await handling_casino_sql.insert_into_user_money(event.author.id, sender_money)
    await handling_casino_sql.insert_into_user_money(int(mention.thread_id), receiver_money)
    return f"✅ Wysłano {money_to_give} do drugiej osoby :)"


async def buy_jackpot_ticket(event):
    try:
        tickets_to_buy = abs(int(event.message.text.split()[1]))
    except (IndexError, ValueError, TypeError):
        return "🚫 Wygląd komendy: !jackpotbuy liczba_biletów"
    money = await handling_casino_sql.fetch_user_money(event.author.id)
    if money < tickets_to_buy:
        return "🚫 Nie masz wystarczająco pieniędzy"
    tickets = await handling_casino_sql.fetch_user_tickets(event.author.id)
    tickets += tickets_to_buy
    await handling_casino_sql.insert_into_user_money(event.author.id, money-tickets_to_buy)
    await handling_casino_sql.add_jackpot_tickets(event.author.id, tickets)
    return f"✅ Kupiono {tickets_to_buy} biletów"


async def jackpot_info(event):
    ticket_number = await handling_casino_sql.fetch_tickets_number()
    user_tickets = await handling_casino_sql.fetch_user_tickets(event.author.id)
    last_jackpot_results = await get_last_jackpot_results()
    last_prize = last_jackpot_results["last_prize"]
    last_winner = last_jackpot_results["last_winner"]
    return f"""Ogólna liczba kupionych biletów: {ticket_number}
Twoja liczba biletów: {user_tickets}
Ostatnio {last_prize} dogecoinów wygrał {last_winner} 

Zasady:
-każdy bilet kosztuje 1 dogecoin
-jeden bilet to jeden los
-na końcu dnia jest losowanie, osoba której bilet zostanie wylosowany wygrywa dogecoiny (każdy kupiony bilet zwiększa pule nagród o jeden dogecoin)"""


async def draw_jackpot_winner():
    users, tickets = zip(*await handling_casino_sql.fetch_all_jackpot_data_to_make_draw())
    total = 0
    try:
        weights = [total := total + i for i in tickets]
    except SyntaxError:
        raise Exception("To run this function, you have to update your python version to 3.8+")
    random = rd.random()*total
    winner_index = bisect.bisect(weights, random)
    winner_id = users[winner_index]
    await save_jackpot_results({"last_winner": winner_id, "last_prize": total})
    user_money = await handling_casino_sql.fetch_user_money(winner_id)
    await handling_casino_sql.insert_into_user_money(winner_id, user_money+total)


async def save_jackpot_results(data):
    async with aiofiles.open("Bot//data//last_jackpot_results.json", "w") as file:
        await file.write(json.dumps(data))


async def get_last_jackpot_results():
    async with aiofiles.open("Bot//data//last_jackpot_results.json", "r") as file:
        data = json.loads(await file.read())
        return data
