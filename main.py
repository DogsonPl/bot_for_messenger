import asyncio
import json
import time
import re

import fbchat

from Bot.parse_config import get_login_data
from Bot.commands_handling.normal_commands import Commands
from Bot.commands_handling.casino_commands import CasinoCommands
from Bot.commands_handling.group_commands import GroupCommands
from Bot import task_scheduler

# works only on linux


class BotCore:
    COOKIES_FILE_PATH = "cookies.json"

    def __init__(self):
        self.session = None
        self.client = None
        self.bot_id = None
        try:
            with open(self.COOKIES_FILE_PATH, "r") as cookies_file:
                self.cookies = json.load(cookies_file)
        except FileNotFoundError:
            self.cookies = None

    async def login(self):
        print("Login in...")
        try:
            self.session = await fbchat.Session.from_cookies(self.cookies)
            print("Logged using cookies")
        except (fbchat.NotLoggedIn, AttributeError):
            mail, password = await get_login_data()
            self.session = await fbchat.Session.login(mail, password)
            print("Logged using mail and password")
            MAIN_LOOP.create_task(self.save_cookies())
        finally:
            self.client = fbchat.Client(session=self.session)
            self.bot_id = self.session.user.id

    async def save_cookies(self):
        new_cookies = self.session.get_cookies()
        with open(self.COOKIES_FILE_PATH, "w") as cookies_file:
            json.dump(new_cookies, cookies_file)


