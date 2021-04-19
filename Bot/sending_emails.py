import random as rd
import aiosmtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from . import parse_config


async def get_confirmation_code():
    confirmation_code = rd.randint(10000, 99999)
    return confirmation_code


class SmptConnection:
    def __init__(self):
        self.smpt_connection = aiosmtplib.SMTP(hostname=hostname, port=465, use_tls=True)
        loop.run_until_complete(self.smpt_connection.connect())
        loop.run_until_complete(self.smpt_connection.ehlo())
        loop.run_until_complete(self.smpt_connection.login(mail, password))

    async def send_mail(self, receiver, code):
        message = MIMEMultipart("alternative")
        message["From"] = mail
        message["To"] = receiver
        message["Subject"] = "Kod potwierdzający"
        message.attach(MIMEText(f"""<html><body><h1>Twój kod to {code}</h1>
Wpisz komendę !kod {code}. Kod wygaśnie za godzinę</body></html>""", "html", "utf-8"))
        try:
            await self.smpt_connection.send_message(message)
            return f"Wysłano email z kodem do {receiver}"
        except aiosmtplib.errors.SMTPRecipientsRefused:
            return "Nie udało się wysłać emaila. Czy na pewno podałeś poprawny email?"


loop = asyncio.get_event_loop()
hostname, mail, password = loop.run_until_complete(parse_config.get_smpt_config())
smpt_connection = SmptConnection()