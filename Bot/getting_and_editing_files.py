from io import BytesIO
import random as rd
import os

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import emoji

MEMES_DIR = "Bot//media//memes"
FILMS_DIR = "Bot//media//films"
MONEY_FLIP_DIR = "Bot//media//orzel_reszka"

MEMES_FILES = [os.path.join(MEMES_DIR, i) for i in os.listdir(MEMES_DIR)]
FILMS_FILES = [os.path.join(FILMS_DIR, i) for i in os.listdir(FILMS_DIR)]
COIN_FLIP_FILES = [os.path.join(MONEY_FLIP_DIR, i) for i in os.listdir(MONEY_FLIP_DIR)]
FONT = ImageFont.truetype("Bot//media//fonts/FallingSkySemibold-Bn7B.otf", 15)

EMOJI_LIST = emoji.UNICODE_EMOJI_ENGLISH


async def get_random_meme():
    drawn_meme = rd.choice(MEMES_FILES)
    return drawn_meme, "image/png"


async def get_random_film():
    drawn_film = rd.choice(FILMS_FILES)
    return drawn_film, "video/mp4"


async def make_coin_flip():
    selected = rd.choice(COIN_FLIP_FILES)
    return selected, "image/png"


def edit_tvpis_image(text):
    if text == "":
        return "🚫 Napisz coś po !tvpis, np !tvpis jebać pis", None

    # image can have max 46 letters
    text = text[:46].upper().replace("\n", " ")

    tvpis_image = Image.open("Bot//media//tvpis//img.png")
    draw = ImageDraw.Draw(tvpis_image)
    draw.text((72, 176), text, (255, 255, 255), FONT)
    bytes_image = BytesIO()
    tvpis_image.save(bytes_image, format='PNG')
    return bytes_image, "image/jpeg"


def get_tts(text):
    for i in text:
        if i in EMOJI_LIST:
            max_len = 150
            break
    else:
        max_len = 3000

    if len(text) > max_len:
        return "🚫 Wiadomość może mieć maksymalnie 3000 znaków lub 150 jeśli posiada emotki"
    if text == "":
        return "🚫 Po !say napisz coś co ma powiedzieć bot, np !say elo"

    tts = gTTS(text, lang="pl")
    bytes_object = BytesIO()
    try:
        tts.write_to_fp(bytes_object)
    except AssertionError:
        return "🚫 Podano niepoprawne znaki"
    return bytes_object