class Listener(BotCore):
    def __init__(self):
        super().__init__()
        self.normal_commands = None
        self.group_commands = None
        self.casino_commands = None
        self.commands = None

    async def init_commands(self):
        self.normal_commands = Commands(MAIN_LOOP, self.bot_id, self.client)
        self.group_commands = GroupCommands(MAIN_LOOP, self.bot_id, self.client)
        self.casino_commands = CasinoCommands(MAIN_LOOP, self.bot_id, self.client)
        MAIN_LOOP.create_task(self.casino_commands.get_shop_items())
        self.commands = {"help": self.normal_commands.send_help_message,
                         "pomoc": self.normal_commands.send_help_message,
                         "mem": self.normal_commands.send_random_meme,
                         "film": self.normal_commands.send_random_film,
                         "say": self.normal_commands.send_tts,
                         "tvpis": self.normal_commands.send_tvpis_image,
                         "pogoda": self.normal_commands.send_weather,
                         "nick": self.normal_commands.change_nick,
                         "strona": self.normal_commands.send_webpage_link,
                         "id": self.normal_commands.send_user_id,
                         "koronawirus": self.normal_commands.send_covid_info,
                         "koronawiruspl": self.normal_commands.send_covid_pl_info,
                         "utrudnieniawawa": self.normal_commands.send_public_transport_difficulties_in_warsaw,
                         "utrudnieniawroclaw": self.normal_commands.send_public_transport_difficulties_in_wroclaw,
                         "utrudnienialodz": self.normal_commands.send_public_transport_difficulties_in_lodz,
                         "disco": self.normal_commands.make_disco,
                         "moneta": self.normal_commands.send_random_coin_side,
                         "tworca": self.normal_commands.send_link_to_creator_account,
                         "wsparcie": self.normal_commands.send_support_info,
                         "wersja": self.normal_commands.send_bot_version,
                         "waluta": self.normal_commands.convert_currency,
                         "pytanie": self.normal_commands.send_random_question,
                         "szukaj": self.normal_commands.send_search_message,
                         "miejski": self.normal_commands.send_miejski_message,
                         "tlumacz": self.normal_commands.send_translated_text,
                         "tłumacz": self.normal_commands.send_translated_text,
                         "zdjecie": self.normal_commands.send_google_image,
                         "zdjęcie": self.normal_commands.send_google_image,
                         "play": self.normal_commands.send_spotify_song,
                         "banan": self.normal_commands.send_banana_message,
                         "cena": self.normal_commands.send_product_price,
                         "tekst": self.normal_commands.send_song_lyrics,
                         "stan": self.normal_commands.send_stan_message,
                         "tablica": self.normal_commands.send_registration_number_info,
                         "bet": self.casino_commands.send_bet_message,
                         "daily": self.casino_commands.send_daily_money_message,
                         "bal": self.casino_commands.send_user_money,
                         "zdrapka": self.casino_commands.send_scratch_card_message,
                         "top": self.casino_commands.send_top_players,
                         "tip": self.casino_commands.send_tip_message,
                         "register": self.casino_commands.register,
                         "jackpot": self.casino_commands.send_jackpot_info,
                         "jackpotbuy": self.casino_commands.send_jackpot_ticket_bought_message,
                         "email": self.casino_commands.get_email,
                         "kod": self.casino_commands.check_email_verification_code,
                         "duel": self.casino_commands.send_duel_message,
                         "profil": self.casino_commands.send_player_profil,
                         "osiagniecia": self.casino_commands.send_achievements,
                         "osiągnięcia": self.casino_commands.send_achievements,
                         "sklep": self.casino_commands.send_shop_message,
                         "ruletka": self.group_commands.delete_random_person,
                         "luckymember": self.group_commands.send_message_with_random_mention,
                         "nowyregulamin": self.group_commands.set_new_group_regulations,
                         "regulamin": self.group_commands.get_group_regulations,
                         "powitanie": self.group_commands.set_welcome_message,
                         "everyone": self.group_commands.mention_everyone,
                         "kocha": self.group_commands.send_love_message}

    async def init_listening(self):
        try:
            await self.listening()
        except (fbchat.NotConnected, fbchat.NotLoggedIn, fbchat.HTTPError, UnicodeDecodeError, OSError):
            print("\nRestarting...\n")
            await self.session.logout()
            time.sleep(15)  # sleep in this place can reduce chance to get banned on facebook
            await self.login()
            await self.init_listening()
        except NotImplementedError:
            await self.session.logout()
            raise SystemError("Bot works only on Linux")

    async def set_sequence_id(self, listener):
        self.client.sequence_id_callback = listener.set_sequence_id
        await self.client.fetch_threads(limit=None).__anext__()

    async def listening(self):
        await self.init_commands()
        listener = fbchat.Listener(session=self.session, chat_on=True, foreground=True)
        MAIN_LOOP.create_task(self.set_sequence_id(listener))

        print("\nListening...\n")
        async for event in listener.listen():
            if isinstance(event, (fbchat.MessageEvent, fbchat.MessageReplyEvent)):
                MAIN_LOOP.create_task(self.handle_message_event(event))
            elif isinstance(event, fbchat.PeopleAdded):
                MAIN_LOOP.create_task(self.group_commands.send_message_on_person_added(event))
            elif isinstance(event, fbchat.PersonRemoved):
                MAIN_LOOP.create_task(self.group_commands.reply_on_person_removed(event))

    async def handle_message_event(self, event):
        if event.author.id != self.bot_id:
            try:
                if event.message.text.startswith("!"):
                    command = event.message.text.split()[0][1:].lower()
                    MAIN_LOOP.create_task(self.commands[command](event))
                    return

                yt_links = re.findall(r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?",
                                      event.message.text)
                if len(yt_links) > 0:
                    yt_link = "https://youtu.be/" + yt_links[0][0]
                    MAIN_LOOP.create_task(self.normal_commands.send_yt_video(event, yt_link))
                    return

                if "https://vm.tiktok.com/" in event.message.text:
                    MAIN_LOOP.create_task(self.normal_commands.send_tiktok(event))

            except (AttributeError, KeyError):
                # attribute error happens when someone sends photo and message doesn't have text
                pass


async def main():
    await bot.login()
    MAIN_LOOP.create_task(bot.init_listening())
    MAIN_LOOP.create_task(task_scheduler.init())


if __name__ == '__main__':
    MAIN_LOOP = asyncio.get_event_loop()
    bot = Listener()
    MAIN_LOOP.create_task(main())
    MAIN_LOOP.run_forever()
