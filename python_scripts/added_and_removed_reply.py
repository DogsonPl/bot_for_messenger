from python_scripts.sending_actions import send_text_message
from python_scripts.sql_actions import GetInfoFromDatabase


@send_text_message
async def added(event):
    try:
        async with GetInfoFromDatabase() as db:
            await db.fetch_welcome_message(event.thread.id)
            message = db.data[0]
        return message
    except IndexError:
        return """Witaj w grupie! Jeśli chcesz zobaczyć moje funkcje napisz !help 
Jeśli chesz ustawić wiadomość powitalną użyj komendy !powitanie"""


@send_text_message
async def removed(event):
    return "Jakaś kurwa opusciła grupe"
