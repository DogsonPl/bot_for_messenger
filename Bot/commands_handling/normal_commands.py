import fbchat
import random as rd
from .. import getting_and_editing_files, page_parsing
from ..bot_actions import BotActions


SETABLE_COLORS = fbchat._threads.SETABLE_COLORS


HELP_MESSAGE = """🎉Komendy🎉
⚙ !help - wysyła komendy
⚙ !strona - wysyła link do strony, jest to obecnie wersja beta, niedługo będzie możliwość snchronizowania dogecoinów
⚙ !wersja - wysyła wersje bota + to co ostatnio dodano do bota
⚙ !wsparcie - jeśli chcesz wesprzeć powstawanie bota, wyślij pieniądze na ten adres. Bot jest darmowy, ale za serwer ja muszę płacić :/ Wielkie dzięki za każdą wpłatę i pomoc!
⚙ !tworca - wysyła link do mnie (twórcy bota) Możesz śmiało do pisać :)
⚙ !id - wysyła twoje id
⚙ !koronawirus - wysyła informacje o koroawirusie na świecie
⚙ !koronawiruspl - wysyła informacje o koronawirusie w polsce
⚙ !mem - wysyła losowego mema
⚙ !luckymember - losuje losowego członka grupy
⚙ !ruletka - usuwa losowego członka grupy (bot musi mieć admina)
⚙ !pogoda x - wysyła pogode w danym miejscu (wpisz np: !pogoda Warszawa)
⚙ !nick x - zmienia twój nick na x (np '!nick coś' usatwi twoj nick na 'coś')
⚙ !everyone - oznacza wszystkich ludzi na grupie (jest napisane że oznacza jedną osobe ale tak naprawde oznaczony jest każdy)
⚙ !utrudnieniawroclaw - pisze utrudnienia w komunikacji miejskiej we Wrocławiu (ostatnie dwa posty MPK Wrocław)
⚙ !utrudnieniawawa - pisze utrudnienia w komunikacji miejsiej w Warszawie
⚙ !utrudnienialodz - pisze utrudnienia w komunikacji miejskiej w Łodzi
⚙ !moneta - bot rzuca monete (orzeł lub reszka)\n
💎DODATKOWE KOMENDY ZA ZAKUP WERSJI PRO💎
🔥 !film - wysyła losowy śmieszny film
🔥 !tvpis x- tworzy pasek z tvpis z napisem który zostanie podany po komendzie (np !tvpis jebać pis")
🔥 !disco - robi dyskoteke
🔥 !powitanie 'treść' - ustawia powitanie na grupie nowego członka
🔥 !nowyregulamin 'treść' - ustawia regulamin grupy
🔥 !regulamin - wysyła regulamin grupy
🔥 !say 'wiadomosc'- ivona mówi to co się napisze po !say\n
💰 KOMENDY DO GRY KASYNO (dogecoinsy nie są prawdziwe i nie da się ich wypłacić)💰 
💸 !register - po użyciu tej komendy możesz grać w kasyno
💸 !daily - daje codziennie darmowe dogecoins
💸 !top - wysyła 3 graczy którzy mają najwięcej monet
💸 !bal - wysyła twoją liczbe dogecoinów
💸 !bet x y - obstawiasz swoje dogecoiny (np !bet 10 50 obstawia 10 dogecoinów i masz 50% na wygraną)
💸 !tip x @oznaczenie_osoby - wysyłą x twoich dogecoinów do oznaczonej osoby np !tip 10 @imie
💸 !jackpot - wysyła informacje o tym jak działa jackpot, ile masz biletów i o tym ile w sumie zostało ich kupionych
💸 !jackpotbuy x - kupuje x ticketów (jeden ticket = 1 dogecoin)
💸 !email x - ustaw swój email jako x
💸 !kod x - wpisz kod potwierdzający który dostałeś na email
"""

LINK_TO_MY_FB_ACCOUNT_MESSAGE = "👨‍💻 Możesz do mnie (twórcy) napisac na: https://www.facebook.com/dogsonjakub.nowak.7"

SUPPORT_INFO_MESSAGE = """🧧💰💎 Jeśli chcesz wspomóc prace nad botem, możesz wysłac donejta. Za każdą pomoc wielkie dzieki 💎💰🧧!
💴 Paypal: paypal.me/DogsonPL
💴 Konto bankowe: nr konta 22 1140 2004 0000 3002 7878 9413, Jakub Nowakowski
💴 Psc: wyślij kod na pv do !tworca"""

BOT_VERSION_MESSAGE = """❤DZIĘKUJĘ ZA ZAKUP WERSJI PRO!❤
🤖 Wersja bota: 7.1 + 8.2 pro 🤖

🧾 Ostatnio do bota dodano:
🆕 !strona
🆕 !email
🆕 !kod
"""


class Commands(BotActions):
    def __init__(self, loop, bot_id, client):
        self.get_weather = page_parsing.GetWeather().get_weather
        self.downloading_videos = 0
        super().__init__(loop, bot_id, client)

    async def send_help_message(self, event):
        await self.send_text_message(event, HELP_MESSAGE)

    async def send_link_to_creator_account(self, event):
        await self.send_text_message(event, LINK_TO_MY_FB_ACCOUNT_MESSAGE)

    async def send_support_info(self, event):
        await self.send_text_message(event, SUPPORT_INFO_MESSAGE)

    async def send_bot_version(self, event):
        await self.send_text_message(event, BOT_VERSION_MESSAGE)

    async def send_user_id(self, event):
        await self.send_text_message(event, f"🆔 Twoje id to {event.author.id}")

    async def send_webpage_link(self, event):
        await self.send_text_message(event, """🔗 Link do strony www: https://dogson.ovh. Strona jest w wersji beta

Żeby połączyć swoje dane z kasynem że stroną, ustaw w  bocie email za pomocą komendy !email, a potem załóż konto na stronie bota na ten sam email""")

    async def send_weather(self, event):
        city = event.message.text[8:]
        weather = await self.get_weather(city)
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

    async def send_yt_video(self, event):
        if self.downloading_videos > 10:
            await self.send_text_message(event, "🚫 Bot obecnie pobiera za dużo filmów. Spróbuj ponownie później")
        else:
            self.downloading_videos += 1
            link = event.message.text.split()[0]
            video, filetype = await self.loop.run_in_executor(None, page_parsing.download_yt_video, link)
            await self.send_bytes_file(event, video, filetype)
            self.downloading_videos -= 1

    @staticmethod
    async def make_disco(event):
        for _ in range(5):
            color = rd.choice(SETABLE_COLORS)
            await event.thread.set_color(color)

    async def change_nick(self, event):
        try:
            await event.thread.set_nickname(user_id=event.author.id, nickname=" ".join(event.message.text.split()[1:]))
        except fbchat.InvalidParameters:
            await self.send_text_message(event, "🚫 Wpisano za długi nick")
