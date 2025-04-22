import random as rd
import asyncio
import json
from datetime import datetime, timedelta
from typing import Union, Tuple

import fbchat
from currency_converter import CurrencyConverter
from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException, NotValidPayload
from dataclasses import dataclass

from .logger import logger
from .. import getting_and_editing_files, page_parsing
from .bot_actions import BotActions
from ..sql import handling_group_sql


SETABLE_COLORS = fbchat._threads.SETABLE_COLORS
currency_converter = CurrencyConverter()
questions = []
with open("Bot/data/questions.txt") as file:
    for i in file.readlines():
        questions.append(i)


HELP_MESSAGE = """🎉 𝐊𝐎𝐌𝐄𝐍𝐃𝐘 🎉
!help, !strona, !wersja, !wsparcie, !tworca, !id, !mem, !luckymember, !ruletka, !pogoda, !nick, !everyone, !utrudnieniawawa, !utrudnienialodz, !utrudnieniapoznan, !utrudnieniatroj, !moneta, !waluta, !kocha, !banan, !tekst , !stan , !tablica, !pytanie, !essa, !flagi, !kiedy, !leosia
💎 𝐃𝐎𝐃𝐀𝐓𝐊𝐎𝐖𝐄 𝐊𝐎𝐌𝐄𝐍𝐃𝐘 𝐙𝐀 𝐙𝐀𝐊𝐔𝐏 𝐖𝐄𝐑𝐒𝐉𝐈 𝐏𝐑𝐎 💎
!szukaj, !tlumacz, !miejski, !film, !tvpis, !disco, !powitanie, !nowyregulamin, !regulamin, !zdjecie, !play, !cena, !sstats, !say, !ai
💰 𝐊𝐎𝐌𝐄𝐍𝐃𝐘 𝐃𝐎 𝐆𝐑𝐘 𝐊𝐀𝐒𝐘𝐍𝐎 (𝐝𝐨𝐠𝐞𝐜𝐨𝐢𝐧𝐬𝐲 𝐧𝐢𝐞 𝐬𝐚 𝐩𝐫𝐚𝐰𝐝𝐳𝐢𝐰𝐞 𝐢 𝐧𝐢𝐞 𝐝𝐚 𝐬𝐢𝐞 𝐢𝐜𝐡 𝐰𝐲𝐩ł𝐚𝐜𝐢𝐜)💰 
!register, !daily, !top, !bal, !bet, !zdrapka, !tip, !jackpot, !jackpotbuy, !duel, !email, !kod, !profil, !osiagniecia, !sklep, !slots
"""

LINK_TO_MY_FB_ACCOUNT_MESSAGE = "👨‍💻 Możesz do mnie (twórcy) napisać na: https://www.facebook.com/dogson420"

SUPPORT_INFO_MESSAGE = """🧧💰💎 𝐉𝐞𝐬𝐥𝐢 𝐜𝐡𝐜𝐞𝐬𝐳 𝐰𝐬𝐩𝐨𝐦𝐨𝐜 𝐩𝐫𝐚𝐜𝐞 𝐧𝐚𝐝 𝐛𝐨𝐭𝐞𝐦, 𝐦𝐨𝐳𝐞𝐬𝐳 𝐰𝐲𝐬𝐥𝐚𝐜 𝐝𝐨𝐧𝐞𝐣𝐭𝐚. 𝐙𝐚 𝐤𝐚𝐳𝐝𝐚 𝐩𝐨𝐦𝐨𝐜 𝐰𝐢𝐞𝐥𝐤𝐢𝐞 𝐝𝐳𝐢𝐞𝐤𝐢 💎💰🧧!
💴 𝙋𝙖𝙮𝙥𝙖𝙡: paypal.me/DogsonPL
💴 𝙆𝙤𝙣𝙩𝙤 𝙗𝙖𝙣𝙠𝙤𝙬𝙚: nr konta 22 1140 2004 0000 3002 7878 9413, Jakub Nowakowski
💴 𝙋𝙨𝙘: wyślij kod na pv do !tworca"""

