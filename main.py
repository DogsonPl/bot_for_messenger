import asyncio
import json
import time

import fbchat

from Bot.parse_config import get_login_data
from Bot.commands_handling.normal_commands import Commands
from Bot.commands_handling.casino_commands import CasinoCommands
from Bot.commands_handling.group_commands import GroupCommands
from Bot import task_scheduler

# works only on linux


class BotCore:
    def __init__(self):
        self.session = None
        self.client = None
        self.bot_id = None
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
            self.bot_id = self.session.user.id

    async def save_cookies(self):
        new_cookies = self.session.get_cookies()
        with open(self.cookies_file_path, "w") as cookies_file:
            json.dump(new_cookies, cookies_file)


class Listener(BotCore):
    def __init__(self):
        super().__init__()

    async def init_commands_handlers(self):
        normal_commands = Commands(MAIN_LOOP, self.bot_id, self.client)
        group_commands = GroupCommands(MAIN_LOOP, self.bot_id, self.client)
        casino_commands = CasinoCommands(MAIN_LOOP, self.bot_id, self.client)
        commands = {"help": normal_commands.send_help_message,
                    "pomoc": normal_commands.send_help_message,
                    "mem": normal_commands.send_random_meme,
                    "film": normal_commands.send_random_film,
                    "say": normal_commands.send_tts,
                    "tvpis": normal_commands.send_tvpis_image,
                    "pogoda": normal_commands.send_weather,
                    "nick": normal_commands.change_nick,
                    "strona": normal_commands.send_webpage_link,
                    "id": normal_commands.send_user_id,
                    "koronawirus": normal_commands.send_covid_info,
                    "koronawiruspl": normal_commands.send_covid_pl_info,
                    "utrudnieniawawa": normal_commands.send_public_transport_difficulties_in_warsaw,
                    "utrudnieniawroclaw": normal_commands.send_public_transport_difficulties_in_wroclaw,
                    "utrudnienialodz": normal_commands.send_public_transport_difficulties_in_lodz,
                    "disco": normal_commands.make_disco,
                    "moneta": normal_commands.send_random_coin_side,
                    "tworca": normal_commands.send_link_to_creator_account,
                    "wsparcie": normal_commands.send_support_info,
                    "wersja": normal_commands.send_bot_version,
                    "bet": casino_commands.send_bet_message,
                    "daily": casino_commands.send_daily_money_message,
                    "bal": casino_commands.send_user_money,
                    "top": casino_commands.send_top_players,
                    "tip": casino_commands.send_tip_message,
                    "register": casino_commands.register,
                    "jackpot": casino_commands.send_jackpot_info,
                    "jackpotbuy": casino_commands.send_jackpot_ticket_bought_message,
                    "email": casino_commands.get_email,
                    "kod": casino_commands.check_email_verification_code,
                    "ruletka": group_commands.delete_random_person,
                    "luckymember": group_commands.send_message_with_random_mention,
                    "nowyregulamin": group_commands.set_new_group_regulations,
                    "regulamin": group_commands.get_group_regulations,
                    "powitanie": group_commands.set_welcome_message,
                    "everyone": group_commands.mention_everyone}
        return commands, normal_commands, group_commands, casino_commands

    async def init_listening(self):
        try:
            await self.listening()
        except (fbchat.NotConnected, OSError):
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
        commands, normal_commands, group_commands, casino_commands = await self.init_commands_handlers()
        listener = fbchat.Listener(session=self.session, chat_on=True, foreground=True)
        MAIN_LOOP.create_task(self.set_sequence_id(listener))

        print("\nListening...\n")
        async for event in listener.listen():
            if isinstance(event, fbchat.MessageEvent):
                if event.author.id != self.bot_id:
                    try:
                        if event.message.text.startswith("!"):
                            command = event.message.text.split()[0][1:]
                            MAIN_LOOP.create_task(commands[command](event))
                        elif event.message.text.startswith("https://youtu"):
                            MAIN_LOOP.create_task(normal_commands.send_yt_video(event))
                    except (AttributeError, KeyError):
                        # attribute error happens when someone sends photo and message doesn't have text
                        continue
            elif isinstance(event, fbchat.PeopleAdded):
                for user in event.added:
                    if user.id == self.bot_id:
                        MAIN_LOOP.create_task(group_commands.send_bot_added_message(event))
                        break
                else:
                    MAIN_LOOP.create_task(group_commands.reply_on_person_added(event))
            elif isinstance(event, fbchat.PersonRemoved):
                if self.bot_id != event.removed.id:
                    MAIN_LOOP.create_task(group_commands.reply_on_person_removed(event))

        print("\nListening stopped. Restarting...\n")
        await bot.init_listening()


if __name__ == '__main__':
    MAIN_LOOP = asyncio.get_event_loop()
    bot = Listener()

    MAIN_LOOP.run_until_complete(bot.login())
    MAIN_LOOP.create_task(bot.init_listening())
    MAIN_LOOP.create_task(task_scheduler.init())
    MAIN_LOOP.run_forever()
