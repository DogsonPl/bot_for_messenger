import random as rd


async def kurwa(event):
    kurwa_answers = ("to twoja stara", "to cie robila", "gdzie", "spierdalaj kurwo", "to twoj stary", "kurwy poszukaj u siebie w domu","kurwa to twoje imie")
    answer = kurwa_answers[rd.randint(0, len(kurwa_answers) - 1)]
    await event.thread.send_text(answer)


async def co(event):
    co_answers = ("jajco", "gówno w zoo")
    answer = co_answers[rd.randint(0, len(co_answers) - 1)]
    await event.thread.send_text(answer)


async def Xd(event):
    await event.thread.send_text("Serio, mało rzeczy mnie triggeruje tak jak to chore „Xd”. Kombinacji x i d można używać na wiele wspaniałych sposobów. Coś cię śmieszy? Stawiasz „xD”. Coś się bardzo śmieszy? Śmiało: „XD”! Coś doprowadza Cię do płaczu ze śmiechu? „XDDD” i załatwione. Uśmiechniesz się pod nosem? „xd”. Po kłopocie.A co ma do tego ten bękart klawiaturowej ewolucji, potwór i zakała ludzkiej estetyki - „Xd”? Co to w ogóle ma wyrażać? Martwego człowieka z wywalonym jęzorem? Powiem Ci, co to znaczy. To znaczy, że masz w telefonie włączone zaczynanie zdań dużą literą, ale szkoda Ci klikać capsa na jedno „d” później. Korona z głowy spadnie? Nie sondze. „Xd” to symptom tego, że masz mnie, jako rozmówcę, gdzieś, bo Ci się nawet kliknąć nie chce, żeby mi wysłać poprawny emotikon. Szanujesz mnie? Używaj „xd”, „xD”, „XD”, do wyboru. Nie szanujesz mnie? Okaż to. Wystarczy, że wstawisz to zjebane „Xd” w choć jednej wiadomości. Nie pozdrawiam")


async def jd(event):
    jd_answers = ("jebanie disa powiększa penisa", "jebać disa", "jd", "jebać disa syna diabła", "sram na disa", "dis to kurwa", "odpierdol sie od niego", "jest dobrze")
    answer = jd_answers[rd.randint(0, len(jd_answers) - 1)]
    await event.thread.send_text(answer)


async def chuj(event):
    chuj_answers = ("chuja to masz małego", "chuja to ci stary do dupy wsadza", "chuja to ma twoja stara", "chuja to ci stara w cipe wsadza", "chuja mam tak dużego że twojej starej cipę rozwaliłem")
    answer = chuj_answers[rd.randint(0, len(chuj_answers) - 1)]
    await event.thread.send_text(answer)


async def fortnite(event):
    fortnite_answers = ("fortnite to gówno", "wypierdalaj z tą grą dla downów")
    answer = fortnite_answers[rd.randint(0, len(fortnite_answers) - 1)]
    await event.thread.send_text(answer)

async def pis_konfederacja(event):
    pis_answers = ["Na górze róże\nNa dole akacje\nJebać pis\nI konfederacje", "JEBAĆ PIS", "***** ***", "Ziobro ty kurwo jebana"]
    answer = pis_answers[rd.randint(0, len(pis_answers)-1)]
    await event.thread.send_text(answer)


async def seks(event):
    await event.message.react("❤")