BOT_VERSION_MESSAGE = """❤𝐃𝐙𝐈𝐄𝐊𝐔𝐉𝐄 𝐙𝐀 𝐙𝐀𝐊𝐔𝐏 𝐖𝐄𝐑𝐒𝐉𝐈 𝐏𝐑𝐎!❤
🤖 𝐖𝐞𝐫𝐬𝐣𝐚 𝐛𝐨𝐭𝐚: 9.9 + 14.0 pro 🤖

🧾 𝐎𝐬𝐭𝐚𝐭𝐧𝐢𝐨 𝐝𝐨 𝐛𝐨𝐭𝐚 𝐝𝐨𝐝𝐚𝐧𝐨:
🆕 !ai
🆕 !utrudnieniatroj, utrudnieniapoznan
🆕 !pogoda -f
Ograniczona ilość wysyłanych wiadomości
"""

download_tiktok = page_parsing.DownloadTiktok()

MARIJUANA_MESSAGES = ["Nie zjarany/a", "Po kilku buszkach", "Niezłe gastro, zjadł/a całą lodówkę i zamówił/a dwie duże pizze",
                      "Pierdoli coś o kosmitach", "Słodko śpi", "Badtrip :(", "Spierdala przed policją",
                      "Jara właśnie", "Gotuje wesołe ciasteczka", "Mati *kaszle* widać po *kaszle* mnie?",
                      "Mocno wyjebało, nie ma kontaktu", "Jest w swoim świecie", "xDDDDDDDDDDDDDDD", "JD - jest z nim/nią dobrze",
                      "Wali wiadro", "Wesoły", "Najwyższy/a w pokoju", "Mówi że lubi jeździć na rowerze samochodem",
                      "*kaszlnięcie*, *kaszlnięcie*, *kaszlnięcie*", "Kometa wpadła do buzi, poterzny bul"]

leosia_quotes = []
with open("Bot/media/leosia.txt", "r") as file:
    for i in file.readlines():
        leosia_quotes.append(i.strip())


@dataclass
class FlagsGame:
    time: datetime.date
    answer: Union[str, list]
    message_id: str


with open("Bot/data/flags.json", "r") as file:
    FLAGS = json.load(file)

flags_game = {}


