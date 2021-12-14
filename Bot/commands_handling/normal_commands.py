import random as rd

import fbchat
from forex_python.converter import CurrencyRates, RatesNotAvailableError
from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException, NotValidPayload

from .logger import logger
from .. import getting_and_editing_files, page_parsing
from ..bot_actions import BotActions


SETABLE_COLORS = fbchat._threads.SETABLE_COLORS
currency_converter = CurrencyRates()
questions = []
with open("Bot/data/questions.txt") as file:
    for i in file.readlines():
        questions.append(i)


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
⚙ !moneta - bot rzuca monete (orzeł lub reszka)
⚙ !waluta ilość z do - np !waluta 10 PLN USD zamienia 10 złoty na 10 dolarów
⚙ !kocha @nick1 @nick2 - wysyła wiadomość jak bardzo pierwsza oznaczona osoba kocha drugą oznaczoną osobę
⚙ !banan @nick - wysyła wiadomość jak dużego masz banana (albo osoba oznaczona gdy zostanie ktoś oznacozny)
⚙ !lyrics twórca, tytuł piosenki
⚙ !pytanie - wysyła losowe pytanie\n
💎DODATKOWE KOMENDY ZA ZAKUP WERSJI PRO💎
🔥 !szukaj x - wyszukuje informacje o rzeczy x w internecie np !szukaj python
🔥 !tlumacz --jezyk x - tlumaczy tekst na podany jezyk (normalnie na polski), np !tlumacz --english Привет lub !tlumacz Привет
🔥 !miejski x - wyszukuje podane słowo na stronie miejski
🔥 !film - wysyła losowy śmieszny film
🔥 !tvpis x- tworzy pasek z tvpis z napisem który zostanie podany po komendzie (np !tvpis jebać pis")
🔥 !disco - robi dyskoteke
🔥 !powitanie 'treść' - ustawia powitanie na grupie nowego członka
🔥 !nowyregulamin 'treść' - ustawia regulamin grupy
🔥 !regulamin - wysyła regulamin grupy
🔥 !zdjecie x - wysyła zdjecie x
🔥 !play x - bot wysyła piosenke, można wpisać nazwe piosenki albo link do spotify
🔥 !cena x - wysyła cene podanej rzeczy
🔥 !say 'wiadomosc'- ivona mówi to co się napisze po !say\n
💰 KOMENDY DO GRY KASYNO (dogecoinsy nie są prawdziwe i nie da się ich wypłacić)💰 
💸 !register - po użyciu tej komendy możesz grać w kasyno
💸 !daily - daje codziennie darmowe dogecoins
💸 !top - wysyła 3 graczy którzy mają najwięcej monet
💸 !bal - wysyła twoją liczbe dogecoinów
💸 !bet x y - obstawiasz swoje dogecoiny (np !bet 10 50 obstawia 10 dogecoinów i masz 50% na wygraną)
💸 !zdrapka - koszt zdrapki to 5 dogów, można wygrać od 0 do 2500 dogecoinów 
💸 !tip x @oznaczenie_osoby - wysyłą x twoich dogecoinów do oznaczonej osoby np !tip 10 @imie
💸 !jackpot - wysyła informacje o tym jak działa jackpot, ile masz biletów i o tym ile w sumie zostało ich kupionych
💸 !jackpotbuy x - kupuje x ticketów (jeden ticket = 1 dogecoin)
💸 !duel - gra duel, po więcej informacji napisz !duel
💸 !email x - ustaw swój email jako x
💸 !kod x - wpisz kod potwierdzający którego otrzymano na email
💸 !profil- wysyła twoje statystyki
"""

LINK_TO_MY_FB_ACCOUNT_MESSAGE = "👨‍💻 Możesz do mnie (twórcy) napisac na: https://www.facebook.com/dogsonjakub.nowak.7"

SUPPORT_INFO_MESSAGE = """🧧💰💎 Jeśli chcesz wspomóc prace nad botem, możesz wysłac donejta. Za każdą pomoc wielkie dzieki 💎💰🧧!
💴 Paypal: paypal.me/DogsonPL
💴 Konto bankowe: nr konta 22 1140 2004 0000 3002 7878 9413, Jakub Nowakowski
💴 Psc: wyślij kod na pv do !tworca"""

BOT_VERSION_MESSAGE = """❤DZIĘKUJĘ ZA ZAKUP WERSJI PRO!❤
🤖 Wersja bota: 7.8 + 9.0 pro 🤖

🧾 Ostatnio do bota dodano:
🆕 !lyrics
🆕 !profil (zamiast !stats)
🆕 LEGENDARNE DOGI, WIĘCEJ INFO PO UŻYCIU KOMENDY !bal
🆕 !play
🆕 !strona
"""

download_tiktok = page_parsing.DownloadTiktok()


class Commands(BotActions):
    def __init__(self, loop, bot_id, client):
        self.get_weather = page_parsing.GetWeather().get_weather
        self.downloading_videos = 0
        self.sending_say_messages = 0
        self.chats_where_making_disco = []
        super().__init__(loop, bot_id, client)

    @logger
    async def send_help_message(self, event):
        await self.send_text_message(event, HELP_MESSAGE)

    @logger
    async def send_link_to_creator_account(self, event):
        await self.send_text_message(event, LINK_TO_MY_FB_ACCOUNT_MESSAGE)

    @logger
    async def send_support_info(self, event):
        await self.send_text_message(event, SUPPORT_INFO_MESSAGE)

    @logger
    async def send_bot_version(self, event):
        await self.send_text_message(event, BOT_VERSION_MESSAGE)

    @logger
    async def send_user_id(self, event):
        await self.send_text_message(event, f"🆔 Twoje id to {event.author.id}")

    @logger
    async def send_webpage_link(self, event):
        await self.send_text_message(event, """🔗 Link do strony www: https://dogson.ovh. Strona jest w wersji beta

Żeby połączyć swoje dane z kasynem że stroną, ustaw w  bocie email za pomocą komendy !email, a potem załóż konto na stronie bota na ten sam email""")

    @logger
    async def send_weather(self, event):
        city = " ".join(event.message.text.split()[1:])
        if not city:
            message = "🚫 Po !pogoda podaj miejscowość z której chcesz mieć pogode, np !pogoda warszawa"
        else:
            message = await self.get_weather(city)
        await self.send_text_message(event, message)

    @logger
    async def send_covid_info(self, event):
        covid_info = await page_parsing.get_coronavirus_info()
        await self.send_text_message(event, covid_info)

    @logger
    async def send_covid_pl_info(self, event):
        covid_pl_info = await page_parsing.get_coronavirus_pl_info()
        await self.send_text_message(event, covid_pl_info)

    @logger
    async def send_public_transport_difficulties_in_warsaw(self, event):
        difficulties_in_warsaw = await page_parsing.get_public_transport_difficulties_in_warsaw()
        await self.send_text_message(event, difficulties_in_warsaw)

    @logger
    async def send_public_transport_difficulties_in_wroclaw(self, event):
        difficulties_in_wroclaw = await page_parsing.get_public_transport_difficulties_in_wroclaw()
        await self.send_text_message(event, difficulties_in_wroclaw)

    @logger
    async def send_public_transport_difficulties_in_lodz(self, event):
        difficulties_in_lodz = await page_parsing.get_public_transport_difficulties_in_lodz()
        await self.send_text_message(event, difficulties_in_lodz)

    @logger
    async def send_random_meme(self, event):
        meme_path, filetype = await getting_and_editing_files.get_random_meme()
        await self.send_file(event, meme_path, filetype)

    @logger
    async def send_random_film(self, event):
        film_path, filetype = await getting_and_editing_files.get_random_film()
        await self.send_file(event, film_path, filetype)

    @logger
    async def send_random_coin_side(self, event):
        film_path, filetype = await getting_and_editing_files.make_coin_flip()
        await self.send_file(event, film_path, filetype)

    @logger
    async def send_tvpis_image(self, event):
        text = event.message.text[6:]
        image, filetype = await self.loop.run_in_executor(None, getting_and_editing_files.edit_tvpis_image, text)
        await self.send_bytes_file(event, image, filetype)

    @logger
    async def send_tts(self, event):
        if self.sending_say_messages > 8:
            await self.send_text_message(event, "🚫 Bot obecnie wysyła za dużo wiadomości głosowych, poczekaj")
        else:
            self.sending_say_messages += 1
            text = event.message.text[4:]
            tts = await self.loop.run_in_executor(None, getting_and_editing_files.get_tts, text)
            await self.send_bytes_audio_file(event, tts)
            self.sending_say_messages -= 1

    @logger
    async def send_yt_video(self, event, yt_link):
        if self.downloading_videos > 8:
            await self.send_text_message(event, "🚫 Bot obecnie pobiera za dużo filmów. Spróbuj ponownie później")
        else:
            self.downloading_videos += 1
            link = yt_link
            video, filetype = await self.loop.run_in_executor(None, page_parsing.download_yt_video, link)
            await self.send_bytes_file(event, video, filetype)
            self.downloading_videos -= 1

    @logger
    async def convert_currency(self, event):
        message_data = event.message.text.split()
        try:
            amount = float(message_data[1])
            from_ = message_data[2].upper()
            to = message_data[3].upper()
        except (IndexError, ValueError):
            message = "💡 Użycie komendy: !waluta ilość z do - np !waluta 10 PLN USD zamienia 10 złoty na 10 dolarów (x musi być liczbą całkowitą)"
        else:
            try:
                converted_currency = float(currency_converter.convert(from_, to, 1))
            except RatesNotAvailableError:
                message = f"🚫 Podano niepoprawną walute"
            else:
                new_amount = "%.2f" % (converted_currency*amount)
                message = f"💲 {'%.2f' % amount} {from_} to {new_amount} {to}"
        await self.send_text_message(event, message)
        
    @logger
    async def send_random_question(self, event):
        question = rd.choice(questions)
        await self.send_text_message(event, question)

    @logger
    async def send_search_message(self, event):
        thing_to_search = event.message.text.split()[1:]
        if not thing_to_search:
            message = "💡 Po !szukaj podaj rzecz którą chcesz wyszukać"
        else:
            thing_to_search = "_".join(thing_to_search).title()
            if len(thing_to_search) > 50:
                message = "🚫 Za dużo znaków"
            else:
                message = await page_parsing.get_info_from_wikipedia(thing_to_search)
        await self.send_message_with_reply(event, message)

    @logger
    async def send_miejski_message(self, event):
        thing_to_search = event.message.text.split()[1:]
        if not thing_to_search:
            message = "💡 Po !miejski podaj rzecz którą chcesz wyszukać"
        else:
            thing_to_search = "+".join(thing_to_search).title()
            if len(thing_to_search) > 50:
                message = "🚫 Za dużo znaków"
            else:
                message = await page_parsing.get_info_from_miejski(thing_to_search)
        await self.send_message_with_reply(event, message)

    @logger
    async def send_translated_text(self, event):
        try:
            to = event.message.text.split("--")[1].split()[0]
            text = " ".join(event.message.text.split()[2:])
        except IndexError:
            to = "pl"
            text = " ".join(event.message.text.split()[1:])

        if not text or len(text) > 3000:
            translated_text = """💡 Po !tlumacz napisz co chcesz przetlumaczyc, np !tlumacz siema. Tekst może mieć maksymalnie 3000 znaków
Możesz tekst przetłumaczyć na inny język używająć --nazwa_jezyka, np !tlumacz --english siema"""
        else:
            try:
                translated_text = GoogleTranslator("auto", to).translate(text)
            except LanguageNotSupportedException:
                translated_text = f"🚫 {to} - nie moge znaleźć takiego języka, spróbuj wpisać pełną nazwe języka"
            except NotValidPayload:
                translated_text = "🚫 Nie można przetłumaczyć tego tekstu"

        if not translated_text:
            translated_text = "🚫 Nie można przetłumaczyć znaku który został podany"
        await self.send_message_with_reply(event, translated_text)

    @logger
    async def send_google_image(self, event):
        search_query = event.message.text.split()[1:]
        if not search_query:
            await self.send_message_with_reply(event, "💡 Po !zdjecie napisz czego chcesz zdjęcie, np !zdjecie pies")
        else:
            search_query = "%20".join(search_query)
            if len(search_query) > 100:
                await self.send_message_with_reply(event, "🚫 Podano za długą fraze")
            else:
                image = await page_parsing.get_google_image(search_query)
                await self.send_bytes_file(event, image, "image/png")

    @logger
    async def send_tiktok(self, event):
        self.downloading_videos += 1
        for i in event.message.text.split():
            if i.startswith("https://vm.tiktok.com/"):
                video = await download_tiktok.download_tiktok(i)
                await self.send_bytes_file(event, video, "video/mp4")
                break
        self.downloading_videos -= 1

    @logger
    async def send_spotify_song(self, event):
        if self.sending_say_messages > 8:
            await self.send_message_with_reply(event, "🚫 Bot obecnie pobiera za dużo piosenek, poczekaj spróbuj ponownie za jakiś czas")
        else:
            song_name = event.message.text.split()[1:]
            if not song_name:
                await self.send_message_with_reply(event, "💡 Po !play wyślij link do piosenki, albo nazwe piosenki. Pamiętaj że wielkość liter ma znaczenie, powinna być taka sama jak w tytule piosenki na spotify")
                return
            
            song_name = "".join(song_name)
            if len(song_name) > 150:
                await self.send_message_with_reply(event, "🚫 Za długa nazwa piosenki")
                return
            
            if "open.spotify.com/playlist" in song_name.lower() or "open.spotify.com/episode" in song_name.lower() or "open.spotify.com/artist" in song_name.lower() or "open.spotify.com/album" in song_name.lower():
                await self.send_text_message(event, "🚫 Można wysyłać tylko linki do piosenek")
                return

            self.sending_say_messages += 2
            song = await self.loop.run_in_executor(None, page_parsing.download_spotify_song, song_name)
            await self.send_bytes_audio_file(event, song)
            self.sending_say_messages -= 2

    @logger
    async def send_banana_message(self, event):
        mentioned_person = event.message.mentions
        banana_size = rd.randint(-100, 100)
        if mentioned_person:
            mentioned_person_name = event.message.text[8:event.message.mentions[0].length+7]
            message = f"🍌 Banan {mentioned_person_name} ma {banana_size} centymetrów"
        else:
            message = f"🍌 Twój banan ma {banana_size} centymetrów"
        await self.send_message_with_reply(event, message)

    @logger
    async def send_product_price(self, event):
        item = event.message.text[6:]
        item_query_len = len(item)
        if item_query_len == 0 or item_query_len > 200:
            message = "💡 Po !cena podaj nazwe przedmiotu (np !cena twoja stara) którego cene chcesz wyszukać, może miec max 200 znaków"
        else:
            message = await page_parsing.check_item_price(item.replace(' ', '+'))
            if not message:
                message = f"🚫 Nie można odnaleźć {item} :("
        await self.send_text_message(event, message)

    @logger
    async def send_song_lyrics(self, event):
        try:
            args = event.message.text.split(",")
            creator_ = args[0].split()[1:]
            creator = " ".join(creator_).replace(" ", "-")
            song_name = args[1].replace(" ", "-").replace("(", "-").replace(")", "")
        except IndexError:
            lyrics = "💡 Wygląd komendy: !lyrics twórca, tytuł piosenki (nie używaj polskich znaków)\nPrzykład: !tworca chivas, mam na twarzy krew i tym razem nie jest sztuczna"
        else:
            lyrics = await page_parsing.get_lyrics(creator, song_name)
            if not lyrics:
                lyrics = "😢 Nie udało się odnaleźć tekstu do piosenki"
            if len(lyrics) > 3000:
                lyrics = lyrics[0:3500]
                lyrics += "\n\n[...] Za długi tekst piosenki (messenger ogranicza wielkość wiadomości"
        await self.send_text_message(event, lyrics)

    @logger
    async def make_disco(self, event):
        thread_id = event.thread.id
        if thread_id in self.chats_where_making_disco:
            await self.send_text_message(event, "🎇🎈 Rozkręcam właśnie imprezę")
        else:
            self.chats_where_making_disco.append(event.thread.id)
            for _ in range(12):
                color = rd.choice(SETABLE_COLORS)
                await event.thread.set_color(color)
            self.chats_where_making_disco.remove(thread_id)

    @logger
    async def change_nick(self, event):
        try:
            await event.thread.set_nickname(user_id=event.author.id, nickname=" ".join(event.message.text.split()[1:]))
        except fbchat.InvalidParameters:
            await self.send_text_message(event, "🚫 Wpisano za długi nick")
