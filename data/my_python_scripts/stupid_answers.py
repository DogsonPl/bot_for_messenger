import random as rd


async def kurwa(event):
    kurwa_answers = ("to twoja stara", "to cie robila", "gdzie", "spierdalaj kurwo", "to twoj stary",
                     "kurwy poszukaj u siebie w domu", "kurwa to twoje imie")
    await event.thread.send_text(rd.choice(kurwa_answers))


async def co(event):
    co_answers = ("jajco", "gówno w zoo")
    await event.thread.send_text(rd.choice(co_answers))


async def Xd(event):
    await event.thread.send_text("Serio, mało rzeczy mnie triggeruje tak jak to chore „Xd”. Kombinacji x i d można używać na wiele wspaniałych sposobów. Coś cię śmieszy? Stawiasz „xD”. Coś się bardzo śmieszy? Śmiało: „XD”! Coś doprowadza Cię do płaczu ze śmiechu? „XDDD” i załatwione. Uśmiechniesz się pod nosem? „xd”. Po kłopocie.A co ma do tego ten bękart klawiaturowej ewolucji, potwór i zakała ludzkiej estetyki - „Xd”? Co to w ogóle ma wyrażać? Martwego człowieka z wywalonym jęzorem? Powiem Ci, co to znaczy. To znaczy, że masz w telefonie włączone zaczynanie zdań dużą literą, ale szkoda Ci klikać capsa na jedno „d” później. Korona z głowy spadnie? Nie sondze. „Xd” to symptom tego, że masz mnie, jako rozmówcę, gdzieś, bo Ci się nawet kliknąć nie chce, żeby mi wysłać poprawny emotikon. Szanujesz mnie? Używaj „xd”, „xD”, „XD”, do wyboru. Nie szanujesz mnie? Okaż to. Wystarczy, że wstawisz to zjebane „Xd” w choć jednej wiadomości. Nie pozdrawiam")


async def jd(event):
    jd_answers = ("jebanie disa powiększa penisa", "jebać disa", "jd", "jebać disa syna diabła", "sram na disa",
                  "dis to kurwa", "odpierdol sie od niego", "jest dobrze")
    await event.thread.send_text(rd.choice(jd_answers))


async def chuj(event):
    chuj_answers = ("chuja to masz małego", "chuja to ci stary do dupy wsadza", "chuja to ma twoja stara",
                    "chuja to ci stara w cipe wsadza", "chuja mam tak dużego że twojej starej cipę rozwaliłem")
    await event.thread.send_text(rd.choice(chuj_answers))


async def fortnite(event):
    fortnite_answers = ("fortnite to gówno", "wypierdalaj z tą grą dla debili")
    await event.thread.send_text(rd.choice(fortnite_answers))


async def pis_konfederacja(event):
    pis_answers = ["Na górze róże\nNa dole akacje\nJebać pis\nI konfederacje", "JEBAĆ PIS", "***** ***",
                   "ziobro ty kurwo jebana", "szkoda że kaczyński nie poleciał z bratem",
                   "sasin przejebał na wybory 70000mln i nie poniósł za to żadnych konsekwencji"]
    await event.thread.send_text(rd.choice(pis_answers))


async def seks(event):
    await event.message.react("❤")
