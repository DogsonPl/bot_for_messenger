from Bot.handling_sql_actions import *
import random as rd


async def take_daily(event):
    got_daily, strike = await check_daily(event.author.id)
    if got_daily == 1:
        return "Odebrałeś już dzisiaj daily"

    coins_to_give = 10 + strike
    await insert_into_daily(event.author.id, strike + 1, coins_to_give)
    return f"Dostałeś właśnie darmowe {coins_to_give} dogecoinów. Jest to twoje {strike} daily z rzędu"


async def make_bet(event):
    message_values = event.message.text.split()
    try:
        percent_to_win = float(message_values[2])
        bet_money = abs(float(message_values[1]))
    except (ValueError, IndexError):
        return "Wygląd komendy: !bet x y, gdzie x to liczba monet które obstawiasz a y to % na wygraną"
    if percent_to_win < 1 or percent_to_win > 90:
        return "Możesz mieć od 1% do 90% na wygraną"

    current_money = await get_user_money(event.author.id)
    if current_money < bet_money:
        return "Nie masz wystarczająco dogecoinów"

    lucky_number = rd.SystemRandom().random() * 100
    if lucky_number >= percent_to_win:
        current_money = current_money - bet_money
        message = f"Przegrałeś {bet_money} dogecoinów\nMasz ich obecnie {'%.2f' % current_money}\nWylosowana liczba: {'%.1f' % lucky_number}"
    else:
        won_money = ((bet_money / (percent_to_win / 100)) - bet_money)*0.99
        current_money += won_money
        message = f"Wygrałeś {'%.2f' % won_money} dogecoinów\nMasz ich obecnie {'%.2f' % current_money}\nWylosowana liczba: {'%.1f' % lucky_number}"
    await insert_into_user_money(event.author.id, current_money)
    return message


async def make_tip(event):
    try:
        mention = event.message.mentions[0]
        money_to_give = abs(float(event.message.text.split()[1]))
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
