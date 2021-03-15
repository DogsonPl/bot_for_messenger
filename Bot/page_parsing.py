import feedparser
import aiohttp
from bs4 import BeautifulSoup

WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather?appid=48cf48dbb3891862735dd16b01a3a62f&q="
COVID_IN_WORLD_URL = "https://coronavirus-19-api.herokuapp.com/all"
COVID_IN_POLAND_URL = "https://coronavirus-19-api.herokuapp.com/countries/poland"
DIFFICULTIES_IN_WARSAW_URL = "https://www.wtp.waw.pl/feed/?post_type=impediment"
DIFFICULTIES_IN_LODZ_URL = "http://www.mpk.lodz.pl/rozklady/utrudnienia.jsp"
DIFFICULTIES_IN_WROCLAW_URL = "https://www.facebook.com/mpkwroc/"


async def get_weather(city):
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
        return f"""Pogoda w {city.title()}
Temperatura: {int(temperature)}C 
Odczuwalna: {int(perceptible_temperature)}C
Atmosfera: {weather_description} 
Ciśnienie: {pressure} hPa
Wilgotność: {humidity} %
Prędkość wiatru: {wind_speed} m/s"""
    except KeyError:
        return "Nie znaleziono takiej miejscowości"


async def get_coronavirus_info():
    async with aiohttp.ClientSession() as session:
        html = await session.get(COVID_IN_WORLD_URL)
    data = await html.json()

    try:
        return f"""Koronawirus na świecie
Potwierdzonych: {data['cases']}
Śmierci: {data['deaths']}
Uleczonych: {data['recovered']}
Chore osoby w tej chwili: {data['cases'] - data['deaths'] - data['recovered']}"""
    except KeyError:
        return "Błąd API. Spróbuj ponownie za kilka minut"


async def get_coronavirus_pl_info():
    async with aiohttp.ClientSession() as session:
        html = await session.get(COVID_IN_POLAND_URL)
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


async def get_public_transport_difficulties_in_warsaw():
    feed = feedparser.parse(DIFFICULTIES_IN_WARSAW_URL)
    message = ""
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


async def get_public_transport_difficulties_in_wroclaw():
    async with aiohttp.ClientSession() as session:
        html = await session.get(DIFFICULTIES_IN_WROCLAW_URL)
        soup = BeautifulSoup(await html.text(), "html.parser")

    message = "Dane z fb MPK Wrocław\n"
    for i in soup.find_all("p"):
        message += i.text + "\n"
    return message


async def get_public_transport_difficulties_in_lodz():
    async with aiohttp.ClientSession() as session:
        html = await session.get(DIFFICULTIES_IN_LODZ_URL)
        soup = BeautifulSoup(await html.text(), "html.parser")

    message = "Właścicielami danych jest http://www.mpk.lodz.pl/rozklady/utrudnienia.jsp\n"
    for i in soup.find_all("p"):
        if "mpk na facebook" in i.text.lower():
            message += "\n"
        elif "Zamknij" in i.text:
            break
        else:
            message += i.text + "\n"
    return message
