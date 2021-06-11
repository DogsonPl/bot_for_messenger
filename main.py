import asyncio
import json
import time

import fbchat

from Bot.parse_config import get_login_data
from Bot.commands_handling.normal_commands import Commands
from Bot.commands_handling.casino_commands import CasinoCommands
from Bot.commands_handling.group_commands import GroupCommands
from Bot import task_scheduler


class BotCore:
    def __init__(self):
        self.cookies_file_path = "Bot//data//cookies.json"
        try:
            with open(self.cookies_file_path, "r") as cookies_file:
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

    async def save_cookies(self):
        new_cookies = self.session.get_cookies()
        with open(self.cookies_file_path, "w") as cookies_file:
            json.dump(new_cookies, cookies_file)

    async def init_listening(self):
        try:
            await Listener(self.session, self.client).listening()
        except (fbchat.NotConnected, OSError):
            print("\nRestarting...\n")
            await self.session.logout()
            time.sleep(15)  # sleep in this place can reduce chance to get banned on facebook
            await self.login()
            await self.init_listening()
        except NotImplementedError:
            await self.session.logout()
            raise SystemError("Bot works only on Linux")


class Listener:
    def __init__(self, session, client):
        self.session = session
        self.client = client
        self.bot_id = self.session.user.id
        self.normal_commands = Commands(MAIN_LOOP, self.bot_id, self.client)
        self.group_commands = GroupCommands(MAIN_LOOP, self.bot_id, self.client)
        self.casino_commands = CasinoCommands(MAIN_LOOP, self.bot_id, self.client)
        self.commands = {"!help": self.normal_commands.send_help_message,
                         "!mem": self.normal_commands.send_random_meme,
                         "!film": self.normal_commands.send_random_film,
                         "!say": self.normal_commands.send_tts,
                         "!tvpis": self.normal_commands.send_tvpis_image,
                         "!pogoda": self.normal_commands.send_weather,
                         "!nick": self.normal_commands.change_nick,
                         "!strona": self.normal_commands.send_webpage_link,
                         "!id": self.normal_commands.send_user_id,
                         "!koronawirus": self.normal_commands.send_covid_info,
                         "!koronawiruspl": self.normal_commands.send_covid_pl_info,
                         "!utrudnieniawawa": self.normal_commands.send_public_transport_difficulties_in_warsaw,
                         "!utrudnieniawroclaw": self.normal_commands.send_public_transport_difficulties_in_wroclaw,
                         "!utrudnienialodz": self.normal_commands.send_public_transport_difficulties_in_lodz,
                         "!disco": self.normal_commands.make_disco,
                         "!moneta": self.normal_commands.send_random_coin_side,
                         "!tworca": self.normal_commands.send_link_to_creator_account,
                         "!wsparcie": self.normal_commands.send_support_info,
                         "!wersja": self.normal_commands.send_bot_version,
                         "!bet": self.casino_commands.send_bet_message,
                         "!daily": self.casino_commands.send_daily_money_message,
                         "!bal": self.casino_commands.send_user_money,
                         "!top": self.casino_commands.send_top_players,
                         "!tip": self.casino_commands.send_tip_message,
                         "!register": self.casino_commands.register,
                         "!jackpot": self.casino_commands.send_jackpot_info,
                         "!jackpotbuy": self.casino_commands.send_jackpot_ticket_bought_message,
                         "!email": self.casino_commands.get_email,
                         "!kod": self.casino_commands.check_email_verification_code,
                         "!ruletka": self.group_commands.delete_random_person,
                         "!luckymember": self.group_commands.send_message_with_random_mention,
                         "!nowyregulamin": self.group_commands.set_new_group_regulations,
                         "!regulamin": self.group_commands.get_group_regulations,
                         "!powitanie": self.group_commands.set_welcome_message,
                         "!everyone": self.group_commands.mention_everyone}

    async def set_sequence_id(self, listener):
        self.client.sequence_id_callback = listener.set_sequence_id
        await self.client.fetch_threads(limit=None).__anext__()

    async def listening(self):
        listener = fbchat.Listener(session=self.session, chat_on=True, foreground=True)
        MAIN_LOOP.create_task(self.set_sequence_id(listener))

        print("\nListening...\n")
        async for event in listener.listen():
            if isinstance(event, fbchat.MessageEvent):
                if event.author.id != self.bot_id:
                    try:
                        if event.message.text.startswith("!"):
                            MAIN_LOOP.create_task(self.commands[event.message.text.split()[0]](event))
                        elif event.message.text.startswith("https://youtu"):
                            MAIN_LOOP.create_task(self.normal_commands.send_yt_video(event))
                    except (AttributeError, KeyError):
                        # attribute error happens when someone sends photo and message doesn't have text
                        continue
            elif isinstance(event, fbchat.PeopleAdded):
                for user in event.added:
                    if user.id == self.bot_id:
                        MAIN_LOOP.create_task(self.group_commands.send_bot_added_message(event))
                        break
                else:
                    MAIN_LOOP.create_task(self.group_commands.reply_on_person_added(event))
            elif isinstance(event, fbchat.PersonRemoved):
                if self.bot_id != event.removed.id:
                    MAIN_LOOP.create_task(self.group_commands.reply_on_person_removed(event))

        print("\nListening stopped. Restarting...\n")
        await bot.init_listening()


if __name__ == '__main__':
    bot = BotCore()
    MAIN_LOOP = asyncio.get_event_loop()

    MAIN_LOOP.run_until_complete(bot.login())
    MAIN_LOOP.create_task(bot.init_listening())
    MAIN_LOOP.create_task(task_scheduler.init())
    MAIN_LOOP.run_forever()

# works only on linux
