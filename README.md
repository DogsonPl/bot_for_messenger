# Asynchronous Bot for messenger
## Important note 1: Bot works only on Linux 
## Important Note 2: Bot is in Polish language. Sorry for that, but I created this bot to polish groups on messenger
### Clone the repo:
   ```
   git clone https://github.com/DogsonPl/bot_for_messenger.git
   ```
### Install required packages:
   ```
   pip3 install -r requirements.txt
   ```
## First configuration
In a file _Bot/data/mail_and_password.json_ write your mail and password to your Facebook account.\
**I recommend run bot on your second FB account, because Fb can ban your account**

## All available commands and their description:</h3>
**!help** - sends all available commands and their description\
**!wersja** - (wersja = version) sends info about bot version and news from the last update\
**!wsparcie** - (wsparcie = support) sends link to paypal and bank account for people who want support bot\
**!tworca** - (tworca = developer) sends Facebook profile of the person who created the bot\
**!koronawirus** - (koronawirus = coronavirus) sends info about coronavirus in the world (total cases, total deaths, total recovered, current cases)\
**!koronawiruspl** - (koronawirus = coronavirus) sends info about coronavirus in Poland (total cases, today cases, total deaths, recovered, current cases, cases per million, number of tests, tests per million)\
**!mem** - sends random meme\
**!luckymember** - draws and mention a random group member\
**!ruletka** - (ruletka = roulette) removes random person from group (bot must be an admin)\
**!pogoda x** - (pogoda = weather) sends weather from x place (for example !pogoda London)\
**!nick x** - changes your nick in group to x (for example !nick friend change your nick in group to friend)\  
**!everyone** - mentions everyone on group\
**!utrudnieniawroclaw** - sends difficulties in public transport in Wroclaw (Wrocław is polish city)\
**!utrudnieniawawa** - sends difficulties in public transport in Warsaw (Warsaw is polish city)\
**!utrudnienialodz** - sends difficulties in public transport in Łódź (Łódź is polish city)\
**!moneta** - (moneta = draw) bot makes coin flip\
**!film**- sends random funny film\
**!tvpis x** - (tvpis = tv station) sends TV news bar with x (for example !tvpis Hi sends bar with Hi)\
**!disco**- make disco on chat 😎 (bot changes chat color few times)\
**!emotka x** - (emotka = emoji) change group emoji to x (for example !emotka 😎 change chat emoji to 😎)\
**!powitanie x** - (powitanie = welcome) sets message which bot send when someone joins to group (for example !powitanie Hi sets welcome message to Hi)\
**!nowyregulamin x** - (nowyregulamin = new regulations) sets group regulations to x (for example !nowyregulamin be cool change group regulations to be cool)\
**!regulamin** - (regulamin = regulations) sends group regulations\
**!say x** - sends voice message (for example !say hello sends voice message where bot says hello)\
**!daily** - give you daily free virtual money\
**!top** - sends tree persons which have the biggest amount of money\
**!bal** - sends your balance\
**!bet x y** - you can bet virtual value (x is how many money you bet and y is how many % to win you have, for example !bet 10 80)\
**!tip x @mention** - you can send virtual money to your friend (for example !tip 10 @nick)
