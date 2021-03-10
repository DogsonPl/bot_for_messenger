from python_scripts import sql_actions
from python_scripts.sending_actions import send_text_message, send_text_message_with_reply
import random as rd


@send_text_message_with_reply
async def give_user_daily_money(event):
    try:
        async with sql_actions.GetInfoFromDatabase() as db:
            await db.fetch_info_if_user_got_today_daily(event.author.id)
            got_daily = db.data[0][0]
            strike = db.data[0][1]
    except IndexError:
        got_daily = 0
        strike = 1

    if got_daily == 1:
        return "Odebrałeś już dzisiaj daily"

    coins_to_give = 10+strike
    async with sql_actions.InsertIntoDatabase() as db:
        await db.insert_into_daily(event.author.id)
        await db.insert_into_daily_strike(event.author.id, strike+1)
    money = await get_user_money(event.author.id)
    await insert_into_user_money(event.author.id, coins_to_give+money)
    return f"Dostałeś właśnie darmowe {coins_to_give} dogecoinów. Jest to twoje {strike} daily z rzędu"


@send_text_message_with_reply
async def bet(event):
    message_values = event.message.text.split()
    try:
        percent_to_win = float(message_values[2])
        bet_money = float(message_values[1])
    except (ValueError, IndexError):
        return "Wygląd komendy: !bet x y, gdzie x to liczba monet które obstawiasz a y to % na wygraną"
    if percent_to_win < 1 or percent_to_win > 90:
        return "Możesz mieć od 1% do 90% na wygraną"
    if bet_money < 0:
        return "Nie możesz obstawiać dogecoinów na minusie"

    current_money = await get_user_money(event.author.id)
    if current_money < bet_money:
        return "Nie masz wystarczająco dogecoinów"

    lucky_number = rd.SystemRandom().random()*100
    if lucky_number >= percent_to_win:
        current_money = current_money - bet_money
        message = f"Przegrałeś {bet_money} dogecoinów\nMasz ich obecnie {'%.2f' % current_money}\nWylosowana liczba: {'%.1f' % lucky_number}"
    else:
        won_money = ((bet_money/(percent_to_win/100))-bet_money)*0.99
        current_money += won_money
        message = f"Wygrałeś {'%.2f' % won_money} dogecoinów\nMasz ich obecnie {'%.2f' % current_money}\nWylosowana liczba: {'%.1f' % lucky_number}"
    await insert_into_user_money(event.author.id, current_money)
    return message


@send_text_message_with_reply
async def send_user_money(event):
    user_money = await get_user_money(event.author.id)
    return f"Posiadasz obecnie {'%.2f' % user_money} dc"


@send_text_message_with_reply
async def tip(event):
    try:
        mention = event.message.mentions[0]
        money_to_give = float(event.message.text.split()[1])
    except (IndexError, ValueError, TypeError):
        return "Wygląd komendy: !tip liczba_monet oznaczenie_osoby"

    sender_money = await get_user_money(event.author.id)
    if sender_money < money_to_give:
        return "Nie masz wystarczająco pieniędzy"

    receiver_money = await get_user_money(mention.thread_id)
    receiver_money += money_to_give
    sender_money -= money_to_give
    await insert_into_user_money(event.author.id, sender_money)
    await insert_into_user_money(int(mention.thread_id), receiver_money)
    return f"Wysłaleś {money_to_give} do drugiej osoby :)"


@send_text_message
async def get_top_players(event, client):
    message = "3 użytkowników z najwiekszą liczbą dogecoinów:\n"
    try:
        async with sql_actions.GetInfoFromDatabase() as db:
            await db.fetch_top_three_players()
            top_users = db.data
    except IndexError:
        return "Brak danych"
    for i in top_users:
        user_info = await client.fetch_thread_info([str(i[0])]).__anext__()
        message += user_info.name + f": {'%.2f' % i[1]} dc\n"
    return message


async def get_user_money(person_id):
    try:
        async with sql_actions.GetInfoFromDatabase() as db:
            await db.fetch_user_money(person_id)
            user_money = db.data[0][0]
    except IndexError:
        user_money = 0
    if user_money is None:
        user_money = 0
    return user_money


async def insert_into_user_money(person_id, money):
    async with sql_actions.InsertIntoDatabase() as db:
        await db.insert_into_user_money(person_id, money)
