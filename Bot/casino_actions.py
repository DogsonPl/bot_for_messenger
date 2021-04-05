from Bot.handling_sql import *
import secrets


async def take_daily(event):
    got_daily, strike = await check_daily(event.author.id)
    if got_daily == 1:
        return "🚫 Odebrano już dzisiaj daily"

    try:
        coins_to_give = 10 + (strike/10)
    except TypeError:
        coins_to_give = 11
        strike = 0
    await insert_into_daily(event.author.id, strike + 1, coins_to_give)
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

    current_money = await get_user_money(event.author.id)
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
    await insert_into_user_money(event.author.id, current_money)
    return message


async def make_tip(event):
    try:
        mention = event.message.mentions[0]
        money_to_give = abs(float(event.message.text.split()[1]))
    except (IndexError, ValueError, TypeError):
        return "🚫 Wygląd komendy: !tip liczba_monet oznaczenie_osoby"

    sender_money = await get_user_money(event.author.id)
    if sender_money < money_to_give:
        return "🚫 Nie masz wystarczająco pieniędzy"

    receiver_money = await get_user_money(mention.thread_id)
    receiver_money += money_to_give
    sender_money -= money_to_give
    await insert_into_user_money(event.author.id, sender_money)
    await insert_into_user_money(int(mention.thread_id), receiver_money)
    return f"✅ Wysłano {money_to_give} do drugiej osoby :)"


async def buy_jackpot_ticket(event):
    try:
        tickets_to_buy = abs(int(event.message.text.split()[1]))
    except (IndexError, ValueError, TypeError):
        return "🚫 Wygląd komendy: !jackpotbuy liczba_biletów"
    money = await get_user_money(event.author.id)
    if money < tickets_to_buy:
        return "🚫 Nie masz wystarczająco pieniędzy"
    tickets = await get_user_tickets(event.author.id)
    tickets += tickets_to_buy
    await insert_into_user_money(event.author.id, money-tickets_to_buy)
    await insert_into_user_tickets(event.author.id, tickets)
    return f"✅ Kupiono {tickets_to_buy} biletów"


async def jackpot_info(event):
    ticket_number = await get_tickets_number()
    user_tickets = await get_user_tickets(event.author.id)
    return f"""Ogólna liczba kupionych biletów: {ticket_number}
Twoja liczba biletów: {user_tickets}

Zasady:
-każdy bilet kosztuje 1 dogecoin
-jeden bilet to jeden los
-na końcu dnia jest losowanie, osoba której bilet zostanie wylosowany wygrywa dogecoiny (każdy kupiony bilet zwiększa pule nagród o jeden dogecoin)"""
