from data.my_python_scripts import commends, added_and_removed_reply, stupid_answers
import fbchat
import asyncio
import json
import logging


class BotCore:
    def __init__(self, loop):
        self.loop = loop

        try:
            with open("data\\mutelist.json", "r") as read_file:
                self.mutelist = json.load(read_file)
        except FileNotFoundError:
            self.mutelist = []
            print("Don't find mutelist.json")
        try:
            with open("data\\cookies.json", "r") as cookies_file:
                self.cookies = json.load(cookies_file)
        except FileNotFoundError:
            self.cookies = None
            print("Don`t find cookies.json")

        self.mail = ""
        self.password = ""

    async def start(self):
        print("Login in...")
        try:
            self.session = await fbchat.Session.from_cookies(self.cookies)
            self.client = fbchat.Client(session=self.session)
            print("Zalogowano uzywajac ciastek")
        except:
            self.session = await fbchat.Session.login(self.mail, self.password)
            self.client = fbchat.Client(session=self.session)
            logging.getLogger("fbchat").setLevel(logging.DEBUG)
            print("Zalogowano uzuwajac maila i hasla")

        await self.listening()

    async def _fetch_sequence_id(self):
        self.client.sequence_id_callback = self.listener.set_sequence_id
        await asyncio.sleep(5)
        await self.client.fetch_threads(limit=1).__anext__()

    async def listening(self):
        self.listener = fbchat.Listener(session=self.session, chat_on=True, foreground=True)
        self.loop.create_task(self._fetch_sequence_id())
        print("Listening...")
        cookies = self.session.get_cookies()
        with open("data\\cookies.json", "w") as cookies_file:
            json.dump(cookies, cookies_file)
        async for event in self.listener.listen():
            if isinstance(event, fbchat.MessageEvent):
                if event.author.id != self.session.user.id:
                    if event.message.text is None:
                        pass
                    else:
                        if event.message.text.startswith("!"):
                            if event.message.text == "!help" or event.message.text == "!pomoc" or event.message.text == "!komendy":
                                self.loop.create_task(commends.help_(event))
                            elif event.message.text == "!mem":
                                self.loop.create_task(commends.mem(event, self.client))
                            elif event.message.text == "!mem2":
                                self.loop.create_task(commends.mem2(event, self.client))
                            elif event.message.text == "!film":
                                self.loop.create_task(commends.film(event, self.client))
                            elif event.message.text == "!moneta":
                                self.loop.create_task(commends.moneta(event, self.client))
                            elif "!say" in event.message.text:
                                self.loop.create_task(commends.say(event, self.client))
                            elif "!pogoda" in event.message.text:
                                self.loop.create_task(commends.weather_function(event))
                            elif event.message.text == "!koronawirus":
                                self.loop.create_task(commends.coronavirus(event))
                            elif event.message.text == "!koronawiruspl":
                                self.loop.create_task(commends.coronavirus_pl(event))
                            elif event.message.text == "!utrudnieniawawa":
                                self.loop.create_task(commends.utrudnienia_wawa(event))
                            elif event.message.text == "!utrudnieniawroclaw":
                                self.loop.create_task(commends.utrudnienia_wroclaw(event))
                            elif event.message.text == "!utrudnienialodz":
                                self.loop.create_task(commends.utrudnienia_lodz(event))
                            elif event.message.text == "!mute":
                                self.loop.create_task(commends.mute(event, self.client, self.mutelist))
                            elif event.message.text == "!unmute":
                                self.loop.create_task(commends.unmute(event, self.client, self.mutelist))
                            elif event.message.text == "!luckymember":
                                self.loop.create_task(commends.luckymember(event, self.client))
                            elif event.message.text == "!para":
                                self.loop.create_task(commends.para(event, self.client))
                            elif event.message.text == "!everyone":
                                self.loop.create_task(commends.everyone(event, self.client, self.mutelist))
                            elif event.message.text == "!ruletka":
                                self.loop.create_task(commends.ruletka(event, self.client, self.session.user.id))
                            elif "!nowyregulamin" in event.message.text:
                                self.loop.create_task(commends.nowy_regulamin(event, self.client))
                            elif event.message.text == "!regulamin":
                                self.loop.create_task(commends.wyslij_regulamin(event))
                            elif "!powitanie" in event.message.text:
                                self.loop.create_task(commends.powitanie(event, self.client))
                            elif "!emotka" in event.message.text:
                                self.loop.create_task(commends.zmiana_emoji(event))
                            elif event.message.text == "!disco":
                                self.loop.create_task(commends.disco(event))
                            elif "!tvpis" in event.message.text:
                                self.loop.create_task(commends.tvpis(event, self.client))
                            elif "!nick" in event.message.text:
                                self.loop.create_task(commends.change_nick(event))
                            elif "!losuj" in event.message.text:
                                self.loop.create_task(commends.losuj(event))
                            elif event.message.text == "!tworca":
                                self.loop.create_task(commends.tworca(event))
                            elif event.message.text == "!wsparcie":
                                self.loop.create_task(commends.wsparcie(event))
                            elif event.message.text == "!wersja":
                                self.loop.create_task(commends.wersja(event))
                            elif event.message.text == "!":
                                self.loop.create_task(commends.test(event, self.mutelist))
                        else:
                            if event.thread.id in self.mutelist:
                                pass
                            else:
                                if "kurwa" in event.message.text.lower():
                                    self.loop.create_task(stupid_answers.kurwa(event))
                                elif "co" in event.message.text:
                                    self.loop.create_task(stupid_answers.co(event))
                                elif "Xd" in event.message.text:
                                    self.loop.create_task(stupid_answers.Xd(event))
                                elif "jd" in event.message.text.lower():
                                    self.loop.create_task(stupid_answers.jd(event))
                                elif "chuj" in event.message.text:
                                    self.loop.create_task(stupid_answers.chuj(event))
                                elif "fortnite" in event.message.text:
                                    self.loop.create_task(stupid_answers.fortnite(event))
                                elif "seks" in event.message.text or "69" in event.message.text:
                                    self.loop.create_task(stupid_answers.seks(event))
                                elif "pis" in event.message.text or "konfederacja" in event.message.text:
                                    self.loop.create_task(stupid_answers.pis_konfederacja(event))
            elif isinstance(event, fbchat.PeopleAdded):
                await loop.create_task(added_and_removed_reply.added(event, self.mutelist))
            elif isinstance(event, fbchat.PersonRemoved):
                if self.session.user.id != event.removed.id:
                    await loop.create_task(added_and_removed_reply.removed(event, self.mutelist))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(BotCore(loop).start())
    loop.run_forever()

# dziala tylko na linuxie
