from io import BytesIO
import re
import requests
from random import choice
import os
import shutil
from requests.exceptions import MissingSchema
from typing import Tuple, Union

import feedparser
import aiohttp
from bs4 import BeautifulSoup
import pytube
import cloudscraper

from Bot.parse_config import weather_api_key


WEATHER_API_URL = f"http://api.openweathermap.org/data/2.5/weather?appid={weather_api_key}&lang=pl&units=metric&q="
WEATHER_API_URL_FORECAST = f"http://api.openweathermap.org/data/2.5/forecast?appid={weather_api_key}&lang=pl&units=metric&q="
DIFFICULTIES_IN_WARSAW_URL = "https://www.wtp.waw.pl/feed/?post_type=impediment"
DIFFICULTIES_IN_LODZ_URL = "http://www.mpk.lodz.pl/rozklady/utrudnienia.jsp"
DIFFICULTIES_IN_WROCLAW_URL = "https://www.facebook.com/mpkwroc/"


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

    async def get_forecast(self, city: str) -> str:
        async with aiohttp.ClientSession() as session:
            html = await session.get(WEATHER_API_URL_FORECAST + city)
            json_data = await html.json()
        try:
            city_name = json_data["city"]["name"]
            message = f"🌐 Prognoza pogody w {city_name} 🌐\n"
            for i in json_data["list"][0:12]:
                temp_min_emoji = await self.check_temperature_emoji(i["main"]["temp_min"])
                temp_max_emoji = await self.check_temperature_emoji(i["main"]["temp_max"])
                wind_speed = i["wind"]["speed"] * 3.6 # *3.6 converts ms/s to km/h
                message += f"""
{i["dt_txt"].replace("0", "𝟬").replace("1", "𝟭").replace("2", "𝟮").replace("3", "𝟯").replace("4", "𝟰").replace("5", "𝟱").replace("6", "𝟲").replace("7", "𝟳").replace("8", "𝟴").replace("9", "𝟵").replace("-", "-").replace(":", ":")}
🔰 Najniższa temperatura: {temp_min_emoji} {int(i["main"]["temp_min"])}
🔰 Najwyższa temperatura: {temp_max_emoji} {int(i["main"]["temp_max"])}
🔰 Atmosfera: {self.icons[i["weather"][0]["icon"]]} {i["weather"][0]["description"].capitalize()}
🔰 Prędkość wiatru: {'%.2f' % wind_speed } km/h
"""
            return message
        except KeyError:
            return "🚫 Nie znaleziono takiej miejscowości"

    async def get_weather(self, city: str) -> str:
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
🔰 Prędkość wiatru: {'%.2f' % wind_speed} km/h

Jeśli chcesz pogodę na kilka dni, napisz !pogoda -f {city_name}\n"""
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


async def get_public_transport_difficulties_in_warsaw() -> str:
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


async def get_public_transport_difficulties_in_lodz() -> str:
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


def download_yt_video(link: str) -> Tuple[Union[BytesIO, str], Union[str, None]]:
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


async def get_info_from_wikipedia(thing_to_search: str, restart: bool = True, polish: bool = True) -> str:
    link = f"https://pl.wikipedia.org/wiki/{thing_to_search}" if polish else f"https://wikipedia.org/wiki/{thing_to_search}"
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
                if not polish:
                    info = f"🚫 Nie można odnaleźć: {thing_to_search}"
                    info += f"\n Więcej informacji: {link}"
                else:
                    info = await get_info_from_wikipedia(thing_to_search, False, False)
    info = re.sub(r"\[[0-9]*\]", "", info)
    return info


async def get_info_from_miejski(thing_to_search: str) -> str:
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
    async def download_tiktok(self, tiktok_link: str) -> Tuple[Union[BytesIO, list], str]:
        scraper = cloudscraper.create_scraper()
        download_url = await self.get_tiktok_download_url(tiktok_link, scraper)
        if download_url and download_url != "https://musicallydown.page.link/app":
            try:
                if type(download_url) == str:
                    response = scraper.get(download_url)
                    bytes_object = BytesIO()
                    bytes_object.write(response.content)
                    return bytes_object, "video/mp4"
                else:
                    photos = []
                    for i in download_url:
                        response = scraper.get(i)
                        bytes_object = BytesIO()
                        bytes_object.write(response.content)
                        photos.append(bytes_object)
                    return photos, "image/png"
            except MissingSchema:
                return "🚫 Znaleziono tiktoka, ale najprawdopodobniej jest to prywatny film i nie można go pobrać"
        return "🚫 Najprawdopodobniej podano niepoprawny link"

    async def get_tiktok_download_url(self, tiktok_link: str, scraper: cloudscraper.CloudScraper) -> Union[str, list]:
        links = []
        post_data, cookies = await self.get_required_post_data(tiktok_link, scraper)
        response = scraper.post("https://musicaldown.com/download", data=post_data, cookies=cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        for i in soup.find_all("a"):
            try:
                link = i["href"]
            except KeyError:
                continue
            if link.startswith("https://") and "type=mp3" not in link:
                if link.startswith("https://") and "type=mp3" not in link:
                    return link
                elif "type=photo" in link:
                    links.append(link)
        return links

    @staticmethod
    async def get_required_post_data(tiktok_link: str, scraper: cloudscraper.CloudScraper) -> Tuple[dict, dict]:
        url_name = ""
        key_name = ""
        key = ""
        response = scraper.get("https://musicaldown.com/")
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


async def get_google_image(search_query: str) -> Union[BytesIO, str]:
    link = f"https://images.search.yahoo.com/search/images;?p={search_query}"
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    images = soup.find_all("img")
    for i in images:
        if i.get("src"):
            temp = i["src"]
            if "&w=" in temp and "&h=" in temp:
                links.append(temp)
    try:
        download_link = choice(links)
        response = requests.get(download_link)
        bytes_object = BytesIO()
        bytes_object.write(response.content)
        return bytes_object
    except IndexError:
        return f"Nie odnaleziono {search_query.replace('%20', ' ')} 😔"


def download_spotify_song(song_name: str) -> Union[BytesIO, str]:
    song_name = song_name.replace('&utm_source=copy-link', '')
    output_dir = os.path.join("Bot/media/music/", song_name.replace('/', ''))
    if not os.path.exists(output_dir):
        try:
            os.mkdir(output_dir)
            os.system(f"spotdl {song_name} -o ./{output_dir}")
            os.remove(os.path.join(output_dir, ".spotdl-cache"))
            os.listdir(output_dir)[0]  # checks if the song has been downloaded, if not this line will raise a IndexError
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


async def check_item_price(item: str) -> str:
    link = f"https://www.skapiec.pl/szukaj?query={item}"
    async with aiohttp.ClientSession() as session:
        html = await session.get(link)
        soup = BeautifulSoup(await html.text(), "html.parser")

    message = ""
    i = 0
    for item in soup.find_all("div", class_="product-item"):
        product_name = item.find("a", class_="product-box-narrow__title")
        price = item.find("span", class_="price")
        message += product_name.text.strip() + "\n" + price.text.strip() + "\n\n"
        if i == 4:  # show only first five items
            break
        i += 1
    return message


async def get_lyrics(creator: str, song_name: str) -> str:
    lyrics = ""
    async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}) as session:
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
            response = await session.get(f"https://tekstowo.pl{song_link}")
            soup = BeautifulSoup(await response.text(), "html.parser")
            try:
                lyrics = soup.find("div", class_="inner-text").text
            except AttributeError:
                # song was not found
                pass
    return lyrics


async def get_vehicle_registration_number_info(registration_num: str) -> str:
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
