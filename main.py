import fbchat
import asyncio
import json
import time
import python_scripts.commends
import python_scripts.casino
import python_scripts.sql_actions
import python_scripts.added_and_removed_reply


class BotCore:
    def __init__(self):

        try:
            with open("data//cookies.json", "r") as cookies_file:
                self.cookies = json.load(cookies_file)
        except FileNotFoundError:
            self.cookies = None
            print("Don`t find cookies.json")

        self.mail = ""
        self.password = ""

    async def login_and_start(self):
        print("Login in...")
        try:
            self.session = await fbchat.Session.from_cookies(self.cookies)
            self.client = fbchat.Client(session=self.session)
            print("Logged using cookies")
        except fbchat.NotLoggedIn:
            self.session = await fbchat.Session.login(self.mail, self.password)
            self.client = fbchat.Client(session=self.session)
            print("Logged using mail and password")

        try:
            await self.listening()
        except fbchat.NotConnected:
            print("\nRestarting...\n")
            await self.session.logout()
            time.sleep(15)
            MAIN_LOOP.create_task(BotCore().login_and_start())

    async def set_sequence_id(self, listener):
        self.client.sequence_id_callback = listener.set_sequence_id
        await self.client.fetch_threads(limit=1).__anext__()

    async def listening(self):
        listener = fbchat.Listener(session=self.session, chat_on=True, foreground=True)
        MAIN_LOOP.create_task(self.set_sequence_id(listener))
        cookies = self.session.get_cookies()
        with open("data//cookies.json", "w") as cookies_file:
            json.dump(cookies, cookies_file)
        print("Listening...")
        bot_id = self.session.user.id
        async for event in listener.listen():
            if isinstance(event, fbchat.MessageEvent):
                if event.author.id != bot_id:
                    try:
                        if event.message.text.startswith("!"):
                            MAIN_LOOP.create_task(COMMENDS[event.message.text.split()[0]](event, self.client))
                    except (AttributeError, KeyError):
                        # attribute error happens when someone sends photo and message don't have text
                        pass
            elif isinstance(event, fbchat.PeopleAdded):
                MAIN_LOOP.create_task(python_scripts.added_and_removed_reply.added(event, self.client))
            elif isinstance(event, fbchat.PersonRemoved):
                if bot_id != event.removed.id:
                    MAIN_LOOP.create_task(python_scripts.added_and_removed_reply.removed(event, self.client))


if __name__ == '__main__':
    COMMENDS = {"!help": python_scripts.commends.get_help_message,
                "!mem": python_scripts.commends.get_meme,
                "!film": python_scripts.commends.get_film,
                "!say": python_scripts.commends.get_tts,
                "!tvpis": python_scripts.commends.get_tvpis_image,
                "!pogoda": python_scripts.commends.get_weather,
                "!bet": python_scripts.casino.bet,
                "!daily": python_scripts.casino.give_user_daily_money,
                "!bal": python_scripts.casino.send_user_money,
                "!top": python_scripts.casino.get_top_players,
                "!tip": python_scripts.casino.tip,
                "!koronawirus": python_scripts.commends.get_coronavirus_info,
                "!koronawiruspl": python_scripts.commends.get_coronavirus_pl_info,
                "!utrudnieniawawa": python_scripts.commends.get_public_transport_difficulties_in_warsaw,
                "!utrudnieniawroclaw": python_scripts.commends.get_public_transport_difficulties_in_wroclaw,
                "!utrudnienialodz": python_scripts.commends.get_public_transport_difficulties_in_lodz,
                "!luckymember": python_scripts.commends.get_and_mention_random_member,
                "!everyone": python_scripts.commends.get_and_mention_random_member,
                "!ruletka": python_scripts.commends.delete_random_person,
                "!nowyregulamin": python_scripts.commends.set_new_group_regulations,
                "!regulamin": python_scripts.commends.get_group_regulations,
                "!powitanie": python_scripts.commends.set_welcome_message,
                "!disco": python_scripts.commends.make_disco,
                "!moneta": python_scripts.commends.make_coin_flip,
                "!nick": python_scripts.commends.change_nick,
                "!tworca": python_scripts.commends.get_link_to_creator_account,
                "!wsparcie": python_scripts.commends.get_support_info,
                "!wersja": python_scripts.commends.get_bot_version}
    MAIN_LOOP = asyncio.get_event_loop()
    MAIN_LOOP.create_task(python_scripts.sql_actions.init(MAIN_LOOP))
    MAIN_LOOP.create_task(BotCore().login_and_start())
    MAIN_LOOP.run_forever()

# works only on linux
