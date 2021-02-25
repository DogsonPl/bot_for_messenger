import fbchat
import feedparser
import aiohttp
from bs4 import BeautifulSoup
import json
from gtts import gTTS
import random as rd
import os
from PIL import Image, ImageDraw, ImageFont

help_commends = """Komendy:\n
!help - wysyła komendy\n
!wersja - wysyła wersje bota + to co ostatnio dodano do bota\n
!wsparcie - jeśli chcesz wesprzeć powstawanie bota, wyślij pieniądze na ten adres. Bot jest darmowy, ale za vps itp ja muszę płacić :/ Wielkie dzięki za każdą wpłatę i pomoc!\n
!tworca - wysyła link do mnie (twórcy bota) Możesz tam pisać opinie, propozycje na dodanie czegoś do bota itp\n
!koronawirus - wysyła informacje o koroawirusie na świecie\n
!koronawiruspl - wysyła informacje o koronawirusie w polsce\n
!mem - wysyła losowego mema\n
!mem2 - wysyła nowsze memy\n
!luckymember - losuje losowego członka grupy\n
!para - losuje dwie osoby które sie kochaja!\n
!ruletka - usuwa losowego członka grupy (bot musi mieć admina)\n
!pogoda x - wysyła pogode w danym miejscu (wpisz np: !pogoda warszawa)\n
!nick x - zmienia twój nick na x (np '!nick coś' usatwi twoj nick na 'coś')\n  
!everyone - oznacza wszystkich ludzi na grupie (jest napisane że oznacza jedną osobe ale tak naprawde oznaczony jest każdy)\n
!utrudnieniawroclaw - pisze utrudnienia w komunikacji miejskiej we Wrocławiu (ostatnie dwa posty MPK Wrocław)\n
!utrudnieniawawa - pisze utrudnienia w komunikacji miejsiej w Warszawie\n
!utrudnienialodz - pisze utrudnienia w komunikacji miejskiej w Łodzi\n
!losuj x y= losuje losowa liczbe (od x do y, np !losuj 10 20)\n
!moneta - bot rzuca monete (orzeł lub reszka)\n
!mute - wycisza głupie odzywki bota na np 'co' + wyłącza komendę !everyone\n
!unmute - odcisza bota\n
DODATKOWE KOMENDY ZA ZAKUP WERSJI PRO:
!film - wysyła losowy śmieszny film\n
!tvpis x- tworzy pasek z tvpis z napisem który zostanie podany po komendzie (np !tvpis jebać pis")
!disco - robi dyskoteke (czasami występują błędy)\n
!emotka x - zmienia emotke na x (np emotka 😎)\n
!powitanie 'treść' - ustawia powitanie na grupie nowego członka\n
!nowyregulamin 'treść' - ustawia regulamin grupy\n
!regulamin - wysyła regulamin grupy\n
!say 'wiadomosc'- ivona mówi to co się napisze po !say\n """


async def help_(event):
    await event.thread.send_text(help_commends)


async def mem(event, client):
    drawing_mem = str(rd.randint(1, 199))
    mem_name = f"data//memes//mem{drawing_mem}.png"
    with open(mem_name, "rb") as f:
        files = await client.upload([(mem_name, f, "image/png")])
    await event.thread.send_files(files)


async def mem2(event, client):
    drawing_mem = str(rd.randint(200, 356))
    mem_name = f"data//memes//mem{drawing_mem}.png"
    with open(mem_name, "rb") as f:
        files = await client.upload([(mem_name, f, "image/png")])
    await event.thread.send_files(files)


async def film(event, client):
    drawing_film = str(rd.randint(1, 63))
    film_name = f"data//films//film{drawing_film}.mp4"
    with open(film_name, "rb") as f:
        files = await client.upload([(film_name, f, "video/mp4")])
    await event.thread.send_files(files)


async def moneta(event, client):
    choosen = rd.choice(["data//orzel_reszka//orzel", "data//orzel_reszka//reszka"])
    with open(f"{choosen}.png", "rb") as file:
        files = await client.upload([(f"{choosen}.png", file, "image/png")])
    await event.thread.send_files(files)


