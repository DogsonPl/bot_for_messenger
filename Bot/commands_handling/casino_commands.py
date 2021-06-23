from .logger import logger
from ..bot_actions import BotActions
from .. import casino_actions
from ..sql import handling_casino_sql
from ..sending_emails import smpt_connection, get_confirmation_code

MEDALS = ["🥇", "🥈", "🥉"]


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
            await self.send_message_with_reply(event, f"🏦 Posiadasz obecnie {'%.2f' % user_money} dc")
        except TypeError:
            await self.send_message_with_reply(event, user_money)

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
    async def register(self, event):
        name = await self.get_thread_info(event.author.id)
        message = await handling_casino_sql.register_casino_user(event.author.id, name.name)
        await self.send_message_with_reply(event, message)

    @logger
    async def get_email(self, event):
        try:
            user_email, = await handling_casino_sql.get_user_email(event.author.id)
        except ValueError:
            user_email = None
        if user_email is not None:
            await self.send_text_message(event, f"📧 Twój email to {user_email}")
            return

        try:
            email = event.message.text.split()[1]
        except IndexError:
            await self.send_text_message(event, "🚫 Po !email podaj swojego maila")
            return

        confirmation_code = await get_confirmation_code()
        user_send_mail_in_last_hour = await handling_casino_sql.new_email_confirmation(event.author.id, email,
                                                                                       confirmation_code)
        if user_send_mail_in_last_hour:
            await self.send_text_message(event, "🚫 Możesz poprosić o jednego maila w ciągu godziny")
        else:
            email_message = await smpt_connection.create_message(email, confirmation_code)
            message = await smpt_connection.send_mail(email, email_message)
            await self.send_text_message(event, message)

    @logger
    async def check_email_verification_code(self, event):
        try:
            code = event.message.text.split()[1]
            message = await handling_casino_sql.check_email_confirmation(event.author.id, code)
            await self.send_text_message(event, message)
        except IndexError:
            await self.send_text_message(event, "🚫 Po !kod napisz kod którego dostałeś na maila")

    @logger
    async def send_player_stats(self, event):
        won_bets, lost_bets = await handling_casino_sql.fetch_user_stats(event.author.id)
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
🕹 Stosunek wygrane/przegrane bety: {win_ratio_formatted}"""
        await self.send_text_message(event, message)
