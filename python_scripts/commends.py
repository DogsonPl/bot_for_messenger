import fbchat
import feedparser
import aiohttp
from bs4 import BeautifulSoup
from gtts import gTTS
import random as rd
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from python_scripts.sending_actions import *
from python_scripts import sql_actions


# todo MAKE BS4 AND FEEDPARSER ASYNCHRONOUS

SETABLE_COLORS = fbchat._threads.SETABLE_COLORS
MEMES_FILES = os.listdir("data//memes")
FILMS_FILES = os.listdir("data//films")
FONT = ImageFont.truetype("data//fonts/FallingSkySemibold-Bn7B.otf", 15)
WEATHER_API_ADDRESS = "http://api.openweathermap.org/data/2.5/weather?appid=48cf48dbb3891862735dd16b01a3a62f&q="


@send_text_message
async def get_help_message(event):
    return """Komendy:\n
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
!mute - wycisza głupie odzywki bota na np 'co'\n
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


@send_text_message
async def get_link_to_creator_account(event):
    return "Możesz do mnie (twórcy) napisac na: https://www.facebook.com/dogsonjakub.nowak.7"


@send_text_message
async def get_support_info(event):
    return """Jeśli chcesz wspomóc prace nad botem, możesz wysłac donejta. Za kazdą pomoc wielkie dzieki!
Paypal: paypal.me/DogsonPL
Konto bankowe: nr konta 22 1140 2004 0000 3002 7878 9413, Jakub Nowakowski
Psc: wyslij kod na pv do !tworca"""


@send_text_message
async def get_bot_version(event):
    return """DZIĘKUJĘ ZA ZAKUP WERSJI PRO! Wersja bota: 4.0 + 7.1 pro
Ostatnio do bota dodano:
!para została usunięta
!everyone jest dostępne tylko dla adminów
Dodano komende !off
Usunieto funkcje !unmute i została zastąpiona komendą !mute (teraz ta komenda odmutowuje i mutuje)
Dodano komende !tvpis"""


@send_text_message
async def get_weather(event):

    city = event.message.text[8:]
    url = WEATHER_API_ADDRESS + city
    async with aiohttp.ClientSession() as session:
        html = await session.get(url)
    json_data = await html.json()

    try:
        temperature = json_data["main"]["temp"]
        temperature -= 273  # convert to Celsius
        perceptible_temperature = json_data["main"]["feels_like"]
        perceptible_temperature -= 273  # convert to Celsius
        weather_description = json_data["weather"][0]["description"]
        pressure = json_data["main"]["pressure"]
        humidity = json_data["main"]["humidity"]
        wind_speed = json_data["wind"]["speed"]
        return f"""Pogoda w {city.title()}
Temperatura: {int(temperature)}C 
Odczuwalna: {int(perceptible_temperature)}C
Atmosfera: {weather_description} 
Ciśnienie: {pressure} hPa
Wilgotność: {humidity} %
Prędkość wiatru: {wind_speed} m/s"""
    except KeyError:
        return "Nie znaleziono takiej miejscowości"


@send_text_message
async def get_coronavirus_info(event):
    async with aiohttp.ClientSession() as session:
        html = await session.get("https://coronavirus-19-api.herokuapp.com/all")
    data = await html.json()

    try:
        return f"""Koronawirus na świecie
Potwierdzonych: {data['cases']}
Śmierci: {data['deaths']}
Uleczonych: {data['recovered']}
Chore osoby w tej chwili: {data['cases'] - data['deaths'] - data['recovered']}"""
    except KeyError:
        return "Błąd API. Spróbuj ponownie za kilka minut"


@send_text_message
async def get_coronavirus_pl_info(event):
    async with aiohttp.ClientSession() as session:
        html = await session.get("https://coronavirus-19-api.herokuapp.com/countries/poland")
    data = await html.json()

    try:
        return f"""Koronawirus w Polsce
