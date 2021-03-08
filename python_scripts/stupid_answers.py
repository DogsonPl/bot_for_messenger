import random as rd
from python_scripts.sending_actions import send_text_message


@send_text_message
async def kurwa(event):
    kurwa_answers = ("to twoja stara", "to cie robila", "gdzie", "spierdalaj kurwo", "to twoj stary",
                     "kurwy poszukaj u siebie w domu", "kurwa to twoje imie")
    return rd.choice(kurwa_answers)


@send_text_message
async def co(event):
    co_answers = ("jajco", "gówno w zoo")
    return rd.choice(co_answers)


@send_text_message
async def jd(event):
    jd_answers = ("jebanie disa powiększa penisa", "jebać disa", "jd", "jebać disa syna diabła", "sram na disa",
                  "dis to kurwa", "odpierdol sie od niego", "jest dobrze")
    return rd.choice(jd_answers)


@send_text_message
async def chuj(event):
    chuj_answers = ("chuja to masz małego", "chuja to ci stary do dupy wsadza", "chuja to ma twoja stara",
                    "chuja to ci stara w cipe wsadza", "chuja mam tak dużego że twojej starej cipę rozwaliłem")
    return rd.choice(chuj_answers)


@send_text_message
async def fortnite(event):
    fortnite_answers = ("fortnite to gówno", "wypierdalaj z tą grą dla debili")
    return rd.choice(fortnite_answers)


@send_text_message
async def pis_konfederacja(event):
    pis_answers = ("Na górze róże\nNa dole akacje\nJebać pis\nI konfederacje", "JEBAĆ PIS", "***** ***",
                   "ziobro ty kurwo jebana", "szkoda że kaczyński nie poleciał z bratem",
                   "sasin przejebał na wybory 70 milionów i nie poniósł za to żadnych konsekwencji")
    return rd.choice(pis_answers)