async def say(event, client):
    if len(event.message.text) > 1000:
        await event.thread.send_text("Wiadomość może mieć maksymalnie 1000 znaków (musiałem zrobić te ograniczenie bo bot się za bardzo lagował)")
    elif event.message.text == "!say":
        await event.thread.send_text("Po !say napisz coś co ma powiedzieć bot, np !say elo")
    else:
        tts = gTTS(event.message.text[4:], lang="pl")
        save_path = f"data//voice_messages{event.message.id}.mp3"
        tts.save(save_path)
        with open(save_path, "rb") as f:
            files = await client.upload([(save_path, f, "audio/mp3")], voice_clip=True)
        await event.thread.send_files(files)
        os.remove(save_path)


async def weather_function(event):
    try:
        api_address = 'http://api.openweathermap.org/data/2.5/weather?appid=48cf48dbb3891862735dd16b01a3a62f&q='
        city = event.message.text[8:]
        url = api_address + city
        async with aiohttp.ClientSession() as session:
            html = await session.get(url)
            json_data = await html.json()
        temperature = json_data["main"]["temp"]
        temperature -= 273
        feel_temperature = json_data["main"]["feels_like"]
        feel_temperature -= 273
        weather = json_data["weather"][0]["description"]
        preassure = json_data["main"]["pressure"]
        humidity = json_data["main"]["humidity"]
        wind_speed = json_data["wind"]["speed"]
        full_weather = f"""Pogoda w {str(city).title()}
Temperatura: {int(temperature)} C 
Odczuwalna: {int(feel_temperature)} C
Atmosfera: {weather} 
Ciśnienie: {preassure} hPa
Wilgotność: {humidity} %
Prędkość wiatru: {wind_speed} m/s"""
        await event.thread.send_text(full_weather)
    except:
        await event.thread.send_text("Nie znalezione takiej miejscowości, lub linux nie umie odczytać polskiego znaku. Spróbuj wpisać nazwe miejscowości bez polskich znakow")


async def coronavirus(event):
    async with aiohttp.ClientSession() as session:
        html = await session.get("https://coronavirus-19-api.herokuapp.com/all")
        data = await html.json()
        message = f"Koronawirus na świecie\nPotwierdzonych: {data['cases']}\nŚmierci: {data['deaths']}\nUleczonych: {data['recovered']}\nChore osoby w tej chwili: {data['cases'] - data['deaths'] - data['recovered']}"
    if message != "":
        await event.thread.send_text(message)
    else:
        await event.thread.send_text("Błąd api. Spróbuj ponownie za kilka minut")


async def coronavirus_pl(event):
    async with aiohttp.ClientSession() as session:
        html = await session.get("https://coronavirus-19-api.herokuapp.com/countries/poland")
        data = await html.json()
        message = f"Koronawirus w Polsce\nPotwierdzonych: {data['cases']}\nDzisiaj potwierdzono: {data['todayCases']}\nŚmierci: {data['deaths']}\nUleczonych: {data['recovered']}\nChore osoby w tej chwili: {data['active']}\nLiczba chorych na milion osób: {data['casesPerOneMillion']}\nŚmiertelne przypadki na milion osób: {data['deathsPerOneMillion']}\nLiczba zrobionych testów: {data['totalTests']}\nLiczba testów na milion osób: {data['testsPerOneMillion']}"
    if message != "":
        await event.thread.send_text(message)
    else:
        await event.thread.send_text("Błąd api. Spróbuj ponownie za kilka minut")


async def utrudnienia_wawa(event):
    feed = feedparser.parse('https://www.wtp.waw.pl/feed/?post_type=impediment')
    message = ""
    for entry in feed['entries']:
        message += entry.title
        async with aiohttp.ClientSession() as session:
            async with session.get(entry.link) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                for i in soup.find_all("div", class_="impediment-content"):
                    message += i.text
            message += "\n"

    if len(message) == 0:
        await event.thread.send_text("Brak utrudnień w Warszawie :) Więcej informacji na https://www.wtp.waw.pl")
    else:
        await event.thread.send_text(f"{message}Więcej informacji na https://www.wtp.waw.pl")


async def utrudnienia_wroclaw(event):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.facebook.com/mpkwroc/") as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
    sformatowane_dane = ""
    for i in soup.find_all("p"):
        sformatowane_dane += str(i.text) + "\n"
    await event.thread.send_text(sformatowane_dane)


async def utrudnienia_lodz(event):
    async with aiohttp.ClientSession() as session:
        async with session.get("http://www.mpk.lodz.pl/rozklady/utrudnienia.jsp") as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
    sformatowane_dane = ""
    for i in soup.find_all("p"):
        if "MPK na facebook".lower() in str(i.text).lower():
            sformatowane_dane += "\n"
        elif "Zamknij" in str(i.text):
            break
        else:
            sformatowane_dane += str(i.text) + "\n"
    await event.thread.send_text(f"Właścicielami danych jest http://www.mpk.lodz.pl/rozklady/utrudnienia.jsp\n{sformatowane_dane}")


