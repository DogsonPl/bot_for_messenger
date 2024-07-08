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
!help, !strona, !wersja, !wsparcie, !tworca, !id, !mem, !luckymember, !ruletka, !pogoda, !nick, !everyone, !utrudnieniawawa, !utrudnienialodz, !moneta, !waluta, !kocha, !banan, !tekst , !stan , !tablica, !pytanie, !essa, !flagi, !kiedy, !leosia
💎 𝐃𝐎𝐃𝐀𝐓𝐊𝐎𝐖𝐄 𝐊𝐎𝐌𝐄𝐍𝐃𝐘 𝐙𝐀 𝐙𝐀𝐊𝐔𝐏 𝐖𝐄𝐑𝐒𝐉𝐈 𝐏𝐑𝐎 💎
!szukaj, !tlumacz, !miejski, !film, !tvpis, !disco, !powitanie, !nowyregulamin, !regulamin, !zdjecie, !play, !cena, !sstats, !say
💰 𝐊𝐎𝐌𝐄𝐍𝐃𝐘 𝐃𝐎 𝐆𝐑𝐘 𝐊𝐀𝐒𝐘𝐍𝐎 (𝐝𝐨𝐠𝐞𝐜𝐨𝐢𝐧𝐬𝐲 𝐧𝐢𝐞 𝐬𝐚 𝐩𝐫𝐚𝐰𝐝𝐳𝐢𝐰𝐞 𝐢 𝐧𝐢𝐞 𝐝𝐚 𝐬𝐢𝐞 𝐢𝐜𝐡 𝐰𝐲𝐩ł𝐚𝐜𝐢𝐜)💰 
!register, !daily, !top, !bal, !bet, !zdrapka, !tip, !jackpot, !jackpotbuy, !duel, !email, !kod, !profil, !osiagniecia, !sklep, !slots
"""

LINK_TO_MY_FB_ACCOUNT_MESSAGE = "👨‍💻 Możesz do mnie (twórcy) napisać na: https://www.facebook.com/dogson420"

SUPPORT_INFO_MESSAGE = """🧧💰💎 𝐉𝐞𝐬𝐥𝐢 𝐜𝐡𝐜𝐞𝐬𝐳 𝐰𝐬𝐩𝐨𝐦𝐨𝐜 𝐩𝐫𝐚𝐜𝐞 𝐧𝐚𝐝 𝐛𝐨𝐭𝐞𝐦, 𝐦𝐨𝐳𝐞𝐬𝐳 𝐰𝐲𝐬𝐥𝐚𝐜 𝐝𝐨𝐧𝐞𝐣𝐭𝐚. 𝐙𝐚 𝐤𝐚𝐳𝐝𝐚 𝐩𝐨𝐦𝐨𝐜 𝐰𝐢𝐞𝐥𝐤𝐢𝐞 𝐝𝐳𝐢𝐞𝐤𝐢 💎💰🧧!
💴 𝙋𝙖𝙮𝙥𝙖𝙡: paypal.me/DogsonPL
💴 𝙆𝙤𝙣𝙩𝙤 𝙗𝙖𝙣𝙠𝙤𝙬𝙚: nr konta 22 1140 2004 0000 3002 7878 9413, Jakub Nowakowski
💴 𝙋𝙨𝙘: wyślij kod na pv do !tworca"""

BOT_VERSION_MESSAGE = """❤𝐃𝐙𝐈𝐄𝐊𝐔𝐉𝐄 𝐙𝐀 𝐙𝐀𝐊𝐔𝐏 𝐖𝐄𝐑𝐒𝐉𝐈 𝐏𝐑𝐎!❤
🤖 𝐖𝐞𝐫𝐬𝐣𝐚 𝐛𝐨𝐭𝐚: 9.8 + 13.1 pro 🤖

