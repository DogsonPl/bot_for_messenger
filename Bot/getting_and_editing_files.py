from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random as rd
import os

MEMES_FILES = os.listdir("Bot//media//memes")
FILMS_FILES = os.listdir("Bot//media//films")
FONT = ImageFont.truetype("Bot//media//fonts/FallingSkySemibold-Bn7B.otf", 15)


async def get_random_meme():
    drawn_meme = rd.choice(MEMES_FILES)
    return "Bot//media//memes//" + drawn_meme, "image/png"


async def get_random_film():
    drawn_film = rd.choice(FILMS_FILES)
    return "Bot//media//films//" + drawn_film, "video/mp4"


async def make_coin_flip():
    selected = rd.choice(["Bot//media//orzel_reszka//orzel.png", "Bot//media//orzel_reszka//reszka.png"])
    return selected, "image/png"


def edit_tvpis_image(text):
    if text == "":
        return "Napisz coś po !tvpis, np !tvpis jebać pis", None

    if len(text) > 46:
        text = text[0:46].upper()
    else:
        text = text.upper()

    tvpis_image = Image.open("Bot//media//tvpis//img.png")
    draw = ImageDraw.Draw(tvpis_image)
    draw.text((72, 176), text, (255, 255, 255), FONT)
    bytes_image = BytesIO()
    tvpis_image.save(bytes_image, format='PNG')
    return bytes_image, "image/jpeg"


def get_tts(text):
    if len(text) > 1500:
        return "Wiadomość może mieć maksymalnie 1500 znaków (musiałem zrobić te ograniczenie bo bot się za bardzo lagował)"
    if text == "":
        return "Po !say napisz coś co ma powiedzieć bot, np !say elo"

    tts = gTTS(text, lang="pl")
    bytes_object = BytesIO()
    try:
        tts.write_to_fp(bytes_object)
    except AssertionError:
        return "Podano niepoprawne znaki"
    return bytes_object