async def mute(event, client, mutelist):
    if not isinstance(event.thread, fbchat.Group):
        await event.thread.send_text("To komenda tylko dla grup")
    else:
        participants = await client.fetch_thread_info([event.thread.id]).__anext__()
        if event.author.id not in participants.admins:
            await event.thread.send_text("Tylko administartor grupy może używać tej funkcji")
        else:
            if event.thread.id in mutelist:
                await event.thread.send_text("Jestem zmutowany. Aby mnie odmutować napisz !unmute")
            else:
                await event.thread.send_text("Zostalem zmutowany. Aby mnie odmutowac napisz !unmute")
                mutelist.append(event.thread.id)
                with open("data//mutelist.json", "w") as write_file:
                    json.dump(mutelist, write_file)


async def unmute(event, client, mutelist):
    if not isinstance(event.thread, fbchat.Group):
        await event.thread.send_text("To komenda tylko dla grup")
    else:
        participants = await client.fetch_thread_info([event.thread.id]).__anext__()
        if event.author.id not in participants.admins:
            await event.thread.send_text("Tylko administartor grupy może używać tej funkcji")
        else:
            if event.thread.id not in mutelist:
                await event.thread.send_text("Nie jestem zmutowany")
            else:
                await event.thread.send_text("Nie jestem już zmutowany :)")
                mutelist.remove(event.thread.id)
                with open("data//mutelist.json", "w") as write_file:
                    json.dump(mutelist, write_file)


async def luckymember(event, client):
    if not isinstance(event.thread, fbchat.Group):
        await event.thread.send_text("To komenda tylko dla grup")
    else:
        group_members = await client.fetch_thread_info([event.thread.id]).__anext__()
        group_members = group_members.participants
        lucky_member = rd.choice(group_members).id
        mention = [fbchat.Mention(thread_id=lucky_member, offset=0, length=9)]
        await event.thread.send_text(text="Zwycięzca", mentions=mention)


async def para(event, client):
    if not isinstance(event.thread, fbchat.Group):
        await event.thread.send_text("To komenda tylko dla grup")
    else:
        group_members = await client.fetch_thread_info([event.thread.id]).__anext__()
        group_members = group_members.participants
        first_person = rd.choice(group_members).id
        second_person = rd.choice(group_members).id
        mention1 = [fbchat.Mention(thread_id=first_person, offset=0, length=3)]
        mention2 = [fbchat.Mention(thread_id=second_person, offset=0, length=4)]
        await event.thread.send_text(text="Mąż", mentions=mention1)
        await event.thread.send_text(text="Żona", mentions=mention2)


async def everyone(event, client, mutelist):
    if not isinstance(event.thread, fbchat.Group):
        await event.thread.send_text("To komenda tylko dla grup")
    elif event.thread.id in mutelist:
        await event.thread.send_text("Zły admin wyłączył te funkcję mutująć mnie :(")
    else:
        group = await client.fetch_thread_info([event.thread.id]).__anext__()
        mentions = [fbchat.Mention(thread_id=participant.id, offset=0, length=9)
        for participant in group.participants]
        await event.thread.send_text(text="ELUWA ALL", mentions=mentions)


async def ruletka(event, client, user_id):
    if not isinstance(event.thread, fbchat.Group):
        await event.thread.send_text("To komenda tylko dla grup")
    else:
        group = await client.fetch_thread_info([event.thread.id]).__anext__()
        if event.author.id not in group.admins:
            await event.thread.send_text("Tylko administartor grupy może używać tej funkcji")
        elif user_id not in group.admins:
            await event.thread.send_text("Żeby działała ta funkcja na grupie, muszę mieć admina")
        else:
            member_to_kick = rd.choice(group.participants).id
            if member_to_kick in group.admins:
                await event.thread.send_text("Wylosowalo admina. Nie moge go usunąć")
            else:
                await event.thread.remove_participant(member_to_kick)


async def nowy_regulamin(event, client):
    group = await client.fetch_thread_info([event.thread.id]).__anext__()
    if event.author.id not in group.admins:
        await event.thread.send_text("To komenda tylko dla adminów")
    else:
        with open(f"data//group_regulations//regulamin{event.thread.id}.json", "w") as write_file:
            json.dump(event.message.text[14:], write_file)
        await event.thread.send_text("Regulamin został zmieniony :) Użyj komendy !regulamin by go zobaczyć")