🧾 𝐎𝐬𝐭𝐚𝐭𝐧𝐢𝐨 𝐝𝐨 𝐛𝐨𝐭𝐚 𝐝𝐨𝐝𝐚𝐧𝐨:
🆕 !pogoda -f
🆕 !leosia
Ograniczona ilość wysyłanych wiadomości
🆕 !kiedy
"""

download_tiktok = page_parsing.DownloadTiktok()

MARIJUANA_MESSAGES = ["Nie zjarany/a", "Po kilku buszkach", "Niezłe gastro, zjadł/a całą lodówkę i zamówił/a dwie duże pizze",
                      "Pierdoli coś o kosmitach", "Słodko śpi", "Badtrip :(", "Spierdala przed policją",
                      "Jara właśnie", "Gotuje wesołe ciasteczka", "Mati *kaszle* widać po *kaszle* mnie?",
                      "Mocno wyjebało, nie ma kontaktu", "Jest w swoim świecie", "xDDDDDDDDDDDDDDD", "JD - jest z nim/nią dobrze",
                      "Wali wiadro", "Wesoły", "Najwyższy/a w pokoju", "Mówi że lubi jeździć na rowerze samochodem",
                      "*kaszlnięcie*, *kaszlnięcie*, *kaszlnięcie*", "Kometa wpadła do buzi, poterzny bul"]

leosia_quotes = [
    "Kiedy zaczyna się noc, to wychodzą tu wszystkie bestie, bestie, bestie",
    "Kiedy wchodzę na dance floor to pojawia się ich więcej, więcej więcej, więcej",
    "Jestem z moją bestie, chcecie zrobić sobie selfie",
    "Chodzą jak zaklęci, to już dawno nie są dzieci",
    "Wierz mi, wierz mi, wierz mi, wierz mi",
    "Kiedy wychodzę z klubu to jest to pościg",
    "Mordko nie mam prawka, bo i tak codziennie jazda",
    "Nawet jak nie piję to się czuję skołowana",
    "Może to dlatego, że znowu rolluje blanta",
    "Może to dlatego, żе nie jestem tak odważna",
    "I tak wiеcznie na życiowym zakręcie",
    "Odpalam się przy litrze, odpalam się przy setce",
    "Na mojej ulicy to nie ja się wożę Mercem",
    "Chociaż pewnie siana stąd na kontach mam najwięcej",
    "Dlatego chodzę jak młoda boss",
    "W sercu mam ziomali i jak Deemz mam sauce",
    "Lay low, zawsze, lay low, lay low, lej to",
    "Bo to już nie jest hip hop",
    "Puszczam Afro House i Puerto Bounce",
    "I leci Żab i leci Jaś",
    "Widzę większy kadr, bo chcę rozbić bank",
    "Kiedyś zwiedzę z nimi, kurwa cały świat",
    "Jutro jadę do innego miasta (o tak)",
    "Nasze fury nie Volkswagen Passat (nie Passat)",
    "Siedzę w nowym Audi, a ty Opel Astra (bieda)",
    "Siedzę luksusowo, a ty jak hałastra",
    "Wchodzę na DJ-ejkę, robią hałas (zróbcie hałas)",
    "Zawsze gotowa na te wystąpienia dla mas (dla Was)",
    "Gotowa, żeby zagrać jak najlepiej dla Was (dla mas)",
    "Gotowa pozamiatać tę scenę na szałas (rozpierdalać)",
    "A potem spierdalać",
    "Jak będzie trzeba to przez Kanał La Manche",
    "Może moim domem kiedyś będzie Anglia",
    "Może moim domem kiedyś będzie Francja",
    "Na razie nie uciekam, bo mnie cieszy sława",
    "Cieszy mnie Pinacolada, pita na Dominikanach",
    "Rejon Wyspy Punta Cana, już za dużo opalania",
    "Już za dużo swagowania, zaraz wybuchnie mi bania",
    "Nie mam więcej do jarania, nie mam więcej do gadania (puff, puff)",
    "Gram sety gorące jak Diplo, cały kraj się jara moją ksywką",
    "Cały kraj jara się moją bibką, kiedy za stołem miksuję ten hip-hop",
    "Miksuję ten hip-hop, wszystko, co zrobiłam to było dopiero intro",
    "Z dancehallem miksuję ten hip-hop (bomboclaat)",
    "Skaczesz na parkiecie, a zrobiło się już widno",
    "Kiedyś to codziennie miałam klub, teraz mam tu pełny stół",
    "Z ziomalami dzielę się na pół, każdy ruch to wspólny move",
    "Chcę dostać ordery królowej imprezy, a potem królowej afterów (czemu?)",
    "Bo mi się należy (tak jest!), wie każdy, kto ze mną coś przeżył",
    "Noce nie bywają spokojne, będzie trzeba to pójdę na wojnę",
    "Na ulicy w świecącej kurtce Moncler będę walczyć o zwrot moich wspomnień",
    "Bo chcеcie nam zabrać ten czas i te radosnе bankiety",
    "Oddajcie lokale i hajs, nie cenzurujcie poety",
    "Czekam aż znowu będziemy popijać Bacardi w klubie ze szklanki",
    "Gdy na parkiecie nasze fanki, a na głośniku Nicki i Cardi",
    "Nie mów nikomu, łamiemy zasady, bo w domu też bywa funky",
    "Kiedy wpadają koleżanki, zaczynają się hulanki",
    "Czekam aż znowu będziemy popijać Bacardi w klubie ze szklanki",
    "Gdy na parkiecie nasze fanki, a na głośniku Nicki i Cardi",
    "Nie mów nikomu, łamiemy zasady, bo w domu też bywa funky",
    "Kiedy wpadają koleżanki, zaczynają się hulanki",
    "Wbijaj do mnie na house party (okej!), z nami bawią się sąsiadki (tak jest!)",
    "Najpierw kozackie wieczory, potem w radiu Bolesne Poranki",
    "Mój typ melanżu to takie tańczone, rąk pełna sala przez noc i przez dobę",
    "Buja się cały klub z nogi na nogę, chcę już wieczory spędzać poza domem",
    "Baila Ella, Baila, Baila Ella",
    "Cała sala tańczy tu, to Macarena",
    "Basia, Ela, Maria i Helena",
    "Twoja dupka wraca do nas jak bumerang",
    "Każdy melanż, u nas w każdy melanż",
    "Jest afera, kiedy szukamy aftera",
    "Prawa ręka, lewa ręka",
    "Prawa noga, lewa noga",
    "Tańczę twerka już od dziecka",
    "Ciężka głowa nie od zioła",
    "Ale, dajcie mi gibona",
    "Wódka jest zmrożona",
    "Może zaraz skonam",
    "Ludzie tańczą już na stołach",
    "Tus caderas, mueve tus caderas (seniorita)",
    "Kręć biodrami, pokaż im jak to się robi teraz",
    "Tus caderas, mueve tus caderas",
    "Dale sexi mami, zatańcz dla moich fellas",
    "A jak kończy się zabawa",
    "Es un problema de nada",
    "Zaraz znajdzie się następna",
    "Zamawiamy już uberka",
    "Słuchamy 'Get Busy'",
    "Z tyłu jest już freaky",
    "Pan się pyta czy podgłośnić",
    "Ja mu mówię si, si",
    "Guantanamera",
    "Zwykłe osiedle, nie żadna fawela",
    "Odkrywam lądy jak Ferdek Magellan, Vasco da Gama",
    "Chociaż to miasto Warszawa",
    "W którym ciągle zabawa (o)",
    "Perro puka do sąsiada (o)",
    "Szybciej bije pikawa (o)",
    "Pęka łeb jak piniata (o)",
    "Z farszem jak Empanada",
    "Po-chowane wiadra",
    "Kręci się jeszcze rolada",
    "Trze-ba ją dojarać",
    "Entramos na balet",
    "Chyba ktoś nam bije brawo",
    "Widzę twoją damę całkiem nieźle naje... (mkhm)",
    "Chyba mi się zdaje, chyba mi się to zdawało",
    "To nie moja sprawa co się tutaj odje... (nie moja)",
    "Nie słucham Gotye, słucham Offset",
    "Słucham Los Del Rio",
    "W Rio wieczorkiem",
    "Chciałabym znowu być w Santiago de Cuba",
    "Tańczyć tam dancehall, chodzić po klubach",
    "Jeść słodkie mango, pływać w jeziorach",
    "Pić rum z limonką, nieważne, jaka pora",
    "Chociaż teraz ciągle jesteśmy w Polsce",
    "To z tobą dni są tak samo gorące",
    "Dlatego chcę cię kiedyś zabrać tam ze sobą",
    "Też masz te rytmy w sercu z brazylijską stopą",
    "Takich jak ja i ty",
    "Nie znają nawet Karaiby (nie, nie, nie!)",
    "I to jest piękne",
    "Codziennie budzę się z uśmiechem (yeah, yeah!)",
    "Czekają na nas Galapagos",
    "I czeka na nas Santorini",
    "Potrzebny mi tam tylko twój głos",
    "Spokojny jak ci jogini",
    "Nie mogę spać",
    "Za dużo mam dziś w planach",
    "Znów jadę grać",
    "Tak dużo miast na mapach",
    "Chcę cię zabrać tam",
    "Gdzie stolicą Hawana",
    "Daj mi tylko czas",
    "Tak dużo wysp na mapach",
    "Bez supermocy jak Batman (Batman)",
    "Całe życie to szach-mat (szach-mat)",
    "Tutaj każda porażka (-rażka)",
    "Robi z ciebie giganta (giganta)",
    "Choć nie jestem jak Badman",
    "Wersy hot jak Jamajka",
    "Czasem czuję się rasta",
    "Lecz już z tego wyrastam (yeah, yeah!)",
    "Postawię wszystko to na jedną kartę",
    "Mam dwadzieścia jeden lat, moje życie to blackjack",
    "Wygrywam tu każdą partię",
    "Obliczam ten profit, tak szybko jak bankier",
    "Nie wiem, czy to wygrywanie jeszcze ma znaczenie",
    "Bo jest mi tu tak dobrze, kiedy jestem obok ciebie",
    "Będę dziś pracować dłużej, no bo dalej wierzę",
    "Że za jakiś czas kupimy sobie dom z basenem",
    "Nigdy nie obstawiłam losu na aukcji",
    "Od dawna gotowa na to życie w branży",
    "Mordko, tu nie ma niczego bez pracy",
    "Trenuję tę muzykę już od pierwszej klasy",
    "Prognozuję mocny wzrost swoich akcji",
    "Hej, kochanie, jeszcze będziemy bogaci",
    "Obiecuję sobie ślub na Hawaii",
    "Staniemy się wielcy, chociaż kochamy się mali",
    "Jungle Girl, moje kwiaty z Cali",
    "Amsterdamu i Hiszpanii",
    "Szczyty Eiffla jak te w Paris",
    "Zapach lepszy od Armani",
    "Jungle Girl, nocą dzika bestia",
    "Non stop w łowach, nie od święta",
    "W torbie gelato torebka",
    "Pójdzie z dymem jeszcze jedna",
    "Jeszcze jedna",
    "Wyszłam tu tylko po paczkę, zobaczyłam ziomków paczkę",
    "Wyciągają mnie na bankiet, mieli dzisiaj dobrą passę",
    "Już mnie nudzą te melanże, chociaż uzależnia parkiet",
    "Miałam siedzieć z jointem w wannie",
    "A nie kręcić nóżką zgrabnie, powabnie",
    "Jak Michael, Jackson",
    "Jeśliby umiał dancehall",
    "Dla mnie to był popu king",
    "Dla tych chłopców ja to queen",
    "Z dżungli, jak różowowłosa Vi",
    "Mocne uderzenie w bit",
    "Skacze po drzewach jak małpka",
    "Znowu dobra fazka",
    "Świeży temat w samarkach",
    "Candy na obrazkach",
    "Wszystko tu pachnie owocami, jak moje strawberry",
    "Nie zadzieramy z władzami, gdy dużo w kieszeni",
    "Mam zieleni na własny użytek",
    "Mocne dragi to zabytek",
    "Chodzę w nocy z lekką głową",
    "U was w nocy bazyliszek",
    "Mam różowe włosy i różowy kocyk",
    "Różowy dywanik, na nim hajsu cały stosik",
    "I mam lekko, a nie ciężko",
    "Za to każdy chce mnie strzepnąć ze sceny",
    "I-i-i tak zrobię te numery",
    "I-i znowu zrobię liczby chociaż żyję w środku dziczy",
    "Ludzi trochę pojebało, znowu brakuje mi ciszy",
    "Znowu wkurwię tamtych dziadów, którym nienawiści mało",
    "Mają za złe tatuaże i to moje, i to moje wyrafinowanie",
    "Przepraszam za przeklinanie tylko moje babcie",
    "Czytam dużo książek, kurwa czytać mi nie każcie",
    "Chce zobaczyć Azję, znowu tańczyć salsę",
    "Prze-prze-przez to znów nie zasnę (przez to znów nie zasnę)",
    "Przez to znów nie zasnę (przez to znów nie zasnę)",
    "Wiem, jak wykorzystać szanse",
    "Był-był-byłby spokój, gdybym zamieszkała na Alasce",
    "Nie znasz moich kroków, dlatеgo sam piszesz baśnie",
    "Dużo osób patrzy mi na ręce i pismo na kartcе",
    "Przyznam się tylko do tego, że żyje jak w bajce",
    "Zapracowałam na to na barze w każde lato",
    "Zapracowałam na to, mam dużo, a miałam mało",
    "Modelki, blogerki, z każdą chcę fotkę",
    "Tancerki, stonerki, zbijamy piątkę",
    "Pozdrawiam serdecznie dziś każdą mordkę",
    "Pozdrawiam serdecznie Monikę Brodkę",
    "Raperki, DJ-ki, wpadam na koncert",
    "Krupierki, dealerki, wyciągam forsę",
    "Pozdrawiam serdecznie dziś każdą mordkę",
    "Oprócz lamusków, którzy mają problem",
    "Życie, jak z bajki anime",
    "Słucham Gucci Mane, Solitaire",
    "Karty dalej w grze (okej)",
    "Chociaż słyszę głosy tak jak Dave",
    "To nie wpadam w paranoję",
    "Kontroluję te nastroje",
    "Like To Party z Burna Boyem",
    "Drakiem, Riri lub we dwoje",
    "I myślę o słońcu (tak jest)",
    "Wracam do początku (okej)",
    "Wracam do początku (gdzie?)",
    "I myślę...",
    "Stoję na dwóch nogach twardo",
    "Stąpam po ziemi, Lambo Gallardo",
    "Może kiedyś to się zmieni",
    "Ale dzisiaj nie, dzisiaj jestem tam gdzie chcę",
    "Teraz wiem, że zwiedzę wyspy na Bahama",
    "Sobie zrobię piknik, nagram Afro płytę, jak WizKid",
    "Wolę upić się rumem, nie whisky",
    "Czasem się czuję, jak piratka (arrr)",
    "Jakbym rozbijała banki na statkach",
    "Dresscode, jak wariatka",
    "Tak rozbijam bańki już na kontraktach",
    "I wiem, że nie zmęczy mnie ta branża (nigdy)",
    "Alе nie, nie spocznę na laurach (nigdy)",
    "Nie lubię, gdy kończy się zabawa (nigdy)",
    "Dlatеgo zawsze chodzę tylko w dużych stadach",
    "O tym, że skończyły się granice",
    "To już nie to samo życie, kiedy budzisz się na szczycie",
    "Kiedy budzisz się na szczycie, to każdego dnia masz weekend",
    "I każdego dnia masz pracę, a wyjazdy to już nie wakacje",
    "Na Ba-ha-my, moja pierwsza destynacja",
    "Ma-le-di-wy, w Azji jest kolejna stacja",
    "Chcą być, jak my",
    "Rapowa arystokracja, walczą jak lwy",
    "Ale już zamknięta klatka",
    "Studio jest jak zoo, a scena to nasz wybieg",
    "Jak masz coś do pokazania, najpierw pokazuje siłę",
    "I nie ważne, czy to przekaz, czy tylko twój charakter",
    "Odkryłam ostatnią kartę",
    "I myślę o słońcu",
    "Wracam do początku",
    "Wracam do...",
    "Tańczę shoot jak Blocboy JB (Blocboy)",
    "W moim składzie wszyscy trendy (modni!)",
    "Bujasz się do beatu, baby (mała)",
    "My nie jesteśmy święci (niegrzeczni!)",
    "Jesteśmy w klubie, tu się coś kroi (się kroi)",
    "Dla nas poproszę dziesięć Aperoli (tak dużo?)",
    "Dla kolegi czystą bez coli (ale twardziel!)",
    "After kręcimy na Żoli",
    "Wysoki blok na Ochocie, u nas nigdy nie było gorzej",
    "Wielki dom na mały procent, u nas nigdy nie było skromnie",
    "Serce jak koń, ruchy jak kot, bo od dziecka walczę o swoje",
    "Kurs na skok na bank, z zaskoczenia biorę co moje",
    "Pamiętam jak miałam 6 lat, wielkie domy z ogródkiem i życie spokojne",
    "Pamiętam jak zmienił się świat kiedy zabrakło kart, banki nie były hojne",
    "Nie zrozum mnie źle droga mamo, mi nigdy nic nie brakowało",
    "Bo pieniądze szczęścia nie dają, a czasem najbliższych odbiera ci prawo",
    "Jak Janusz wiem co to klasa średnia, od dziecka wiem jak to jest uciekać",
    "Stracić wszystko i przegrać, dobrze, że muzyka jest wieczna",
    "Dobrzе, że zawsze miałam potencjał, wolałam się uczyć, niż żеbrać",
    "Dlatego teraz zamiast pracować piszę kolejny poemat",
    "Chociaż droga była trochę kręta (okej) to pełna skarbów jest meta (tak jest)",
    "Mam wszystko o czym kiedyś marzyłam, zasypiam uśmiechnięta",
    "Dziś z przeszłości czerpię siłę, co cię wzmocni to nie zabije",
    "Kiedyś życie nie było nic warte, a dziś jest pięknym motylem",
    "Teraz mam swój rok tygrysa i patrz jak szczerzę kły",
    "Chcę, żeby każdy widział, tu nie ma smutnych dni",
    "Pracuję, wygrywam, wygrywam, pracuję, moje wieczne koło się toczy",
    "Tworzę, zarabiam, wyjeżdżam, wydaję, aż ze szczęścia pocą się oczy (kap, kap)",
    "Jeden dzień bez słońca",
    "I moja głowa",
    "Nie jest już tak spokojna",
    "Przesiadka w Doha",
    "Nie pisz, bo jestem offline",
    "Teraz kieruję się na Malediwy",
    "Buduję dom mojej małej rodziny",
    "Nie dbam o hasła i nie dbam o piny",
    "Jak jesteś zły to się nie polubimy",
    "Stoicki spokój",
    "Bookuje nowe lokum",
    "Mam coś na oku",
    "Cie-Ciebie po zmroku",
    "Słoneczna Jamajka, słoneczna Sri Lanka",
    "Dziś nie wiem jaką wyspę wybrać",
    "Spory i kłótnie to nie moja bajka",
    "Nie znam się tak dobrze na liczbach",
    "Jak masz coś kraść byle tylko nie grajka, bo w mieście to każdy bandyta",
    "Chce okraść mnie z uczuć zawsze jak ta mżawka",
    "Bez słońca to zawsze jest przypał",
    "Nie ma chmur, więc zakładam nowe oksy Prady",
    "Nie mam słów na to czemu ludzie chcą się ranić",
    "Tysiąc gwiazd, każda wystrojona jak na gali",
    "Ty masz stres, ja przepalam to na kilogramy",
    "Robię comeback na jakiś egzotyczny spot",
    "Daleko stąd",
    "Albo tylko do Włoch",
    "Dziś mam ochotę na jakiś ekstremalny sport",
    "Z klifu skok",
    "Albo ze spadochronem",
    "To nie prywatny samolot",
    "Ale mamy business class",
    "Teraz już nie dbam o hajs",
    "Nie mam na to czasu",
    "Chcę na Bali zobaczyć las (dziki)",
    "Spacerować plażą (piękną)",
    "Nie było tak dawno (nie, nie)",
    "Dziś nic mi nie każą",
    "Let's go",
    "Nie wiem o co chodzi tamtej suce, o",
    "Nie wiem o co chodzi twojej grupie, ej",
    "Nie wiem jaki znaczek masz na bluzie",
    "Kto ci kupił taki outfit, kto zapłacił za tę buzię, nie, nie wiem",
    "Nie wiem o co chodzi, mam to w dupie, yeah",
    "Nie wiem o co chodzi co za ludzie, nie",
    "Nie wiem skąd się biorą takie niunie",
    "One chciały być tu pierwsze, ale chyba już jest too late (Yeah, yeah)",
    "168, szybko tak jak lubię",
    "Bpm'ów w twoim klubie",
    "Pajac z vipa znowu pruje się",
    "Zabierz łach i swoją dziunię",
    "Two-twoją dziunię",
    "Mordo nikt tu nie szanuje cię",
    "Wracamy z ekipą na backstage (Co?)",
    "Ona na stoliku tańczy breakdance",
    "Jej chłopak wygląda jak skejter",
    "Ale rzuca trawę na moje osiedle",
    "Nie wiem o co chodzi jeśli pytasz (Nie, nie wiem)",
    "Mordko, dla mnie wczoraj było dzisiaj (Later)",
    "Nie wiem o co chodzi jaki Michał (Who that?)",
    "Nie wiem o co chodzi jaki przypał (Oh fuck)",
    "Dzień dobry, panie władzo, chyba nie wiem o co chodzi",
    "Jaki hałas, kto to zgłosił, czy sąsiadka znów donosi?",
    "Pik, pik, dzwonek dzwoni, łyk, łyk troszkę Coli",
    "Bling, bling, na mej dłoni, 300 koni nie mój bolid",
    "Porachunki mam na Żoli, trzeba wyjaśnić Marioli",
    "Że wszystkie społeczniary w tym mieście się pierdoli",
    "To znienawidzona młodzież z waszej klatki",
    "Gorące pozdrowienia dla pani wariatki",
    "Nie spodziewałaś się pocisku w piosence",
    "Ty kurwo na piętrze psujesz naszą dzielnie",
    "Nie spodziewałaś się, że ktoś się odezwie",
    "Jebać ten twój PiS, ja mam melanż w kawalerce",
    "Te magiczne świrki zrobią ci tu cruciatus'ka",
    "W jednej ręce różdżka, ale w drugiej susz mam, biorę z nimi buszka",
    "Moi ludzie tacy czarujący - Harry Potter",
    "Ujawniamy karty na koniec bo to jest poker",
    "Każdy ziom to baller, każdy ziom to stoner",
    "Nigdy nie będę broke, stawiam na to jak broker",
    "Głowa w chmurach, palimy skuna",
    "Puff, puff biorę bucha, druga tura - puff, puff",
    "Rozumiemy się bez słów jak w kalamburach",
    "Skład nie wije sieci; Tarantula",
    "Robię interesy, nowa faktura",
    "Internaziomale - agentura",
    "Nowe dresy, z węża skóra",
    "Włos jak u lalki, głos jak u lalki, Malibu Barbie, drogie zabawki",
    "Jak tańczę, to Tai Chi, jak gramy to house'ik, a hity są Hi-Fi",
    "Tu każdy jest lucky, tu każdy ma styl i tu każdy jest jakiś",
    "Oni myślą, że to catfish, czemu się dziwnie patrzysz?",
    "Po co kupiłeś naszyjnik?",
    "W pizdę wsadź se te diamenty (woo)",
    "O czym ty pierdolisz, jak masz w głowie tylko siano?",
    "Częściej gadasz z jubilerem, niż rozmawiasz z własną mamą",
    "Znam cię od dzieciaka, ale zrobiłeś mnie w balon",
    "Mówiłeś, że coś się zmieni, między nami jest to samo",
    "Bywalczyni klubów, to jest 2020 class",
    "Chłopy, dupki, bas, zarobieni aż po pas",
    "ZAiKSy czekają, nasze nuty lecą wprost do kasy",
    "Codziennie nowy hajs, icon, tak jak Wielki Gatsby",
    "Za długie weekendy, za krótkie tygodnie",
    "Mam słownik jak MC i Baggy te spodnie",
    "Mam pełne koncerty, a booker pieniądze",
    "Moi ludzie mają się dobrze",
    "Palą pochodnie (okej)",
    "Wielki joint tu płonie",
    "Bo przez nas jest to modne",
    "W piątek wieczór pije piwko, jaram lufkę, degustuję wódkę",
    "Jestem z twoim synem, zaczepiam twoją córkę",
    "Nie wszystek umrę, sarka.wav, okej",
    "Bawię się z kumplem, podkręć interfejs",
    "Daj to głośniej Wroobel",
    "Niech leci w każdym klubie",
    "Nasz DJ wie, co lubię",
    "Wie, że tych emocji nie ostudzę",
    "Słuchają nas ludzie w każdej budzie, w każdej radiostacji",
    "Mam fanów z pojebanych akcji",
    "Kiedy ja dzwonię do Ciebie, w kółko mamy jakiś problem",
    "Muszę się martwić o siebie, Ciebie na bank nie zapomnę",
    "Z oczu znowu lecą krople, nie pomoże five star hotel",
    "Wolę być z Tobą w samolocie",
    "Fake uśmiech jak Joker, blefuje jak w poker",
    "Gdy piszesz to gówno, bo nie jest mi okej",
    "Traktujmy się równo, traktujmy się dobrze",
    "Chcę z Tobą być długo, nie tylko na moment",
    "Jak dużo jeszcze smutnych dni",
    "Nienawidzę tracić chwil",
    "Ty Michael, a ja Billie Jean",
    "Bo liczysz się już tylko Ty",
    "Wiem, że ciągle nam ucieka czas",
    "Nie chcę już innych opcji, mam The One (mam The One)",
    "Jak mówisz, że się zmienisz dla nas",
    "To kocham słuchać twoich pięknych kłamstw",
    "Pachniesz jak Maison Margiela",
    "I pachniesz jak każda szczęśliwa niedziela",
    "Wiesz, że jestem znów w studio, więc znów nie odbieram",
    "A piszę love songi, nie robię kolegi, rapera",
    "Kici kici meow",
    "Pliki jakbyś ojebał bank",
    "Gdzie są drinki, pijesz to tańcz",
    "Zawodniczki jak w MMA",
    "Taka latina, queen jak Selena",
    "Kręci się wokół twojego palca",
    "Świecą diamenty z pierścienia, nie stal",
    "Tu same koty, ona nie chce psa",
    "Dirty Diana, ma Ciebie dziś w planach",
    "Otwieraj garaż, tu wszystko jest w oparach",
    "Carlos Santana, szybszy niż jego gitara",
    "Jebie benzyną, ryk Jaguara",
    "Nie wiem jak nauczyć kogoś kochać, ale wiem jak dobrze żyć",
    "Lubię się zgubić w imprezowych nocach, lubię się zgubić tam gdzie Ty",
    "Mam patenty na szczęście, przepis na uśmiech",
    "Klucz do dobrej zabawy",
    "Będę lekiem na serce, lecz zniknę, gdy uśniesz",
    "Czemu jesteśmy tacy sami?",
    "Co myśmy zrobili, że nie toniemy już w morzu tequili",
    "Co myśmy zrobili, że nie spędzamy razem ani chwili",
    "Dalej pragniemy życia, normalnych ludzi",
    "To poszło za daleko i już nie jest takie łatwe",
    "Lecz wszystko jest puste i kiedyś nas zgubi",
    "Myślę, że było tego warte",
    "Boję się kochać",
    "Mało było dni, w których coś mogło jeszcze mnie zaskoczyć",
    "Teraz jesteś ty, a ja jak wariat nigdy nie mam dosyć",
    "Słodki jak żelki, silny jak cios z uśmiechem prosto w oczy",
    "To trochę cringe, przez Ciebie sexy stał się shadowboxing",
    "To trochę cringe, więc znowu na DM ślę Ci małe kotki",
    "Jak będziesz się bić - ja zawsze w pierwszym rzędzie, jak te fanki",
    "Co weekend odpalamy wrotki i codziennie gasimy blanty",
    "Nie wiem, czy to sny, czy, ziomek, urwałeś mi się z innej bajki",
    "Dni z Tobą są jak pierwszy Opener, jak pierwsze gibony i pierwsze wagary",
    "U-, u-, ucieczka od starych, te szlugi, pojary, pierwszy hajs wydany",
    "Na stare mieszkanie i nowe Jordany, na małe bluzeczki, jakieś okulary",
    "Jak noc Carlo Rossi i LM klikany, je-, je-, jesteś dojebany",
    "Love story jak z Hanny Montany, bo teraz się ciągle chowamy",
    "Choć wie o nas już cała Polska, wciąż low-key wolimy być sami",
    "Może po mieście krążą plotki i może w necie latają już fotki",
    "Styl dla mnie to jest tak private, jak odblokowanie na odcisk",
    "Bo teraz ja wiem jak wygląda z rana Twoja twarz",
    "Choć nie chcesz mi pokazać, dobrze wiem, że czujesz strach",
    "I każda laska chce się wkleić na Twój Instagram",
    "Ja chcę być plastrem, który sklei Ci najgorsze z ran",
    "Jak ćmy do światła i księżyc do nocy, cola do chipsów i trawa do rosy",
    "Jak ocean Twoje niebieskie oczy, jak rozgwiazdy moje różowe włosy",
    "Tak się przyciągają jak pszczoły do ula, jak joker do asa, królowa do króla",
    "Jak w portfelu stówa, tej dupki miniówa, pa-, pa-, pasujesz na ulał",
    "Love story jak z Małej Syrenki, Ty masz pałac, ja rozum Arielki",
    "Oboje umiemy być sami, ale razem jesteśmy w chuj lepsi",
    "Twoją mamę lubi moja mama, a Ciebie lubią moje bestie",
    "Więc po co coś dłużej udawać? Chodź się całować na backseat",
    "Ale syf, my tu grzeczny balet a lamus wydzwonił psy",
    "Wóda, pas i weed, wóda, pas i weed",
    "Jebać ich",
    "Nie otwieraj",
    "Nie-nie-nie otwieraj drzwi",
    "Ijo, ijo, kto jest żmiją? kto poskarżył na nasz house?",
    "Bi-biją żonę w domu, narzekając na hałas",
    "Dokły frajer, taki sąsiad nie ma wstępu na melanż",
    "I zamula dupę w domu, a nie psuje ludziom trap",
    "Łap, kolejnego bucha, ta afera nas nie rusza",
    "Coś wpisuję do arkusza, pierdolony a nie muszę",
    "Się nazywa Marek Susza, bo nie rucha od jakiś stu lat — co za stulejarz",
    "Kick, rozjebał chyba sufit, co za przypał, zrób im BLIK",
    "Nikt chyba się nie łudzi na naprawę, starczy mi",
    "Niech dziecko się nie budzi — załatwimy jakiś kwit",
    "I tak nie otworzę drzwi, nie otworzę drzwi",
    "Mordzia łatwo, mikrofon za nim Aston",
    "Nagrywam EP-kę z siostrą, tak że światła tu nie gasną",
    "Żeby była jasność, Francis goat, jak Benny Blanco",
    "W tym domu Project X, u was tylko klasztor",
    "Pięć minut, już minęło, więc zostanę tu na zawsze",
    "Proszę nie płaczcie, to słodziakowy anthem",
    "W was okrągłe zero, a ja znowu robię bańkę",
    "(Wiem to nie fair) Zażalenie wyślij faksem",
    "Buzia młoda — Kate Moss",
    'Leci Kizo — "Czempion"',
    "Wygląda jak anioł, no a w sercu zieje piekło",
    "Na dysku same sztosy i nie są to pornosy",
    "Ciągle coś pieczemy, więc nigdy nie wyjdę z formy",
    "Widzę ciągle węszysz, bo brakuje Ci na nosy",
    "Tu się sypie mąka, tylko jak robimy sosy",
    "Kręcą mnie kamienie, szlifuję je, jak Rolling Stones",
    "Dzisiaj łapię nowe brzmienie, a jutro już zmieniam ton",
    "Chwilę, jestem pewna siebie, a potem chcę zniknąć stąd",
    "W sumie jebać to, rap to nowy rock'n'roll",
    "Ja to twoja crushi, a Ty to mój crush",
    "Plotkujemy nawet w snach",
    "Chcę swój pierwszy raz, z tobą przeżyć, jeszcze raz",
    "Ty to moja LSD, miеszasz w głowie tak jak drink",
    "Nigdy nie ufałam im, ale Ty to szczеry typ",
    "Dla mnie jesteś słodki, lubisz puszczać moje zwrotki",
    "Uległam tobie bejbi, chociaż zawsze byłam bossy",
    "Zabierz mnie do Paris, tam zrobimy sobie fotki",
    "Adoptujmy pieski, potem adoptujmy kotki (Meow)",
    "Stoję pod twoim domem, a w oknie widzę twój cień",
    "Mam cię na oku, jak stalker — nie mogę oprzeć się",
    "Zawsze ich daję w lewo, a Ty to double match",
    "Oni są jak Pro Evo, a Ty jak FIFA, EA",
    "Podoba mi się twój game, ich gadka dla mnie to fame — pray up",
    "Ty jesteś słodki, jak cake",
    "Najlepszy w tym mieście grail",
    "Nadal wspominam każde odpierdalanie",
    "Patrzę na niego, przypomina mi się wszystko",
    "Miałam tak dużo a zostawiam Ciebie dziś, bo...",
    "Tu nie mam nic, dlatego dalej biegnę",
    "Chodź ze mną, cho-cho-chodź ze mną",
    "Może w afekcie znajdziemy lepsze miejsce",
    "Rzucę wszystko, żeby znaleźć szczęście",
    "Mój różowy dom, obok twój błękitny",
    "Twój zabawkowy wóz i nocny fastfood",
    "Wspólnie śpiewanych wersów",
    "Ale nie ma cię dziś",
    "Chyba nie miało to sensu, bo...",
    "Mam układy, mam zasady",
    "Mam zalety i mam wady",
    "Mam kotlety i mam chleby",
    "I mam w piździe wasze rady",
    "Możesz pisać coś pod postem, a ja będę dalej smażyć",
    "Nikt nie zrobił takiej pengi, na czytaniu komentarzy",
    "Coś tam pierdolą, bla bla",
    "Twoja hoe, to moja fanka",
    "Moje skoki — Balenciaga (Swag)",
    "Ty promujesz markę kasztan",
    "To fabryka hitów, pozdro OTSO",
    "Ja i Bambina, czytaj — PG$",
    "Słuchanie dupeczek, to teraz flex",
    "Nie słucha nas tylko jebany pies",
    "Wpadaj do mojej bandy, zrobię z ciebie Nicki, Cardi",
    "Będziecie stać na Louis, Supreme, Prade, Moncler, Fendi, Marni",
    "Łowię tu w stawie pięknych rybek, potem wyjeżdżam do Azji",
    "Łowca okazji, zapraszam na casting",
    "Chcę się zamknąć w moich czterech ścianach, tam gdzie jest okej",
    "Chcę nie słyszeć nawet głosu ciała, ściszyć każdy dźwięk",
    "Zostać sama z moją ciężką banią, sprawdzić co w niej jest",
    "Bo już nie wiem, nie wiem",
    "Na głośniku After Hours, ciągle pojebany balet",
    "W weekend szaleć, gdzieś przy barze",
    "Każdy koncert pełne sale",
    "Za dużo wódki, za dużo ludzi",
    "Za dużo hajsu, za dużo spraw",
    "Wyłącz ten budzik, dziś nie chcę się budzić",
    "Zostanę pod kołdrą, bo mam tu swój świat",
    "Będę upadłym aniołem, jeśli tak pociągnę, a nie chcę zawodzić już was",
    'Zaczęły się czasy, gdzie często usłyszysz ode mnie: "idę spać"',
    "Wyjdź, idź i wróć i znowu w kółko",
    "Pij, krzycz i płacz — mam nową północ",
    "Wszyscy klaszczą, na mikserze dalеj przester",
    "Dalej przеster, DJ robi przejście",
    "Cały parkiet leci pod czerwoną kreskę, pod czerwoną kreskę",
    "Widzimy się na mieście",
    "Tęsknię za jointem na ławce, za zerem na karcie",
    "Nie mieliśmy zmartwień i żyło się łatwiej",
    "Pierwsze miłości i lufki za szkołą",
    "Tęsknię za luźnym porankiem, gdy humor mam w kratkę",
    "To życie jak w bajce, jest krzywym zwierciadłem",
    "Gdy czuję smutek, to wylewam go na papier, go na papier, go na papier",
    "Już sama nie wiem, przecież z Tobą jest mi łatwiej, jest mi łatwiej, jest mi łatwiej",
    "Hajs to tylko papier, ja nigdy nie byłam graczem",
    "Choć mnie nazwą hazardzistą, dalej stawiam na relację",
    "Bez Ciebie cali, to słaby skun",
    "Bez Ciebie dom, to tylko gruz",
    "Bez miłości brak mi słów, a bez przyjaźni tracę grunt",
    "W koło tyle uśmiechniętych twarzy, zakochane pary",
    "Wszyscy chcą się bawić, a ja ciągle szukam tu Nirvany",
    "Chociaż wszystko mamy, wszystko mamy",
    "Te-te-te-te-te numery mówią za mnie, mówią za mnie (Bonjour Francis, Deemz, ma ten sauce), mówią za mnie",
    "Hokus-Pokus, czary mary, obezwładnia ich mój czar",
    "Potem mają koszmary i znowu nie mogą spać",
    "Femme fatale, parę złamanych serc i parę otwartych ran",
    "I chyba nie chcę już tak (O-o-o-o)",
    "Może tym razem inaczej, niech nikt już przy mnie nie płacze",
    "I zamiast tańczyć jak debil, zamknę się z Tobą na chacie",
    "Po co nam gadki? Zapiszę uczuciami wszystkie tracki",
    "Kochaj mnie zawsze i jebać już te wzloty, upadki",
    "Halo?",
    "Właśnie stary nic nie pamiętam",
    "A dzisiaj już jest sobota, czy co?",
    "Diabeł mnie kusi czerwoną bielizną",
    "Zrobiło się widno, trzymaj się blisko",
    "Rosnę jak bitcoin, no bo nam pykło",
    "Wszędzie nasze nuty, kiedy wchodzisz na TikTok",
    "Odsłuch jak Rick Ross, wizje na przyszłość",
    "Coś pierdolą dzieci na discord",
    "Weszłam na ponton, wchodzę na konto",
    "Trzy lata, to co tam widzę to kosmos",
    "Zwiedzamy Wietnam, zwiedzamy Boston",
    "Spadłam na ziemię i czuję się bosko",
    "tańczy tak jak gwiazda go-go",
    "w tłumie ludzi kręci pogo",
    "wygląda jak jakiś posąg",
    "a, czuję się bosko",
    "Mówią jedź prosto, ja robię rondo",
    "Chcą mnie tu ciszej, to jest o mnie głośno",
    "Chcą czegoś szybciej, to mają to w slow-mo",
    "Tańczę jak diabeł, bo wszystko mi wolno",
    "Dziwne, damy, obraz rozmazany",
    "Duchy, zjawy, zwiedzam ich koszmary",
    "kręci złotą aureolą",
    "trochę zakazany owoc",
    "chyba dawno nie jest sobą",
    "A ja w swoich snach, a czuję się bosko"
]


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
