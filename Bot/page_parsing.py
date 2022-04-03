from io import BytesIO
import re
import requests
from random import choice
import os
import shutil
from requests.exceptions import MissingSchema

import feedparser
import aiohttp
from bs4 import BeautifulSoup
import pytube

from Bot.parse_config import weather_api_key


WEATHER_API_URL = f"http://api.openweathermap.org/data/2.5/weather?appid={weather_api_key}&lang=pl&units=metric&q="
COVID_IN_WORLD_URL = "https://coronavirus-19-api.herokuapp.com/all"
COVID_IN_POLAND_URL = "https://coronavirus-19-api.herokuapp.com/countries/poland"
DIFFICULTIES_IN_WARSAW_URL = "https://www.wtp.waw.pl/feed/?post_type=impediment"
DIFFICULTIES_IN_LODZ_URL = "http://www.mpk.lodz.pl/rozklady/utrudnienia.jsp"
DIFFICULTIES_IN_WROCLAW_URL = "https://www.facebook.com/mpkwroc/"

API_ERROR_MESSAGE = "😭 Błąd API. Spróbuj ponownie za kilka minut"


class GetWeather:
    def __init__(self):
        self.icons = {"01d": "☀", "01n": "🌙",
                      "02d": "🌤", "02n": "☁",
                      "03d": "🌥", "03n": "☁",
                      "04d": "☁", "04n": "☁",
                      "09d": "🌦", "09n": "🌧",
                      "10d": "🌧", "10n": "🌧",
                      "11d": "⛈", "11n": "⛈",
                      "13d": "🌨", "13n": "🌨",
                      "50d": "🌫", "50n": "🌫"}

    async def get_weather(self, city):
        async with aiohttp.ClientSession() as session:
            html = await session.get(WEATHER_API_URL + city)
        json_data = await html.json()
        try:
            city_name = json_data["name"]
            temperature = json_data["main"]["temp"]
            perceptible_temperature = json_data["main"]["feels_like"]
            weather_description = json_data["weather"][0]["description"]
            pressure = json_data["main"]["pressure"]
            humidity = json_data["main"]["humidity"]
            wind_speed = json_data["wind"]["speed"]
            wind_speed *= 3.6  # *3.6 converts ms/s to km/h
            icon = json_data["weather"][0]["icon"]

            weather_emoji = self.icons[icon]
            temperature_emoji = await self.check_temperature_emoji(temperature)
            perceptible_temperature_emoji = await self.check_temperature_emoji(perceptible_temperature)

            return f"""🌐 Pogoda w {city_name} 🌐

🔰 Temperatura: {temperature_emoji} {int(temperature)}C 
🔰 Odczuwalna: {perceptible_temperature_emoji} {int(perceptible_temperature)}C
🔰 Atmosfera: {weather_emoji} {weather_description.capitalize()} 
🔰 Ciśnienie: {pressure} hPa
🔰 Wilgotność: {humidity} %
🔰 Prędkość wiatru: {'%.2f' % wind_speed} km/h"""
        except KeyError:
            return "🚫 Nie znaleziono takiej miejscowości"

    @staticmethod
    async def check_temperature_emoji(temperature):
        if temperature < 0:
            return "🥶"
        elif temperature > 25:
            return "🥵"
        else:
            return "🌡"


async def get_coronavirus_info():
    async with aiohttp.ClientSession() as session:
        html = await session.get(COVID_IN_WORLD_URL)
    data = await html.json()

    try:
        return f"""🦠 Koronawirus na świecie 🦠

🤒 Potwierdzonych: {format(data['cases'], ',d')}
☠ Śmierci: {format(data['deaths'], ',d')}
🩺 Uleczonych: {format(data['recovered'], ',d')}
😷 Chore osoby w tej chwili: {format(data['cases'] - data['deaths'] - data['recovered'], ',d')}"""
    except KeyError:
        return API_ERROR_MESSAGE