Potwierdzonych: {data['cases']}
Dzisiaj potwierdzono: {data['todayCases']}
Śmierci: {data['deaths']}
Uleczonych: {data['recovered']}
Chore osoby w tej chwili: {data['active']}
Liczba chorych na milion osób: {data['casesPerOneMillion']}
Śmiertelne przypadki na milion osób: {data['deathsPerOneMillion']}
Liczba zrobionych testów: {data['totalTests']}
Liczba testów na milion osób: {data['testsPerOneMillion']}"""
    except KeyError:
        return "Błąd API. Spróbuj ponownie za kilka minut"


@send_text_message
async def get_public_transport_difficulties_in_warsaw(event):
    feed = feedparser.parse('https://www.wtp.waw.pl/feed/?post_type=impediment')
    message = ""
    # todo make asynchronous
    for entry in feed['entries']:
        message += entry.title
        async with aiohttp.ClientSession() as session:
            html = await session.get(entry.link)
            soup = BeautifulSoup(await html.text(), "html.parser")
        for i in soup.find_all("div", class_="impediment-content"):
            message += i.text + "\n"
    if message == "":
        return "Brak utrudnień w Warszawie :) Więcej informacji na https://www.wtp.waw.pl"
    return message


@send_text_message
async def get_public_transport_difficulties_in_wroclaw(event):
    async with aiohttp.ClientSession() as session:
        html = await session.get("https://www.facebook.com/mpkwroc/")
        soup = BeautifulSoup(await html.text(), "html.parser")

    message = "Dane z fb MPK Wrocław\n"
    # todo make asynchronous
    for i in soup.find_all("p"):
        message += i.text + "\n"
    return message


@send_text_message
async def get_public_transport_difficulties_in_lodz(event):
    async with aiohttp.ClientSession() as session:
        html = await session.get("http://www.mpk.lodz.pl/rozklady/utrudnienia.jsp")
        soup = BeautifulSoup(await html.text(), "html.parser")

    message = "Właścicielami danych jest http://www.mpk.lodz.pl/rozklady/utrudnienia.jsp\n"
    # todo make asynchronous
    for i in soup.find_all("p"):
        if "mpk na facebook" in i.text.lower():
            message += "\n"
        elif "Zamknij" in i.text:
            break
        else:
            message += i.text + "\n"
    return message


@send_text_message_with_mentions
async def get_and_mention_random_member(event, client):
    group = await client.fetch_thread_info([event.thread.id]).__anext__()
    lucky_member = rd.choice(group.participants).id
    mention = [fbchat.Mention(thread_id=lucky_member, offset=0, length=9)]
    return "Zwycięzca", mention


@send_file
async def get_meme():
    drawn_meme = rd.choice(MEMES_FILES)
    return "data//memes//" + drawn_meme, "image/png"


@send_file
async def get_film():
    drawn_film = rd.choice(FILMS_FILES)
    return "data//films//" + drawn_film, "video/mp4"


@send_file
async def make_coin_flip():
    selected = rd.choice(["data//orzel_reszka//orzel.png", "data//orzel_reszka//reszka.png"])
    return selected, "image/png"


@send_bytes_file
async def get_tvpis_image(event):
    # todo run in executor and try async
    if event.message.text == "!tvpis":
        return "Napisz coś po !tvpis, np !tvpis jebać pis", None

    if len(event.message.text) > 46:
        text = event.message.text[6:46].upper()
    else:
        text = event.message.text[6:].upper()

    tvpis_image = Image.open("data//tvpis//img.png")
    draw = ImageDraw.Draw(tvpis_image)
    draw.text((72, 176), text, (255, 255, 255), FONT)
    bytes_image = BytesIO()
    tvpis_image.save(bytes_image, format='PNG')
    return bytes_image, "image/jpeg"


@send_bytes_audio_file
def get_tts(event):
    # todo run this in executor and try async tts
    if len(event.message.text) > 2004:
        return "Wiadomość może mieć maksymalnie 2000 znaków (musiałem zrobić te ograniczenie bo bot się za bardzo lagował)"
    if event.message.text == "!say":
        return "Po !say napisz coś co ma powiedzieć bot, np !say elo"

    tts = gTTS(event.message.text[4:], lang="pl")
    bytes_object = BytesIO()
    try:
        tts.write_to_fp(bytes_object)
    except AssertionError:
        return "Podano niepoprawne znaki"
    return bytes_object


@group_actions
async def delete_random_person(event, group_info, bot_id):
    member_to_kick = rd.choice(group_info.participants).id
    if member_to_kick in group_info.admins:
        await event.thread.send_text("Wylosowalo admina. Nie moge go usunąć")
    elif member_to_kick == bot_id:
        await event.thread.send_text("Wylosowało mnie")
    else:
        try:
            await event.thread.remove_participant(member_to_kick)
        except fbchat.InvalidParameters:
            await event.thread.send_text("Żeby działała ta funkcja na grupie, muszę mieć admina")


@group_actions
@send_text_message
async def set_welcome_message(event, group_info):
    if event.message.text == "!powitanie":
        return "Po !powitanie ustaw treść powitania"

    async with sql_actions.InsertIntoDatabase() as db:
        await db.insert_welcome_messages(event.thread.id, event.message.text[10:])
    return "Powitanie zostało zmienione :)"


@group_actions
@send_text_message
async def set_new_group_regulations(event, group_info):
    async with sql_actions.InsertIntoDatabase() as db:
        await db.insert_group_regulations(event.thread.id, event.message.text[14:])
    return "Regulamin został zmieniony :) Użyj komendy !regulamin by go zobaczyć"


@group_actions
@send_text_message
async def get_group_regulations(event, group_info):
    try:
        async with sql_actions.GetInfoFromDatabase() as db:
            await db.fetch_group_regulations(event.thread.id)
            group_regulations = db.data[0]
    except IndexError:
        group_regulations = "Grupa nie ma regulaminu. Aby go ustawić użyj komendy\n!nowyregulamin 'treść'"
    return group_regulations


@group_actions
@send_text_message_with_mentions
async def mention_everyone(event, group_info):
    mentions = [fbchat.Mention(thread_id=participant.id, offset=0, length=9) for participant in group_info.participants]
    return "ELUWA ALL", mentions


async def make_disco(event, client):
    # todo zrób ograniczenie
    for i in range(5):
        color = rd.choice(SETABLE_COLORS)
        await event.thread.set_color(color)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Below are functions which don`t work because Facebook changed API
They should be available soon

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


@send_text_message
async def change_emoji(event):
    return """Fb czasowo usunął możliwość zmieniania emoji przez API. 
Opcja zostanie dodana wtedy kiedy fb znowu doda te funkcje"""

    # todo try to fix this function
    # try:
    #    await event.thread.set_emoji(emoji=event.message.text[8])
    # except:
    #    await event.thread.set_emoji(emoji=event.message.text[7])


@send_text_message
async def change_nick(event):
    return """Fb czasowo usunął nicki.
Opcja zostanie dodana wtedy kiedy fb znowu doda te funkcje"""

    # todo add commented part of code in this function when nicknames in messenger come back
    # try:
    #    await event.thread.set_nickname(user_id=event.author.id, nickname=event.message.text[5:])
    # except:
    #    await event.thread.send_text("Linux nie moze odczytać polskiej litery, albo wpisałes za długi nick")
