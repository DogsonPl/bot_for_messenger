from ..bot_actions import BotActions
from .. import casino_actions
from ..sql import handling_casino_sql

MEDALS = ["🥇", "🥈", "🥉"]


class CasinoCommands(BotActions):
    def __init__(self, loop, bot_id, client):
        super().__init__(loop, bot_id, client)

    async def send_daily_money_message(self, event):
        message = await casino_actions.take_daily(event)
        await self.send_message_with_reply(event, message)

    async def send_bet_message(self, event):
        message = await casino_actions.make_bet(event)
        await self.send_message_with_reply(event, message)

    async def send_user_money(self, event):
        user_money = await handling_casino_sql.fetch_user_money(event.author.id)
        await self.send_message_with_reply(event, f"🏦 Posiadasz obecnie {'%.2f' % user_money} dc")

    async def send_tip_message(self, event):
        message = await casino_actions.make_tip(event)
        await self.send_message_with_reply(event, message)

    async def send_top_players(self, event):
        message = "3 użytkowników z najwiekszą liczbą dogecoinów:\n"
        top_users = await handling_casino_sql.fetch_top_three_players()
        for user, medal in zip(top_users, MEDALS):
            user_info = await self.get_thread_info(str(user[0]))
            message += f"{medal} {user_info.name}: {int(user[1])} dc\n"
        await self.send_text_message(event, message)

    async def send_jackpot_info(self, event):
        ticket_number, user_tickets, last_prize, last_winner = await casino_actions.jackpot_info(event)
        last_winner = await self.get_thread_info(last_winner)
        message = f"""🎫 Ogólna liczba kupionych biletów: {ticket_number}
        🎫 Twoja liczba biletów: {user_tickets}
        🎟 Ostatnio {last_prize} dogecoinów wygrał {last_winner.name} 

        📑 Zasady:
        -każdy bilet kosztuje 1 dogecoin
        -jeden bilet to jeden los
        -na końcu dnia jest losowanie, osoba której bilet zostanie wylosowany wygrywa dogecoiny (każdy kupiony bilet zwiększa pule nagród o jeden dogecoin)"""
        await self.send_text_message(event, message)

    async def send_jackpot_ticket_bought_message(self, event):
        message = await casino_actions.buy_jackpot_ticket(event)
        await self.send_text_message(event, message)
