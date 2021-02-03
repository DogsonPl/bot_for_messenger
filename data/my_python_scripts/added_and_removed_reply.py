import json


async def added(event, mutelist):
    if event.thread.id in mutelist:
        pass
    else:
        try:
            with open(f"data\\welcome_messages\\welcome_message{event.thread.id}.json", "r") as read_file:
                welcome_message = json.load(read_file)
            await event.thread.send_text(welcome_message)
        except FileNotFoundError:
            await event.thread.send_text("Witaj w grupie! Jeśli chcesz zobaczyć moje funkcje napisz !help\nJeśli chesz ustawić wiadomość powitalną użyj komendy !powitanie")


async def removed(event, mutelist):
    if event.thread.id in mutelist:
        pass
    else:
        await event.thread.send_text("Jakaś kurwa opusciła grupe")
