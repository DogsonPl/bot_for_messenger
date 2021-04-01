import feedparser
import aiohttp
from bs4 import BeautifulSoup
from io import BytesIO
import pytube


WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather?appid=48cf48dbb3891862735dd16b01a3a62f&q="
COVID_IN_WORLD_URL = "https://coronavirus-19-api.herokuapp.com/all"
COVID_IN_POLAND_URL = "https://coronavirus-19-api.herokuapp.com/countries/poland"
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

    async def get_weather(self, city):
        async with aiohttp.ClientSession() as session:
            html = await session.get(WEATHER_API_URL + city)
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
            icon = json_data["weather"][0]["icon"]

            weather_emoji = self.icons[icon]
            temperature_emoji = await self.check_temperature_emoji(temperature)
            perceptible_temperature_emoji = await self.check_temperature_emoji(perceptible_temperature)
            return f"""🌐 Pogoda w {city.title()} 🌐

🔰 Temperatura: {temperature_emoji} {int(temperature)}C 
🔰 Odczuwalna: {perceptible_temperature_emoji} {int(perceptible_temperature)}C
🔰 Atmosfera: {weather_emoji} {weather_description} 
🔰 Ciśnienie: {pressure} hPa
🔰 Wilgotność: {humidity} %
🔰 Prędkość wiatru: {wind_speed} m/s"""
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
🩺 Uleczonych: {data['recovered']}
😷 Chore osoby w tej chwili: {format(data['cases'] - data['deaths'] - data['recovered'], ',d')}"""
    except KeyError:
        return "Błąd API. Spróbuj ponownie za kilka minut"


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
        return "Błąd API. Spróbuj ponownie za kilka minut"


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
    return message


async def get_public_transport_difficulties_in_wroclaw():
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
        video = video.streams.first()
    except pytube.exceptions.VideoUnavailable:
        return "Bot nie może pobrać video, ponieważ jest nieobecne w danym ragionie", None
    try:
        video.stream_to_buffer(bytes_object)
    except KeyError:
        return "Nie można pobrać streamu na żywo", None
    return bytes_object, "video/mp4"
