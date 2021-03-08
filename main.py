import fbchat
import asyncio
import json
import time
from python_scripts import commends, stupid_answers, added_and_removed_reply, sql_actions, casino


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
                            if event.message.text == "!help":
                                MAIN_LOOP.create_task(commends.get_help_message(event))
                            elif event.message.text == "!mem":
                                MAIN_LOOP.create_task(commends.get_meme(event, self.client))
                            elif event.message.text == "!film":
                                MAIN_LOOP.create_task(commends.get_film(event, self.client))
                            elif "!say" in event.message.text:
                                MAIN_LOOP.create_task(commends.get_tts(event, self.client))
                            elif "!tvpis" in event.message.text:
                                MAIN_LOOP.create_task(commends.get_tvpis_image(event, self.client))
                            elif "!pogoda" in event.message.text:
                                MAIN_LOOP.create_task(commends.get_weather(event))
                            elif "!bet" in event.message.text:
                                MAIN_LOOP.create_task(casino.bet(event))
                            elif event.message.text == "!daily":
                                MAIN_LOOP.create_task(casino.give_user_daily_money(event))
                            elif event.message.text == "!bal":
                                MAIN_LOOP.create_task(casino.send_user_money(event))
                            elif event.message.text == "!top":
                                MAIN_LOOP.create_task(casino.get_top_players(event, self.client))
                            elif "!tip" in event.message.text:
                                MAIN_LOOP.create_task(casino.tip(event))
                            elif event.message.text == "!koronawirus":
                                MAIN_LOOP.create_task(commends.get_coronavirus_info(event))
                            elif event.message.text == "!koronawiruspl":
                                MAIN_LOOP.create_task(commends.get_coronavirus_pl_info(event))
                            elif event.message.text == "!utrudnieniawawa":
                                MAIN_LOOP.create_task(commends.get_public_transport_difficulties_in_warsaw(event))
                            elif event.message.text == "!utrudnieniawroclaw":
                                MAIN_LOOP.create_task(commends.get_public_transport_difficulties_in_wroclaw(event))
                            elif event.message.text == "!utrudnienialodz":
                                MAIN_LOOP.create_task(commends.get_public_transport_difficulties_in_lodz(event))
                            elif event.message.text == "!luckymember":
                                MAIN_LOOP.create_task(commends.get_and_mention_random_member(event, self.client))
                            elif event.message.text == "!everyone":
                                MAIN_LOOP.create_task(commends.mention_everyone(event, self.client, True))
                            elif event.message.text == "!ruletka":
                                MAIN_LOOP.create_task(commends.delete_random_person(event, self.client, True, bot_id))
                            elif "!nowyregulamin" in event.message.text:
                                MAIN_LOOP.create_task(commends.set_new_group_regulations(event, self.client, True))
                            elif event.message.text == "!regulamin":
                                MAIN_LOOP.create_task(commends.get_group_regulations(event, self.client, False))
                            elif "!powitanie" in event.message.text:
                                MAIN_LOOP.create_task(commends.set_welcome_message(event, self.client, True))
                            elif "!emotka" in event.message.text:
                                MAIN_LOOP.create_task(commends.change_emoji(event))
                            elif event.message.text == "!disco":
                                MAIN_LOOP.create_task(commends.make_disco(event))
                            elif event.message.text == "!moneta":
                                MAIN_LOOP.create_task(commends.make_coin_flip(event, self.client))
                            elif "!nick" in event.message.text:
                                MAIN_LOOP.create_task(commends.change_nick(event))
                            elif event.message.text == "!tworca":
                                MAIN_LOOP.create_task(commends.get_link_to_creator_account(event))
                            elif event.message.text == "!wsparcie":
                                MAIN_LOOP.create_task(commends.get_support_info(event))
                            elif event.message.text == "!wersja":
                                MAIN_LOOP.create_task(commends.get_bot_version(event))

                        else:
                            message = event.message.text.split()
                            if "kurwa" in message:
                                MAIN_LOOP.create_task(stupid_answers.kurwa(event))
                            elif "co" in message:
                                MAIN_LOOP.create_task(stupid_answers.co(event))
                            elif "jd" in message:
                                MAIN_LOOP.create_task(stupid_answers.jd(event))
                            elif "chuj" in message:
                                MAIN_LOOP.create_task(stupid_answers.chuj(event))
                            elif "fortnite" in message:
                                MAIN_LOOP.create_task(stupid_answers.fortnite(event))
                            elif "pis" in message:
                                MAIN_LOOP.create_task(stupid_answers.pis_konfederacja(event))
                    except AttributeError:
                        # attribute error happens when someone sends photo and message don't have text
                        pass
            elif isinstance(event, fbchat.PeopleAdded):
                MAIN_LOOP.create_task(added_and_removed_reply.added(event))
            elif isinstance(event, fbchat.PersonRemoved):
                if bot_id != event.removed.id:
                    MAIN_LOOP.create_task(added_and_removed_reply.removed(event))


if __name__ == '__main__':
    MAIN_LOOP = asyncio.get_event_loop()
    MAIN_LOOP.create_task(sql_actions.init(MAIN_LOOP))
    MAIN_LOOP.create_task(BotCore().login_and_start())
    MAIN_LOOP.run_forever()

# works only on linux
