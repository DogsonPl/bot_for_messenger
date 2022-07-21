import random as rd
import asyncio

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from . import parse_config


async def get_confirmation_code() -> int:
    confirmation_code = rd.randint(10000, 99999)
    return confirmation_code


class SmptConnection:
    def __init__(self):
        self.smpt_connection = aiosmtplib.SMTP(hostname=SMTP_CONFIG.hostname, port=465, use_tls=True)

    async def connect(self):
        await self.smpt_connection.connect()
        await self.smpt_connection.ehlo()
        await self.smpt_connection.login(SMTP_CONFIG.mail, SMTP_CONFIG.password)

    async def send_mail(self, receiver: str, message: MIMEMultipart, reset: bool = False) -> str:
        try:
            await self.smpt_connection.send_message(message)
            return f"✅ Wysłano email z kodem do {receiver}"
        except aiosmtplib.errors.SMTPRecipientsRefused:
            return "🚫 Nie udało się wysłać emaila. Czy na pewno podałeś poprawny email?"
        except aiosmtplib.errors.SMTPServerDisconnected:
            if not reset:
                await self.connect()
                await self.send_mail(receiver, message, True)
            else:
                return "🚫 Nie można wysłać maila, napisz do !tworca"

    @staticmethod
    async def create_message(receiver: str, code: int) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message["From"] = SMTP_CONFIG.mail
        message["To"] = receiver
        message["Subject"] = "Kod potwierdzający"
        message.attach(MIMEText(f"""<h1>Twój kod to {code}</h1>
                                    Wpisz komendę <b>!kod {code}</b>. Kod wygaśnie za godzinę<br>
                                    Jeśli nie chciałeś połączyć tego maila z botem na Facebooku, zignoruj tego maila""",
                                "html", "utf-8"))
        return message

    @staticmethod
    async def create_traceback_message(traceback_message: str):
        message = MIMEMultipart("alternative")
        message["From"] = SMTP_CONFIG.mail
        message["To"] = "dogsonkrul@gmail.com"
        message["Subject"] = "Bot error"
        message.attach(MIMEText(traceback_message, "html", "utf-8"))
        return message


loop = asyncio.get_event_loop()
SMTP_CONFIG = loop.run_until_complete(parse_config.get_smpt_config())
smpt_connection = SmptConnection()
loop.create_task(smpt_connection.connect())
