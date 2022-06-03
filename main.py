import asyncio
import json
import time
import re
import os
import sys
os.chdir(sys.path[0])

import fbchat

from Bot.commands import BotCommands
from Bot.parse_config import get_login_data
from Bot import task_scheduler

# works only on linux!


class BotCore:
    COOKIES_FILE_PATH: str = "cookies.json"
    session: fbchat.Session
    client: fbchat.Client
    bot_id: str

    def __init__(self):
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
    bot_commands: BotCommands
    commands: dict
    find_yt_link_regex: str = r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?"

    def __init__(self):
        super().__init__()

    async def init_commands(self):
        threads = self.client.fetch_threads(None)
        threads_id = []
        async for i in threads:
            threads_id.append(i.id)
        self.bot_commands = BotCommands(MAIN_LOOP, self.bot_id, self.client, threads_id)
        MAIN_LOOP.create_task(self.bot_commands.get_shop_items())
        self.commands = {"help": self.bot_commands.send_help_message,
                         "pomoc": self.bot_commands.send_help_message,
                         "mem": self.bot_commands.send_random_meme,
                         "film": self.bot_commands.send_random_film,
                         "say": self.bot_commands.send_tts,
                         "tvpis": self.bot_commands.send_tvpis_image,
                         "pogoda": self.bot_commands.send_weather,
                         "nick": self.bot_commands.change_nick,
                         "strona": self.bot_commands.send_webpage_link,
                         "id": self.bot_commands.send_user_id,
                         "koronawirus": self.bot_commands.send_covid_info,
                         "koronawiruspl": self.bot_commands.send_covid_pl_info,
                         "utrudnieniawawa": self.bot_commands.send_public_transport_difficulties_in_warsaw,
                         "utrudnieniawroclaw": self.bot_commands.send_public_transport_difficulties_in_wroclaw,
                         "utrudnienialodz": self.bot_commands.send_public_transport_difficulties_in_lodz,
                         "disco": self.bot_commands.make_disco,
                         "moneta": self.bot_commands.send_random_coin_side,
                         "tworca": self.bot_commands.send_link_to_creator_account,
                         "wsparcie": self.bot_commands.send_support_info,
                         "wersja": self.bot_commands.send_bot_version,
                         "waluta": self.bot_commands.convert_currency,
                         "pytanie": self.bot_commands.send_random_question,
                         "szukaj": self.bot_commands.send_search_message,
                         "miejski": self.bot_commands.send_miejski_message,
                         "tlumacz": self.bot_commands.send_translated_text,
                         "tłumacz": self.bot_commands.send_translated_text,
                         "zdjecie": self.bot_commands.send_google_image,
                         "zdjęcie": self.bot_commands.send_google_image,
                         "play": self.bot_commands.send_spotify_song,
                         "banan": self.bot_commands.send_banana_message,
                         "cena": self.bot_commands.send_product_price,
                         "tekst": self.bot_commands.send_song_lyrics,
                         "stan": self.bot_commands.send_stan_message,
                         "tablica": self.bot_commands.send_registration_number_info,
                         "bet": self.bot_commands.send_bet_message,
                         "daily": self.bot_commands.send_daily_money_message,
                         "bal": self.bot_commands.send_user_money,
                         "zdrapka": self.bot_commands.send_scratch_card_message,
                         "top": self.bot_commands.send_top_players,
                         "tip": self.bot_commands.send_tip_message,
                         "register": self.bot_commands.send_register_message,
                         "jackpot": self.bot_commands.send_jackpot_info,
                         "jackpotbuy": self.bot_commands.send_jackpot_ticket_bought_message,
                         "email": self.bot_commands.send_user_email,
                         "kod": self.bot_commands.send_email_verification_code_message,
                         "duel": self.bot_commands.send_duel_message,
                         "profil": self.bot_commands.send_player_profil,
                         "osiagniecia": self.bot_commands.send_achievements,
                         "osiągnięcia": self.bot_commands.send_achievements,
                         "sklep": self.bot_commands.send_shop_message,
                         "slots": self.bot_commands.send_slots_message,
                         "ruletka": self.bot_commands.delete_random_person,
                         "luckymember": self.bot_commands.send_message_with_random_mention,
                         "nowyregulamin": self.bot_commands.set_new_group_regulations,
                         "regulamin": self.bot_commands.get_group_regulations,
                         "powitanie": self.bot_commands.set_welcome_message,
                         "everyone": self.bot_commands.mention_everyone,
                         "kocha": self.bot_commands.send_love_message,
                         "ukraina": self.bot_commands.ukraine}

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
                MAIN_LOOP.create_task(self.bot_commands.send_message_on_person_added(event))
            elif isinstance(event, fbchat.PersonRemoved):
                MAIN_LOOP.create_task(self.bot_commands.reply_on_person_removed(event))

    async def handle_message_event(self, event):
        if event.author.id != self.bot_id:
            try:
                if event.message.text.startswith("!"):
                    command = event.message.text.split()[0][1:].lower()
                    MAIN_LOOP.create_task(self.commands[command](event))
                    return

                yt_links = re.findall(self.find_yt_link_regex, event.message.text)
                if len(yt_links) > 0:
                    yt_link = "https://youtu.be/" + yt_links[0][0]
                    MAIN_LOOP.create_task(self.bot_commands.send_yt_video(event, yt_link))
                    return
                if "https://vm.tiktok.com/" in event.message.text:
                    MAIN_LOOP.create_task(self.bot_commands.send_tiktok(event))

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
