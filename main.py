import fbchat
import asyncio
import json
import time
from Bot.commands_handling.normal_commands import Commands
from Bot.commands_handling.casino_commands import CasinoCommands
from Bot.commands_handling.group_commands import GroupCommands
from Bot import sql_actions


class BotCore:
    def __init__(self):
        try:
            with open("Bot/data//cookies.json", "r") as cookies_file:
                self.cookies = json.load(cookies_file)
        except FileNotFoundError:
            self.cookies = None
            print("Cannot find cookies.json")

        self.mail = ""
        self.password = ""

    async def login(self):
        print("Login in...")
        try:
            self.session = await fbchat.Session.from_cookies(self.cookies)
            self.client = fbchat.Client(session=self.session)
            print("Logged using cookies")
        except fbchat.NotLoggedIn:
            self.session = await fbchat.Session.login(self.mail, self.password)
            self.client = fbchat.Client(session=self.session)
            print("Logged using mail and password")

        new_cookies = self.session.get_cookies()
        with open("Bot/data//cookies.json", "w") as cookies_file:
            json.dump(new_cookies, cookies_file)
        MAIN_LOOP.create_task(self.init_listening())

    async def init_listening(self):
        try:
            await Listener(self.session, self.client).listening()
        except fbchat.NotConnected:
            print("\nRestarting...\n")
            await self.session.logout()
            time.sleep(15)
            MAIN_LOOP.create_task(BotCore().login())


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
                         "!emotka": self.normal_commands.change_emoji,
                         "!nick": self.normal_commands.change_nick,
                         "!koronawirus": self.normal_commands.send_covid_info,
                         "!koronawiruspl": self.normal_commands.send_covid_pl_info,
                         "!utrudnieniawawa": self.normal_commands.send_public_transport_difficulties_in_warsaw,
                         "!utrudnieniawroclaw": self.normal_commands.send_public_transport_difficulties_in_wroclaw,
                         "!utrudnienialodz": self.normal_commands.send_public_transport_difficulties_in_lodz,
                         "!luckymember": self.normal_commands.send_message_with_random_mention,
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
                         "!ruletka": self.group_commands.delete_random_person,
                         "!nowyregulamin": self.group_commands.set_new_group_regulations,
                         "!regulamin": self.group_commands.get_group_regulations,
                         "!powitanie": self.group_commands.set_welcome_message,
                         "!everyone": self.group_commands.mention_everyone}

    async def set_sequence_id(self, listener):
        self.client.sequence_id_callback = listener.set_sequence_id
        await self.client.fetch_threads(limit=1).__anext__()

    async def listening(self):
        listener = fbchat.Listener(session=self.session, chat_on=True, foreground=True)
        MAIN_LOOP.create_task(self.set_sequence_id(listener))

        print("Listening...")
        async for event in listener.listen():
            if isinstance(event, fbchat.MessageEvent):
                if event.author.id != self.bot_id:
                    try:
                        if event.message.text.startswith("!"):
                            MAIN_LOOP.create_task(self.commands[event.message.text.split()[0]](event))
                    except (AttributeError, KeyError):
                        # attribute error happens when someone sends photo and message don't have text
                        pass
            elif isinstance(event, fbchat.PeopleAdded):
                MAIN_LOOP.create_task(self.group_commands.reply_on_person_added(event))
            elif isinstance(event, fbchat.PersonRemoved):
                if self.bot_id != event.removed.id:
                    MAIN_LOOP.create_task(self.group_commands.reply_on_person_removed(event))


if __name__ == '__main__':
    MAIN_LOOP = asyncio.get_event_loop()
    MAIN_LOOP.create_task(sql_actions.init(MAIN_LOOP))
    MAIN_LOOP.create_task(BotCore().login())
    MAIN_LOOP.run_forever()

# works only on linux