class Commands(BotActions):
    def __init__(self, client: fbchat.Client, bot_id: str, loop: asyncio.AbstractEventLoop):
        self.get_weather = page_parsing.GetWeather()
        self.downloading_videos = 0
        self.sending_say_messages = 0
        self.chats_where_making_disco = []
        super().__init__(client, bot_id, loop)

    @logger
    async def send_help_message(self, event: fbchat.MessageEvent):
        await self.send_text_message(event, HELP_MESSAGE)

    @logger
    async def send_leosia_message(self, event: fbchat.MessageEvent):
        message = rd.choice(leosia_quotes)
        await self.send_text_message(event, f"Przekaz od królowej 😄\n{message}\n")

    @logger
    async def send_link_to_creator_account(self, event: fbchat.MessageEvent):
        await self.send_text_message(event, LINK_TO_MY_FB_ACCOUNT_MESSAGE)

    @logger
    async def send_support_info(self, event: fbchat.MessageEvent):
        await self.send_text_message(event, SUPPORT_INFO_MESSAGE)

    @logger
    async def send_bot_version(self, event: fbchat.MessageEvent):
        await self.send_text_message(event, BOT_VERSION_MESSAGE)

    @logger
    async def send_user_id(self, event: fbchat.MessageEvent):
        await self.send_text_message(event, f"🆔 Twoje id to {event.author.id}")

    @logger
    async def send_webpage_link(self, event: fbchat.MessageEvent):
        await self.send_text_message(event, """🔗 Link do strony www: https://dogson.ovh

Żeby połączyć swoje dane z kasynem że stroną, ustaw w  bocie email za pomocą komendy !email, a potem załóż konto na stronie bota na ten sam email""")

    @logger
    async def send_ai(self, event: fbchat.MessageEvent):
        prompt = " ".join(event.message.text.split()[1:])
        if not prompt:
            await self.send_text_message(event, "🚫 Po !ai zadaj pytanie, np ile to 1+1", reply_to_id=event.message.id)
        else:
            response = await self.loop.run_in_executor(None, page_parsing.ai, prompt)
            for i in range(0, len(response), 2000):
                await self.send_text_message(event, response[i:i+2000], reply_to_id=event.message.id)


    @logger
    async def send_weather(self, event: fbchat.MessageEvent):
        city = " ".join(event.message.text.split()[1:])
        if not city:
            message = "🚫 Po !pogoda podaj miejscowość z której chcesz mieć pogodę, np !pogoda warszawa"
        else:
            if "-f" in city:
                message = await self.get_weather.get_forecast(" ".join(city.split()[1:]))
            else:
                message = await self.get_weather.get_weather(city)
        await self.send_text_message(event, message)

    @logger
    async def send_public_transport_difficulties_in_warsaw(self, event: fbchat.MessageEvent):
        difficulties_in_warsaw = await page_parsing.get_public_transport_difficulties_in_warsaw()
        await self.send_text_message(event, difficulties_in_warsaw)

    @logger
    async def send_public_transport_difficulties_in_lodz(self, event: fbchat.MessageEvent):
        difficulties_in_lodz = await page_parsing.get_public_transport_difficulties_in_lodz()
        await self.send_text_message(event, difficulties_in_lodz)

    @logger
    async def send_public_transport_difficulties_in_poznan(self, event: fbchat.MessageEvent):
        difficulties_in_poznan = await page_parsing.get_public_transport_difficulties_in_poznan()
        await self.send_text_message(event, difficulties_in_poznan)

    @logger
    async def send_public_transport_difficulties_in_trojmiasto(self, event: fbchat.MessageEvent):
        difficulties_in_trojmiasto = await page_parsing.get_public_transport_difficulties_in_trojmiasto()
        await self.send_text_message(event, difficulties_in_trojmiasto)

    @logger
    async def send_random_meme(self, event: fbchat.MessageEvent):
        meme_path, filetype = await getting_and_editing_files.get_random_meme()
        await self.send_file(event, meme_path, filetype)

    @logger
    async def send_random_film(self, event: fbchat.MessageEvent):
        film_path, filetype = await getting_and_editing_files.get_random_film()
        await self.send_file(event, film_path, filetype)

    @logger
    async def send_random_coin_side(self, event: fbchat.MessageEvent):
        film_path, filetype = await getting_and_editing_files.make_coin_flip()
        await self.send_file(event, film_path, filetype)

    @logger
    async def send_tvpis_image(self, event: fbchat.MessageEvent):
        text = event.message.text[6:]
        image, filetype = await self.loop.run_in_executor(None, getting_and_editing_files.edit_tvpis_image, text)
        await self.send_bytes_file(event, image, filetype)

    @logger
    async def send_tts(self, event: fbchat.MessageEvent):
        if self.sending_say_messages > 8:
            await self.send_text_message(event, "🚫 Bot obecnie wysyła za dużo wiadomości głosowych, poczekaj")
        else:
            self.sending_say_messages += 1
            text = event.message.text[4:]
            tts = await self.loop.run_in_executor(None, getting_and_editing_files.get_tts, text)
            await self.send_bytes_audio_file(event, tts)
            self.sending_say_messages -= 1

    @logger
    async def send_yt_video(self, event: fbchat.MessageEvent, yt_link: str):
        if self.downloading_videos > 8:
            await self.send_text_message(event, "🚫 Bot obecnie pobiera za dużo filmów. Spróbuj ponownie później")
        else:
            self.downloading_videos += 1
            link = yt_link
            video, filetype = await self.loop.run_in_executor(None, page_parsing.download_yt_video, link)
            await self.send_bytes_file(event, video, filetype)
            self.downloading_videos -= 1

    @logger
    async def convert_currency(self, event: fbchat.MessageEvent):
        message_data = event.message.text.split()
        try:
            amount = float(message_data[1])
            from_ = message_data[2].upper()
            to = message_data[3].upper()
        except (IndexError, ValueError):
            message = "💡 Użycie komendy: !waluta ilość z do - np !waluta 10 PLN USD zamienia 10 złoty na 10 dolarów (x musi być liczbą całkowitą)"
        else:
            try:
                converted_currency = float(currency_converter.convert(1, from_, to))
            except ValueError:
                message = f"🚫 Podano niepoprawną walutę"
            else:
                new_amount = "%.2f" % (converted_currency*amount)
                message = f"💲 {'%.2f' % amount} {from_} to {new_amount} {to}"
        await self.send_text_message(event, message)
        
    @logger
    async def send_random_question(self, event: fbchat.MessageEvent):
        question = rd.choice(questions)
        await self.send_text_message(event, question)

    @logger
    async def send_search_message(self, event: fbchat.MessageEvent):
        thing_to_search = event.message.text.split()[1:]
        if not thing_to_search:
            message = "💡 Po !szukaj podaj rzecz którą chcesz wyszukać"
        else:
            thing_to_search = "_".join(thing_to_search).title()
            if len(thing_to_search) > 50:
                message = "🚫 Za dużo znaków"
            else:
                message = await page_parsing.get_info_from_wikipedia(thing_to_search)
        await self.send_text_message(event, message, reply_to_id=event.message.id)

    @logger
    async def send_miejski_message(self, event: fbchat.MessageEvent):
        thing_to_search = event.message.text.split()[1:]
        if not thing_to_search:
            message = "💡 Po !miejski podaj rzecz którą chcesz wyszukać"
        else:
            thing_to_search = "+".join(thing_to_search).title()
            if len(thing_to_search) > 50:
                message = "🚫 Za dużo znaków"
            else:
                message = await page_parsing.get_info_from_miejski(thing_to_search)
        await self.send_text_message(event, message, reply_to_id=event.message.id)

    @logger
    async def send_translated_text(self, event: fbchat.MessageEvent):
        try:
            to = event.message.text.split("--")[1].split()[0]
            text = " ".join(event.message.text.split()[2:])
        except IndexError:
            to = "pl"
            text = " ".join(event.message.text.split()[1:])

        if not text or len(text) > 3000:
            translated_text = """💡 Po !tlumacz napisz co chcesz przetłumaczyć, np !tlumacz siema. Tekst może mieć maksymalnie 3000 znaków
Możesz tekst przetłumaczyć na inny język używająć --nazwa_jezyka, np !tlumacz --english siema"""
        else:
            try:
                translated_text = GoogleTranslator("auto", to).translate(text)
            except LanguageNotSupportedException:
                translated_text = f"🚫 {to} - nie moge znaleźć takiego języka, spróbuj wpisać pełną nazwę języka"
            except NotValidPayload:
                translated_text = "🚫 Nie można przetłumaczyć tego tekstu"

        if not translated_text:
            translated_text = "🚫 Nie można przetłumaczyć znaku który został podany"
        await self.send_text_message(event, translated_text, reply_to_id=event.message.id)

    @logger
    async def send_google_image(self, event: fbchat.MessageEvent):
        search_query = event.message.text.split()[1:]
        if not search_query:
            await self.send_text_message(event, "💡 Po !zdjecie napisz czego chcesz zdjęcie, np !zdjecie pies",
                                         reply_to_id=event.message.id)
        else:
            search_query = "%20".join(search_query)
            if len(search_query) > 100:
                await self.send_text_message(event, "🚫 Podano za długą fraze", reply_to_id=event.message.id)
            else:
                image = await page_parsing.get_google_image(search_query)
                await self.send_bytes_file(event, image, "image/png")

    @logger
    async def send_tiktok(self, event: fbchat.MessageEvent):
        self.downloading_videos += 1
        for i in event.message.text.split():
            if i.startswith("https://vm.tiktok.com/"):
                video, data_type = await download_tiktok.download_tiktok(i)
                try:
                    await self.send_bytes_file(event, video, data_type)
                except fbchat.HTTPError:
                    await self.send_text_message(event, "🚫 Facebook zablokował wysłanie tiktoka, spróbuj jeszcze raz",
                                                 reply_to_id=event.message.id)
                break
        self.downloading_videos -= 1

    @logger
    async def send_spotify_song(self, event: fbchat.MessageEvent):
        if self.sending_say_messages > 5:
            await self.send_text_message(event, "🚫 Bot obecnie pobiera za dużo piosenek, poczekaj spróbuj ponownie za jakiś czas",
                                         reply_to_id=event.message.id)
        else:
            song_name = event.message.text.split()[1:]
            if not song_name:
                await self.send_text_message(event, "💡 Po !play wyślij link do piosenki, albo nazwe piosenki. Pamiętaj że wielkość liter ma znaczenie, powinna być taka sama jak w tytule piosenki na spotify",
                                             reply_to_id=event.message.id)
                return
            
            song_name = "".join(song_name)
            if len(song_name) > 150:
                await self.send_text_message(event, "🚫 Za długa nazwa piosenki", reply_to_id=event.message.id)
                return
            
            if "open.spotify.com/playlist" in song_name.lower() or "open.spotify.com/episode" in song_name.lower() or "open.spotify.com/artist" in song_name.lower() or "open.spotify.com/album" in song_name.lower():
                await self.send_text_message(event, "🚫 Można wysyłać tylko linki do piosenek")
                return

            self.sending_say_messages += 2
            song = await self.loop.run_in_executor(None, page_parsing.download_spotify_song, song_name)
            await self.send_bytes_audio_file(event, song)
            self.sending_say_messages -= 2

    @logger
    async def send_banana_message(self, event: fbchat.MessageEvent):
        mentioned_person = event.message.mentions
        banana_size = rd.randint(-100, 100)
        if mentioned_person:
            mentioned_person_name = event.message.text[8:event.message.mentions[0].length+7]
            message = f"🍌 Banan {mentioned_person_name} ma {banana_size} centymetrów"
        else:
            message = f"🍌 Twój banan ma {banana_size} centymetrów"
        await self.send_text_message(event, message, reply_to_id=event.message.id)

    @logger
    async def send_product_price(self, event: fbchat.MessageEvent):
        item = event.message.text[6:]
        item_query_len = len(item)
        if item_query_len == 0 or item_query_len > 200:
            message = "💡 Po !cena podaj nazwe przedmiotu (np !cena twoja stara) którego cene chcesz wyszukać, może miec max 200 znaków"
        else:
            message = await page_parsing.check_item_price(item.replace(' ', '+'))
            if not message:
                message = f"🚫 Nie można odnaleźć {item} :("
        await self.send_text_message(event, message, reply_to_id=event.message.id)

    @logger
    async def send_song_lyrics(self, event: fbchat.MessageEvent):
        lyrics = "💡 Wygląd komendy: !tekst tytuł piosenki; twórca\nPrzykład: !lyrics mam na twarzy krew i tym razem nie jest sztuczna; chivas"
        args = event.message.text.split(";")
        try:
            song_name_ = args[0].split()[1:]
            song_name = " ".join(song_name_).replace(" ", "+")
        except IndexError:
            song_name = False
        try:
            creator = args[1].replace(" ", "+")
        except IndexError:
            creator = ""

        if song_name:
            lyrics = await page_parsing.get_lyrics(creator, song_name)
            if not lyrics:
                lyrics = "😢 Nie udało się odnaleźć tekstu do piosenki"
            if len(lyrics) > 4000:
                lyrics = lyrics[0:4000]
                lyrics += "\n\n[...] Za długi tekst piosenki (messenger ogranicza wielkość wiadomości)"
        await self.send_text_message(event, lyrics, reply_to_id=event.message.id)

    @logger
    async def send_stan_message(self, event: fbchat.MessageEvent):
        mentioned_person = event.message.mentions
        alcohol_level = round(rd.uniform(0, 5), 2)
        marijuana_message = rd.choice(MARIJUANA_MESSAGES)
        if mentioned_person:
            mentioned_person_name = event.message.text[7:event.message.mentions[0].length+6]
            message = f"✨ Stan {mentioned_person_name}: ✨"
        else:
            message = f"✨ 𝗧𝘄𝗼𝗷 𝘀𝘁𝗮𝗻: ✨"
        message += f"""
🍻 𝐏𝐫𝐨𝐦𝐢𝐥𝐞: {alcohol_level}‰ 
☘ 𝐙𝐣𝐚𝐫𝐚𝐧𝐢𝐞: {marijuana_message}"""
        await self.send_text_message(event, message, reply_to_id=event.message.id)

    @logger
    async def send_registration_number_info(self, event: fbchat.MessageEvent):
        try:
            registration_number = "".join(event.message.text.split()[1:])
        except IndexError:
            registration_number_info = "💡 Po !tablica podaj numer rejestracyjny"
        else:
            registration_number_info = await page_parsing.get_vehicle_registration_number_info(registration_number)
        await self.send_text_message(event, registration_number_info)

    @logger
    async def send_play_flags_message(self, event: fbchat.MessageEvent):
        message, reply_to = await play_flags(event)
        await self.send_text_message(event, message, reply_to_id=reply_to)

    @logger
    async def send_essa_message(self, event: fbchat.MessageEvent):
        mentioned_person = event.message.mentions
        essa_percent = rd.randint(0, 100)
        if mentioned_person:
            mentioned_person_name = event.message.text[7:event.message.mentions[0].length + 6]
            message = f"{mentioned_person_name} ma {essa_percent}% essy 🤙"
        else:
            message = f"Masz  {essa_percent}% essy 🤙"
        await self.send_text_message(event, message, reply_to_id=event.message.id)

    @logger
    async def send_when_date(self, event: fbchat.MessageEvent):
        message = await calculate_days(event.message.text)
        await self.send_text_message(event, message, reply_to_id=event.message.id)

    @logger
    async def make_disco(self, event: fbchat.MessageEvent):
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
    async def change_nick(self, event: fbchat.MessageEvent):
        try:
            await event.thread.set_nickname(user_id=event.author.id, nickname=" ".join(event.message.text.split()[1:]))
        except fbchat.InvalidParameters:
            await self.send_text_message(event, "🚫 Wpisano za długi nick", reply_to_id=event.message.id)


