import fbchat
import random as rd
from Bot import getting_and_editing_files, page_parsing
from Bot.bot_actions import BotActions


SETABLE_COLORS = fbchat._threads.SETABLE_COLORS


HELP_MESSAGE = """Komendy:\n
!help - wysyła komendy\n
!wersja - wysyła wersje bota + to co ostatnio dodano do bota\n
!wsparcie - jeśli chcesz wesprzeć powstawanie bota, wyślij pieniądze na ten adres. Bot jest darmowy, ale za serwer ja muszę płacić :/ Wielkie dzięki za każdą wpłatę i pomoc!\n
!tworca - wysyła link do mnie (twórcy bota) Możesz śmiało do pisać :)\n
!koronawirus - wysyła informacje o koroawirusie na świecie\n
!koronawiruspl - wysyła informacje o koronawirusie w polsce\n
!mem - wysyła losowego mema\n
!luckymember - losuje losowego członka grupy\n
!ruletka - usuwa losowego członka grupy (bot musi mieć admina)\n
!pogoda x - wysyła pogode w danym miejscu (wpisz np: !pogoda Warszawa)\n
!nick x - zmienia twój nick na x (np '!nick coś' usatwi twoj nick na 'coś')\n  
!everyone - oznacza wszystkich ludzi na grupie (jest napisane że oznacza jedną osobe ale tak naprawde oznaczony jest każdy)\n
!utrudnieniawroclaw - pisze utrudnienia w komunikacji miejskiej we Wrocławiu (ostatnie dwa posty MPK Wrocław)\n
!utrudnieniawawa - pisze utrudnienia w komunikacji miejsiej w Warszawie\n
!utrudnienialodz - pisze utrudnienia w komunikacji miejskiej w Łodzi\n
!moneta - bot rzuca monete (orzeł lub reszka)\n
DODATKOWE KOMENDY ZA ZAKUP WERSJI PRO:\n
!film - wysyła losowy śmieszny film\n
!tvpis x- tworzy pasek z tvpis z napisem który zostanie podany po komendzie (np !tvpis jebać pis")\n
!disco - robi dyskoteke\n
!emotka x - zmienia emotke na x (np emotka 😎)\n
!powitanie 'treść' - ustawia powitanie na grupie nowego członka\n
!nowyregulamin 'treść' - ustawia regulamin grupy\n
!regulamin - wysyła regulamin grupy\n
!say 'wiadomosc'- ivona mówi to co się napisze po !say\n 
KOMENDY DO GRY KASYNO (dogecoinsy nie są prawdziwe i nie da się ich wypłacić)\n
!daily - daje codziennie darmowe dogecoins\n
!top - wysyła 3 graczy którzy mają najwięcej monet\n
!bal - wysyła twoją liczbe dogecoinów\n
!bet x y - obstawiasz swoje dogecoiny (np !bet 10 50 obstawia 10 dogecoinów i masz 50% na wygraną)\n
!tip x @oznaczenie_osoby - wysyłą x twoich dogecoinów do oznaczonej osoby np !tip 10 @imie\n"""

LINK_TO_MY_FB_ACCOUNT_MESSAGE = "Możesz do mnie (twórcy) napisac na: https://www.facebook.com/dogsonjakub.nowak.7"

SUPPORT_INFO_MESSAGE = """Jeśli chcesz wspomóc prace nad botem, możesz wysłac donejta. Za kazdą pomoc wielkie dzieki!
Paypal: paypal.me/DogsonPL
Konto bankowe: nr konta 22 1140 2004 0000 3002 7878 9413, Jakub Nowakowski
Psc: wyslij kod na pv do !tworca"""

BOT_VERSION_MESSAGE = """DZIĘKUJĘ ZA ZAKUP WERSJI PRO! Wersja bota: 5.0 + 8.0 pro
Ostatnio do bota dodano:
Kasyno! Komendy do niego: top, bet, bal, tip, daily
!everyone jest dostępne tylko dla adminów
Dodano komende !tvpis"""


