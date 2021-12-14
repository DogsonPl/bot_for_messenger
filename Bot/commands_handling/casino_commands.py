from math import floor
import requests

from ..parse_config import django_password
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
        user_money, legendary_dogecoins = await handling_casino_sql.fetch_user_all_money(event.author.id)
        try:
            user_money_formatted = floor(user_money*100)/100
            legendary_dogecoins_formatted = floor(legendary_dogecoins*100)/100
            message = f"""🏦 Posiadasz obecnie:
{user_money_formatted} dogecoinów
{legendary_dogecoins_formatted} legendarnych dogecoinów

💡 Co miesiąc (pierwszego dnia każdego miesiąca) wszystkie dogi powyżej 100 są zamieniane w legendarne dogi, codziennie traci się 1% dogów

🔗 coordinated by: https://dogson.ovh, więcej informacji po użyciu komendy !strona"""
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
        top_users, top_legendary_users = await handling_casino_sql.fetch_top_three_players()
        for user, medal in zip(top_users, MEDALS):
            username = user[1] if user[1] else user[0]
            message += f"{medal} {username}: {int(user[2])} dc\n"

        message += "\n3 użytkowników z największą ilością legendarnych dogecoinów:\n"
        for user, medal in zip(top_legendary_users, MEDALS):
            username = user[1] if user[1] else user[0]
            message += f"{medal} {username}: {int(user[2])} dc\n"

        message += "\n🔗 coordinated by: https://dogson.ovh, więcej informacji po użyciu komendy !strona"
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
        response = requests.post("http://127.0.0.1:8000/casino/create_account",
                                 data={"fb_name": name.name, "user_fb_id": event.author.id, "django_password": django_password})
        message = response.json()["message"]
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
    async def send_player_profil(self, event):
        won_bets, lost_bets, today_scratch_bought, best_season, biggest_win, last_season_dogecoins, total_scratch_bought, season_first_place, season_second_place, season_third_place, won_dc, lost_dc = await handling_casino_sql.fetch_user_profil_data(event.author.id)
        total_bets = lost_bets+won_bets
        legendary_dogecoins_gained = 0
        if last_season_dogecoins > 100:
            legendary_dogecoins_gained = last_season_dogecoins-100
        won_bets_percent = str((won_bets/total_bets)*100)[0:5]
        message = f"""👤 Profil (komenda w trakcie tworzenia)
        
🏆 Twoje osiągiecia: soon

📈 Wygrano łącznie {'%.2f' % won_dc} dogecoinów
📉 Przegrano łącznie {'%.2f' % lost_dc} dogecoinów
🔝 Twoja największa wygrana w becie: {float('%.2f' % biggest_win)}

🤑 Wykonałeś łącznie {total_bets} betów, w tym {won_bets} wygranych ({won_bets_percent} %)
💰 Kupiono łącznie {total_scratch_bought} zdrapek, dzisiaj {today_scratch_bought} zdrapek

💲 Twoja ilość dogów na koniec poprzedniego sezonu: {float('%.2f' % last_season_dogecoins)} (otrzymano {float('%.2f' % legendary_dogecoins_gained)} legendarnych dogów)
🎖️ Twój najlepszy sezon: {float('%.2f' % best_season)} dogów

👑 Na koniec sezonu byłeś:
🥇 {season_first_place} razy
🥈 {season_second_place} razy
🥉 {season_third_place} razy"""

        await self.send_message_with_reply(event, message)


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