async def get_coronavirus_pl_info():
    async with aiohttp.ClientSession() as session:
        html = await session.get(COVID_IN_POLAND_URL)
    data = await html.json()

    try:
        return f"""🦠 Koronawirus w Polsce 🦠

🤒 Potwierdzonych: {format(data['cases'], ',d')}
🤒 Dzisiaj potwierdzono: {format(data['todayCases'], ',d')}
☠ Śmierci: {format(data['deaths'], ',d')}
🩺 Uleczonych: {format(data['recovered'], ',d')}
😷 Chore osoby w tej chwili: {format(data['active'], ',d')}
😷 Liczba chorych na milion osób: {format(data['casesPerOneMillion'], ',d')}
☠ Śmiertelne przypadki na milion osób: {format(data['deathsPerOneMillion'], ',d')}
🧬 Liczba zrobionych testów: {format(data['totalTests'], ',d')}
🧬 Liczba testów na milion osób: {format(data['testsPerOneMillion'], ',d')}"""
    except KeyError:
        return API_ERROR_MESSAGE


async def get_public_transport_difficulties_in_warsaw():
    feed = feedparser.parse(DIFFICULTIES_IN_WARSAW_URL)
    message = ""
    for entry in feed['entries']:
        message += "🚇 " + entry.title
        async with aiohttp.ClientSession() as session:
            html = await session.get(entry.link)
            soup = BeautifulSoup(await html.text(), "html.parser")
        for i in soup.find_all("div", class_="impediment-content"):
            message += i.text + "\n"
    if message == "":
        return "🎉🎉 Brak utrudnień w Warszawie :) Więcej informacji na https://www.wtp.waw.pl"
    if len(message) > 4000:
        message = "Utrudnień jest tak dużo, że nie można w wiadomości zmieścić ich szczegółów. Szczegółowe informacje: https://www.wtp.waw.pl/utrudnienia/\n\n"
        for entry in feed["entries"]:
            message += "🚇 " + entry.title + "\n"
    return message


async def get_public_transport_difficulties_in_wroclaw():
    # todo make parsing compatible with newer version of facebook
    async with aiohttp.ClientSession() as session:
        html = await session.get(DIFFICULTIES_IN_WROCLAW_URL)
        soup = BeautifulSoup(await html.text(), "html.parser")

    message = "🚋 Dane z fb MPK Wrocław\n"
    for i in soup.find_all("p"):
        message += i.text + "\n"
    return message


async def get_public_transport_difficulties_in_lodz():
    async with aiohttp.ClientSession() as session:
        html = await session.get(DIFFICULTIES_IN_LODZ_URL)
        soup = BeautifulSoup(await html.text(), "html.parser")

    message = "🚌 Właścicielami danych jest http://www.mpk.lodz.pl/rozklady/utrudnienia.jsp\n"
    for i in soup.find_all("p"):
        if "mpk na facebook" in i.text.lower():
            message += "\n"
        elif "Zamknij" in i.text:
            break
        else:
            message += i.text + "\n"
    return message


def download_yt_video(link):
    video = pytube.YouTube(link)
    try:
        if video.length > 260:
            return "🚫 Wideo jest za długie i nie mogę go pobrać, ponieważ by to zbyt obciążyło serwery", None
    except TypeError:
        return "🚫 Nie mogę znaleźć video", None
    bytes_object = BytesIO()
    try:
        video = video.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
    except pytube.exceptions.VideoUnavailable:
        return "Bot nie może pobrać video, ponieważ jest niedostępne w danym ragionie", None
    try:
        video.stream_to_buffer(bytes_object)
    except KeyError:
        return "Nie można pobrać streamu na żywo", None
    return bytes_object, "video/mp4"


async def get_info_from_wikipedia(thing_to_search, restart=True):
    link = f"https://pl.wikipedia.org/wiki/{thing_to_search}"
    async with aiohttp.ClientSession() as session:
        html = await session.get(link)
        soup = BeautifulSoup(await html.text(), "html.parser")
    info = soup.select_one("p")
    try:
        info = info.text + f"\n Więcej informacji: {link}"
    except AttributeError:
        info = ""
        for i in soup.find_all("div", class_="mw-parser-output"):
            info += i.text.strip()
        if info == "":
            if restart:
                thing_to_search = thing_to_search.split("_")
                for index, item in enumerate(thing_to_search[1:]):
                    thing_to_search[index+1] = thing_to_search[index+1].lower()
                thing_to_search = "_".join(thing_to_search)
                info = await get_info_from_wikipedia(thing_to_search, False)
            else:
                info = f"🚫 Nie można odnaleźć: {thing_to_search}"
                info += f"\n Więcej informacji: {link}"
    info = re.sub(r"\[[0-9]*\]", "", info)
    return info


