from math import floor

from .logger import logger
from ..bot_actions import BotActions
from .. import casino_actions
from ..sql import handling_casino_sql
from ..sending_emails import smpt_connection, get_confirmation_code

MEDALS = ["🥇", "🥈", "🥉"]
DUEL_HELP_MESSAGE = """💡 Użycie komendy:
!duel x @oznaczenie - wyzywasz na pojedynek oznaczoną osobę o x monet 
!duel akceptuj - akcpetuje zaproszenie do gry
!duel odrzuć - odrzucza twoje zaproszenia do gry
"""


class CasinoCommands(BotActions):
    def __init__(self, loop, bot_id, client):
        super().__init__(loop, bot_id, client)

    @logger
    async def send_daily_money_message(self, event):
        message = await casino_actions.take_daily(event)
        await self.send_message_with_reply(event, message)

    @logger
    async def send_bet_message(self, event):
        message = await casino_actions.make_bet(event)
        await self.send_message_with_reply(event, message)

    @logger
    async def send_user_money(self, event):
        user_money = await handling_casino_sql.fetch_user_money(event.author.id)
        try:
            user_money_formatted = floor(user_money*100)/100
            message = f"🏦 Posiadasz obecnie {user_money_formatted} dc"
        except TypeError:
            message = user_money

        await self.send_message_with_reply(event, message)

    @logger
    async def send_tip_message(self, event):
        message = await casino_actions.make_tip(event)
        await self.send_message_with_reply(event, message)

    @logger
    async def send_top_players(self, event):
        message = "3 użytkowników z najwiekszą liczbą dogecoinów:\n"
        top_users = await handling_casino_sql.fetch_top_three_players()
        for user, medal in zip(top_users, MEDALS):
            username = user[1] if user[1] else user[0]
            message += f"{medal} {username}: {int(user[2])} dc\n"
        await self.send_text_message(event, message)

    @logger
    async def send_jackpot_info(self, event):
        ticket_number, user_tickets, last_prize, last_winner = await casino_actions.jackpot_info(event)
        message = f"""🎫 Ogólna liczba kupionych biletów: {ticket_number}
🎫 Twoja liczba biletów: {user_tickets}
🎟 Ostatnio {last_prize} dogecoinów wygrał {last_winner}

📑 Zasady:
-każdy bilet kosztuje 1 dogecoin
-jeden bilet to jeden los
-na końcu dnia jest losowanie, osoba której bilet zostanie wylosowany wygrywa dogecoiny (każdy kupiony bilet zwiększa pule nagród o jeden dogecoin)"""
        await self.send_text_message(event, message)

    @logger
    async def send_jackpot_ticket_bought_message(self, event):
        message = await casino_actions.buy_jackpot_ticket(event)
        await self.send_text_message(event, message)

    @logger
    async def send_scratch_card_message(self, event):
        message = await casino_actions.buy_scratch_card(event)
        await self.send_message_with_reply(event, message)

    @logger
    async def register(self, event):
        name = await self.get_thread_info(event.author.id)
        message = await handling_casino_sql.register_casino_user(event.author.id, name.name)
        await self.send_message_with_reply(event, message)

    @logger
    async def get_email(self, event):
        user_email = await handling_casino_sql.get_user_email(event.author.id)
        if user_email is None:
            message = await send_confirmation_email(event)
        elif user_email is False:
            message = "🚨 Te konto było już używane i dane zostały przeniesione na inne konto, jeśli chcesz znowu grać na tym koncie napisz do !tworca"
        else:
            message = f"""📧 Twój email to {user_email}
Jeśli jeszcze tego nie zrobiłeś, możesz połączyć swoje dane z kasyna ze stroną (komenda !strona) zakładając konto używająć tego samego maila"""
        await self.send_text_message(event, message)

    @logger
    async def check_email_verification_code(self, event):
        try:
            code = event.message.text.split()[1]
            message = await handling_casino_sql.check_email_confirmation(event.author.id, code)
        except IndexError:
            message = "🚫 Po !kod napisz kod którego dostałeś na maila"
        await self.send_text_message(event, message)

    @logger
    async def send_duel_message(self, event):
        mention = None
        args = event.message.text.split()[1:]
        if len(args) == 0:
            message = DUEL_HELP_MESSAGE
        else:
            if args[0] == "akceptuj":
                message, mention = await casino_actions.play_duel(event.author.id)
            elif args[0].replace("ć", "c") == "odrzuc":
                message = await casino_actions.discard_duel(event.author.id)
            else:
                try:
                    wage = abs(float(args[0]))
                    opponent = event.message.mentions[0].thread_id
                except(ValueError, IndexError):
                    message = DUEL_HELP_MESSAGE
                else:
                    message = await casino_actions.make_new_duel(event.author.id, wage, opponent)
        await self.send_text_message_with_mentions(event, message, mention)

    @logger
    async def send_player_stats(self, event):
        won_bets, lost_bets, today_won_money, today_lost_money, scratch_profit, today_scratch_bought = await handling_casino_sql.fetch_user_stats(event.author.id)
        try:
            win_ratio = str(won_bets / lost_bets)
        except TypeError:
            message = "💡 Użyj polecenia !register żeby móc się bawić w kasyno. Wszystkie dogecoiny są sztuczne"
        except ZeroDivisionError:
            message = "🚫 Nie wykonałeś/aś jeszcze żadnych betów. Użyj komendy !bet"
        else:
            bets_num = won_bets+lost_bets
            win_ratio_formatted, dec = win_ratio.split(".")
            win_ratio_formatted += "."
            if dec.startswith("0"):
                win_ratio_formatted += dec[:4]
            else:
                for i in dec[:4]:
                    win_ratio_formatted += i
                    if i == 0:
                        break
            message = f"""🔢 Wykonałeś/aś obecnie: {bets_num} betów
📈 Wygrałeś/aś: {won_bets} razy
📉 Przegrałeś/aś: {lost_bets} razy
🕹 Stosunek wygrane/przegrane bety: {win_ratio_formatted}

🟩 Wygrane dogecoiny dzisiaj: {'%.2f' % today_won_money}
🟥 Przegrane dogecoiny dzisiaj: {'%.2f' % today_lost_money}
💲 Dzisiejszy profit w betowaniu: {'%.2f' % (today_won_money+today_lost_money)}

💥 Dzisiaj kupiłeś/aś: {today_scratch_bought} zdrapek
💲 Profit na zdrapkach: {scratch_profit}
"""
        await self.send_text_message(event, message)


async def send_confirmation_email(event):
    try:
        email = event.message.text.split()[1]
    except IndexError:
        return "🚫 Jeśli chcesz ustawić swojego maila żeby mieć możliwość synchronizacji danych ze stroną, po !email podaj swojego maila"

    confirmation_code = await get_confirmation_code()
    user_send_mail_in_last_hour = await handling_casino_sql.new_email_confirmation(event.author.id, email,
                                                                                   confirmation_code)
    if user_send_mail_in_last_hour:
        return "🚫 Możesz poprosić o jednego maila w ciągu godziny"
    else:
        email_message = await smpt_connection.create_message(email, confirmation_code)
        return await smpt_connection.send_mail(email, email_message)