async def play_flags(event: fbchat.MessageEvent) -> Tuple[str, Union[str, None]]:
    answer = flags_game.get(event.thread.id)
    if answer and answer.time + timedelta(minutes=10) > datetime.now():
        country = event.message.text[6:].lower().strip()
        if not country:
            return "💡 Po !flagi podaj nazwę kraju, do którego należy ta flaga", answer.message_id

        good_answer = False
        if isinstance(answer.answer, str):
            if country == answer.answer:
                good_answer = True
        else:
            for i in answer.answer:
                if i == country:
                    good_answer = True
                    break
        if good_answer:
            user_points = await handling_group_sql.get_user_flags_wins(event.author.id)
            try:
                user_points += 1
            except TypeError:
                return "💡 Użyj polecenia !register żeby móc się bawić w kasyno. Wszystkie dogecoiny są sztuczne", event.message.id
            else:
                await handling_group_sql.set_user_flags_wins(event.author.id, user_points)
                del flags_game[event.thread.id]
                return f"👍 Dobra odpowiedź! Posiadasz już {user_points} dobrych odpowiedzi", event.message.id
        else:
            return "👎 Zła odpowiedź", event.message.id
    flag, answer = rd.choice(list(FLAGS.items()))
    flags_game[event.thread.id] = FlagsGame(datetime.now(), answer, event.message.id)
    return f"Flaga do odgadnięcia {flag}\nNapisz !flagi nazwa_państwa", None

months = {
    "styczeń": 1,
    "styczen": 1,
    "luty": 2,
    "marzec": 3,
    "kwiecień": 4,
    "kwiecien": 4,
    "maj": 5,
    "czerwiec": 6,
    "lipiec": 7,
    "sierpień": 8,
    "sierpien": 8,
    "wrzesień": 9,
    "wrzesien": 9,
    "październik": 10,
    "pazdziernik": 10,
    "listopad": 11,
    "grudzień": 12,
    "grudzien": 12
}

async def calculate_days(date: str) -> str:
    now = datetime.today()
    try:
        date = date.split()
        month = months[date[2]]
        day = int(date[1])
        year = int(date[3])
        date = datetime(year, month, day)
    except (ValueError, KeyError, IndexError):
        return "💡 Zła data. Data powinna mieć format: !kiedy 1 styczeń/luty/marzec... 2023/2024 (słowa typu stycznia nie są akceptowane)"
    days = (date - now).days + 1
    if days < 0:
        return f"Podana data była {abs(days)} dni temu"
    elif days > 0:
        return f"Podana data będzie za {days} dni"
    else:
        return "To dzisiejsza data"