class Commands(BotActions):
    def __init__(self, loop, bot_id, client):
        super().__init__(loop, bot_id, client)

    async def send_help_message(self, event):
        await self.send_text_message(event, HELP_MESSAGE)

    async def send_link_to_creator_account(self, event):
        await self.send_text_message(event, LINK_TO_MY_FB_ACCOUNT_MESSAGE)

    async def send_support_info(self, event):
        await self.send_text_message(event, SUPPORT_INFO_MESSAGE)

    async def send_bot_version(self, event):
        await self.send_text_message(event, BOT_VERSION_MESSAGE)

    async def send_weather(self, event):
        city = event.message.text[8:]
        weather = await page_parsing.get_weather(city)
        await self.send_text_message(event, weather)

    async def send_covid_info(self, event):
        covid_info = await page_parsing.get_coronavirus_info()
        await self.send_text_message(event, covid_info)

    async def send_covid_pl_info(self, event):
        covid_pl_info = await page_parsing.get_coronavirus_pl_info()
        await self.send_text_message(event, covid_pl_info)

    async def send_public_transport_difficulties_in_warsaw(self, event):
        difficulties_in_warsaw = await page_parsing.get_public_transport_difficulties_in_warsaw()
        await self.send_text_message(event, difficulties_in_warsaw)

    async def send_public_transport_difficulties_in_wroclaw(self, event):
        difficulties_in_wroclaw = await page_parsing.get_public_transport_difficulties_in_wroclaw()
        await self.send_text_message(event, difficulties_in_wroclaw)

    async def send_public_transport_difficulties_in_lodz(self, event):
        difficulties_in_lodz = await page_parsing.get_public_transport_difficulties_in_lodz()
        await self.send_text_message(event, difficulties_in_lodz)

    async def send_message_with_random_mention(self, event):
        group_info = await self.get_thread_info(event.thread.id)
        mention = await get_random_mention(group_info)
        await self.send_text_message_with_mentions(event, "Zwycieżca", mention)

    async def send_random_meme(self, event):
        meme_path, filetype = await getting_and_editing_files.get_random_meme()
        await self.send_file(event, meme_path, filetype)

    async def send_random_film(self, event):
        film_path, filetype = await getting_and_editing_files.get_random_film()
        await self.send_file(event, film_path, filetype)

    async def send_random_coin_side(self, event):
        film_path, filetype = await getting_and_editing_files.make_coin_flip()
        await self.send_file(event, film_path, filetype)

    async def send_tvpis_image(self, event):
        text = event.message.text[6:]
        image, filetype = await self.loop.run_in_executor(None, getting_and_editing_files.edit_tvpis_image, text)
        await self.send_bytes_file(event, image, filetype)

    async def send_tts(self, event):
        text = event.message.text[4:]
        tts = await self.loop.run_in_executor(None, getting_and_editing_files.get_tts, text)
        await self.send_bytes_audio_file(event, tts)

    @staticmethod
    async def make_disco(event):
        for i in range(5):
            color = rd.choice(SETABLE_COLORS)
            await event.thread.set_color(color)

    async def change_emoji(self, event):
        await self.send_text_message(event, """Fb czasowo usunął możliwość zmieniania emoji przez API. 
    Opcja zostanie dodana wtedy kiedy fb znowu doda te funkcje""")
        # todo try to fix this function
        # try:
        #    await event.thread.set_emoji(emoji=event.message.text[8])
        # except:
        #    await event.thread.set_emoji(emoji=event.message.text[7])

    async def change_nick(self, event):
        await self.send_text_message(event, """Fb czasowo usunął nicki.
    Opcja zostanie dodana wtedy kiedy fb znowu doda te funkcje""")
        # todo add commented part of code in this function when nicknames in messenger come back
        # try:
        #    await event.thread.set_nickname(user_id=event.author.id, nickname=event.message.text[5:])
        # except:
        #    await event.thread.send_text("Linux nie moze odczytać polskiej litery, albo wpisałes za długi nick")


async def get_random_mention(group_info):
    lucky_member = rd.choice(group_info.participants).id
    mention = [fbchat.Mention(thread_id=lucky_member, offset=0, length=9)]
    return mention
