# Asynchronous Bot for messenger

# Webpage: https://dogson.ovh (in beta)

## To run this bot version on your machine, you have to configure this website:  https://github.com/DogsonPl/bot_for_messenger_website_django <br> If you want to run this bot without configuring django website, check this bot version: https://github.com/DogsonPl/bot_for_messenger/tree/without_connection_with_webpage  

## Important note 1: Bot works only on Linux 
## Important Note 2: Bot is in Polish language. Sorry about that, but I created this bot to polish groups on messenger
### Clone the repo:
   ```
   git clone https://github.com/DogsonPl/bot_for_messenger.git
   ```
### Install required packages:
   ```
   pip3 install -r requirements.txt
   ```
## First configuration
In a file _config.cfg_ write your mail, password to your Facebook account, your mysql database server info and your SMTP server info\
**I recommend run bot on your second FB account, because FB can ban your account\
Bot only answers if you have bot in friends**


## All available commands and their description:
**!help** - sends all available commands and their description\
**!strona** - sends link to bot webpage\
**!wersja** - (wersja = version) sends info about bot version and news from the last update\
**!wsparcie** - (wsparcie = support) sends a link to paypal and bank account for people who want support bot\
**!tworca** - (tworca = developer) sends FB profile of the person who created the bot\
**id** - sends your facebook id\
**!koronawirus** - (koronawirus = coronavirus) sends info about coronavirus in the world (total cases, total deaths, total recovered, current cases)\
**!koronawiruspl** - (koronawirus = coronavirus) sends info about coronavirus in Poland (total cases, today cases, total deaths, recovered, current cases, cases per million, number of tests, tests per million)\
**!mem** - sends random meme\
**!luckymember** - draws and mention a random group member\
**!ruletka** - (ruletka = roulette) removes a random person from group (bot must be an admin)\
**!pogoda x** - (pogoda = weather) sends weather from x (for example !pogoda London)\
**!nick x** - changes your nick in group to x (for example !nick friend change your nick in group to friend)\
**!everyone** - mentions everyone on group\
**!utrudnieniawroclaw** - sends difficulties in public transport in Wroclaw (Wrocław is Polish city)\
**!utrudnieniawawa** - sends difficulties in public transport in Warsaw (Warsaw is Polish city)\
**!utrudnienialodz** - sends difficulties in public transport in Łódź (Łódź is Polish city)\
**!moneta** - (moneta = coin) bot makes coin flip\
**!waluta amount from to** - (waluta = currency) bot converts given currency (for example !waluta 10 PLN USD) converts 10 PLN to USD
**!film**- sends random funny film\
**!tvpis x** - (tvpis = tv station) sends TV news bar with x (for example !tvpis Hi sends bar with Hi)\
**!disco**- make disco on chat 😎 (bot changes chat color few times)\
**!powitanie x** - (powitanie = greeting) sets message which bot sends when someone joins to group (for example !powitanie Hi sets welcome message to Hi)\
**!nowyregulamin x** - (nowyregulamin = new regulations) sets group regulations to x (for example !nowyregulamin be cool change group regulations to be cool)\
**!regulamin** - (regulamin = regulations) sends group regulations\
**!say x** - sends voice message (for example !say hello sends voice message where bot says hello)\
**!daily** - give you daily free casino money\
**!top** - sends tree persons which have the biggest amount of casino money\
**!bal** - sends your casino balance\
**!bet x y** - you can bet casino coins(x is how much coins you bet and y is how many % to win you have, for example !bet 10 80)\
**!tip x @mention** - you can send virtual money to your friend (for example !tip 10 @nick)\
**!jackpot** - sends info about jackpot rules, total tickets and user tickets\
**!jackpotbuy x** - user buys x tickets to jackpot\
**!register** - let you play in casino games\
**!email x** - sets your email to x\
**!kod x** (kod = code) - write confirmation code which you should get on your email\
**!zdrapka** (zdrapka = scratch card) - get scratch card and won prize from 0 to 2500, one scratch card costs 5 dogecoins\
**!profil** - sends user statistic data from casino\
**!duel** - duel game, !duel x @mention create a game for x dogecoins with mentioned person, !duel akceptuj accepts game and !duel odrzuć discard game\
**!pytanie** - (pytanie = question) sends random question\
**!szukaj x** - (szukaj = search) search information about x in wikipedia (for example !szukaj python)\
**!miejski x** - search given word definition\
**!tlumacz --lang x** - (tlumacz = translate) translate x to given language (--lang is not required, default is Polish). (examples: !translate Привет, !translate --english Привет)\
**!zdjecie x** - (zdjecie = image) sends image of x (for example !image dog)  
**!play x** - play music x (x can be song name or link to spotify) \
**!kocha @nick1 @nick** - (kocha = love) sends how much @nick1 loves @nick2 \
**!cena x** - (cena = price) sends price of given item (for example !cena shiba inu) \
**!banan @nick1(optional)** - sends how big is your banana (or mentioned person) \
**!osiągnięcia** - (osiągniecią = achievements) sends player achievements \
**!lyrics creator; song_name** - sends lyrics given song