async def get_info_from_miejski(thing_to_search):
    link = f"https://miejski.pl/slowo-{thing_to_search}"
    info = ""
    async with aiohttp.ClientSession() as session:
        html = await session.get(link)
        soup = BeautifulSoup(await html.text(), "html.parser")
    for i in soup.find_all("article"):
        for j in i.find_all("p"):
            info += j.text.strip()
        info += "\n"
        for j in i.find_all("blockquote"):
            info += j.text.strip()
        info += "\n\n"
    return info


class DownloadTiktok:
    async def download_tiktok(self, tiktok_link):
        download_url = await self.get_tiktok_download_url(tiktok_link)
        if download_url and download_url != "https://musicallydown.page.link/app":
            try:
                response = requests.get(download_url)
                bytes_object = BytesIO()
                bytes_object.write(response.content)
                return bytes_object
            except MissingSchema:
                return "🚫 Znaleziono tiktoka, ale najprawdopodobniej jest to prywatny film i nie można go pobrać"
        return "🚫 Najprawdopodobniej podano niepoprawny link"

    async def get_tiktok_download_url(self, tiktok_link):
        link = ""
        post_data, cookies = await self.get_required_post_data(tiktok_link)
        response = requests.post("https://musicaldown.com/download", data=post_data, cookies=cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        for i in soup.find_all("a"):
            try:
                link = i["href"]
            except KeyError:
                continue
            if link.startswith("https://"):
                break
        return link

    @staticmethod
    async def get_required_post_data(tiktok_link):
        url_name = ""
        key_name = ""
        key = ""
        response = requests.get("https://musicaldown.com/")
        soup = BeautifulSoup(response.text, "html.parser")
        for i in soup.find_all("form"):
            for j in i.find_all('input'):
                if not url_name:
                    url_name = j["name"]
                else:
                    key_name = j["name"]
                    key = j["value"]
                    break

        post_data = {url_name: tiktok_link, key_name: key, "verify": "1"}
        cookies = {"session_data": response.cookies["session_data"]}
        return post_data, cookies

    @staticmethod
    async def _get_tiktok_download_url_deprecated(url):
        """
        depercated function, page has been banned
        """
        link = False
        async with aiohttp.ClientSession() as session:
            response = await session.get(f"https://hamod.ga/api/tiktokWithoutWaterMark.php?u={url}")
            if 'link' in await response.text():
                link = await response.json(content_type=None)
                link = link["link"]
        return link


async def get_google_image(search_query):
    link = f"https://google.com/search?q={search_query}&tbm=isch"
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    images = soup.find_all("img")
    for i in images[1:]:  # ignore first google image
        links.append(i["src"])
    try:
        download_link = choice(links)
        response = requests.get(download_link)
        bytes_object = BytesIO()
        bytes_object.write(response.content)
        return bytes_object
    except IndexError:
        return f"Nie odnaleziono {search_query.replace('%20', ' ')} 😔"


def download_spotify_song(song_name):
    output_dir = os.path.join("Bot/media/music/", song_name.replace('/', ''))
    if not os.path.exists(output_dir):
        try:
            os.mkdir(output_dir)
            os.system(f"spotdl {song_name} -o ./{output_dir}")
            os.remove(os.path.join(output_dir, ".spotdl-cache"))
            os.listdir(output_dir)[0]  # check if song has been downloaded, if not this line raise IndexError
        except (FileNotFoundError, IndexError):
            shutil.rmtree(output_dir)
            message = "🚫 Nie odnaleziono piosenki, pamiętaj że wielkość liter ma znaczenie (powinna być taka sama jak się wyświetla w spotify). Możliwe jest też to że pobieranie piosenki jest zablokowane"
            if "spotify" not in song_name:
                message += "\n\nSpróbuj wysłać link do piosenki na spotify"
            return message

    try:
        filename = os.listdir(output_dir)[0]
    except IndexError:
        return "🚫 Piosenka najprawdopoodbniej była przed chwilą pobierana i nie została znaleziona"
    with open(os.path.join(output_dir, filename), "rb") as song:
        bytes_object = BytesIO(song.read())
    return bytes_object


async def check_item_price(item):
    link = f"https://www.skapiec.pl/szukaj/w_calym_serwisie/{item}"
    async with aiohttp.ClientSession() as session:
        html = await session.get(link)
        soup = BeautifulSoup(await html.text(), "html.parser")

    message = ""
    for i, tag in enumerate(soup.find_all("a", class_="box")):
        product_name = tag.find("h2", class_="title")
        price = tag.find("strong", class_="price")
        message += product_name.text.strip() + "\n" + price.text.strip() + "\n\n"
        if i == 4:  # show only first five items
            break

    return message


async def get_lyrics(creator, song_name):
    lyrics = ""
    async with aiohttp.ClientSession() as session:
        link = f"https://tekstowo.pl/szukaj,wykonawca,{creator},tytul,{song_name}"
        response = await session.get(link)
        soup = BeautifulSoup(await response.text(), "html.parser")
    try:
        songs_links = soup.find("div", "card mb-4")
    except AttributeError:
        return lyrics

    try:
        song_link = songs_links.find("a", class_="title")["href"]
    except (KeyError, AttributeError):
        pass
    else:
        async with aiohttp.ClientSession() as session:
            response = await session.get(f"https://tekstowo.pl{song_link}")
            soup = BeautifulSoup(await response.text(), "html.parser")
        try:
            lyrics = soup.find("div", class_="inner-text").text
        except AttributeError:
            # song was not found
            pass
    return lyrics


async def get_vehicle_registration_number_info(registration_num):
    async with aiohttp.ClientSession() as session:
        link = f"https://tablica-rejestracyjna.pl/{registration_num}"
        response = await session.get(link)
        if response.status != 200:
            return "🚫 Nie odnaleziono podanej tablicy rejestracyjnej, przykładowa tablica to k1dis (!tablica k1dis)"
        soup = BeautifulSoup(await response.text(), "html.parser")

    if soup.find("h3").text == "Wybrane komentarze":
        return "🚫 Nie odnaleziono podanej tablicy rejestracyjnej, przykładowa tablica to k1dis (!tablica k1dis)"

    vehicle_registration_number_info = "𝗜𝗻𝗳𝗼𝗿𝗺𝗮𝗰𝗷𝗲 𝗼 𝘁𝗮𝗯𝗹𝗶𝗰𝘆:\n"
    for i in soup.find_all(itemprop="contentLocation"):
        vehicle_registration_number_info += i.text + "\n"
    vehicle = soup.find(itemprop="description")
    if vehicle:
        vehicle = vehicle.text
    else:
        vehicle = "Nieznany pojazd"
    vehicle_registration_number_info += f"Pojazd: {vehicle}\n"

    vehicle_registration_number_info += "\n𝗞𝗼𝗺𝗲𝗻𝘁𝗮𝗿𝘇𝗲:\n"
    for i in soup.find_all(class_="comment"):
        vehicle_registration_number_info += i.find(class_="text").text.strip() + "\n********\n"
        if len(vehicle_registration_number_info) > 1000:
            break
    return vehicle_registration_number_info




ukraine_link = "https://wiadomosci.onet.pl/swiat/wojna-rosja-ukraina-wybuchy-w-oddalonym-od-polski-o-100-km-lucku-relacja/hqwy3ws"

async def ukraine():
    response = requests.get(ukraine_link)
    soup = BeautifulSoup(response.text, "html.parser")
    message = ""
    for i in soup.find_all("ul", class_="firstList"):
        for j in i.find_all("li"):
            message += f"❗ {j.text}\n"

    message += "\n\n"
    for i in soup.find_all("div", class_="messageItem textItem"):
        if i.text.strip().startswith("{{"):
            continue
        message += i.text.strip() + "\n"
        if len(message) > 3500:
            break
    return message