async def wyslij_regulamin(event):
    try:
        with open(f"data//group_regulations//regulamin{event.thread.id}.json", "r") as read_file:
            regulamin = json.load(read_file)
        await event.thread.send_text(regulamin)
    except FileNotFoundError:
        await event.thread.send_text("Grupa nie ma regulaminu. Aby go ustawić użyj komendy\n!nowyregulamin 'treść'")


async def powitanie(event, client):
    group = await client.fetch_thread_info([event.thread.id]).__anext__()
    if event.author.id not in group.admins:
        await event.thread.send_text("To komenda tylko dla adminów")
    else:
        if event.message.text == "!powitanie":
            await event.thread.send_text("Po !powitanie ustaw treść powitania")
        else:
            with open(f"data//welcome_messages//welcome_message{event.thread.id}.json", "w") as write_file:
                json.dump(event.message.text[10:], write_file)
            await event.thread.send_text("Powitanie zostało zmienione :)")


async def zmiana_emoji(event):
    await event.thread.send_text("Fb czasowo usunął możliwość zmieniania emoji przez API. Opcja zostanie dodana wtedy kiedy fb znowu doda te funckcje")
    #try:
    #    await event.thread.set_emoji(emoji=event.message.text[8])
    #except:
    #    await event.thread.set_emoji(emoji=event.message.text[7])


async def disco(event):
    for i in range(0, 15):
        try:
            change_color = rd.choice(fbchat._threads.SETABLE_COLORS)
            await event.thread.set_color(change_color)
        except:
            pass


async def change_nick(event):
    await event.thread.send_text("Fb czasowo usunął nicki. Opcja zostanie dodana wtedy kiedy fb znowu doda te funckcje")
    #try:
    #    await event.thread.set_nickname(user_id=event.author.id, nickname=event.message.text[5:])
    #except:
    #    await event.thread.send_text("Linux nie moze odczytać polskiej litery, albo wpisałes za długi nick")


async def tvpis(event, client):
    if event.message.text == "!tvpis":
        await event.thread.send_text("Napisz coś po !tvpis, np !tvpis jebać pis")
    elif len(event.message.text) > 50:
        await event.thread.send_text("Może być maksymalnie 45 znaków")
    else:
        image = Image.open("data//tvpis//img.png")
        draw = ImageDraw.Draw(image)
        text = event.message.text[6:].upper()
        save_path = f"data//tvpis//{text}.png"
        font = ImageFont.truetype("data//fonts/FallingSkySemibold-Bn7B.otf", 15)
        draw.text((72, 176), text, (255, 255, 255), font)
        image.save(save_path)
        image.close()
        with open(save_path, "rb") as file:
            files = await client.upload([(save_path, file, "image/png")])
        await event.thread.send_files(files)
        os.remove(save_path)


async def losuj(event):
    try:
        numbers = str(event.message.text).split()
        drawed_number = rd.randint(int(numbers[1]), int(numbers[2]))
        await event.thread.send_text("Wylosowano: " + str(drawed_number))
    except:
        await event.thread.send_text("Losuje tylko pełne liczby (komenda powinna wyglądać podobnie do tej: !losuj 1 10)")


async def tworca(event):
    await event.thread.send_text("Możesz do mnie (twórcy) napisac na: https://www.facebook.com/dogsonjakub.nowak.7")


async def wsparcie(event):
    await event.thread.send_text("""Jeśli chcesz wspomóc prace nad botem, możesz wysłac donejta. Za kazdą pomoc wielkie dzieki!
Paypal: paypal.me/DogsonPL
Konto bankowe: nr konta 22 1140 2004 0000 3002 7878 9413, Jakub Nowakowski
Psc: wyslij kod na pv do !tworca""")


async def wersja(event):
    await event.thread.send_text("DZIĘKUJĘ ZA ZAKUP WERSJI PRO!\nWersja bota: 3.2 + 7.1 pro\nOstatnio do bota dodano:\nNaprawa błędów\nKomenda !tvpis\nDostosowanie bota do nowegp API facebooka\nSzybsze parsowanie stron www")


async def test(event, mutelist):
    if event.thread.id in mutelist:
        await event.thread.send_text("Bot jest zmutowany. Wersja pro")
    else:
        await event.thread.send_text("Test passed! Wersja pro")
