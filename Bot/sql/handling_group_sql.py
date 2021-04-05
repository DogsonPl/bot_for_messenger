from .connection import database


async def set_group_regulations(event):
    await database.execute("""INSERT INTO groups_information(group_id, regulations) 
                              VALUES(?, ?)
                              ON CONFLICT (group_id) DO
                              UPDATE SET regulations=excluded.regulations;""", (event.thread.id, event.message.text[10:]))


async def set_welcome_message(event):
    await database.execute("""INSERT INTO groups_information(group_id, welcome_message) 
                              VALUES(?, ?)
                              ON CONFLICT (group_id) DO
                              UPDATE SET welcome_message=excluded.welcome_message;""", (event.thread.id, event.message.text[15:]))


async def fetch_group_regulations(event):
    try:
        data = await database.fetch_data("""SELECT regulations FROM groups_information
                                             WHERE group_id = ?;""", event.thread.id)
        group_regulations = data[0]
    except IndexError:
        group_regulations = "📜 Grupa nie ma regulaminu. Aby go ustawić użyj komendy\n!nowyregulamin 'treść'"
    return group_regulations


async def fetch_welcome_message(event):
    try:
        data = await database.fetch_data("""SELECT welcome_message FROM groups_information
                                             WHERE group_id = ?;""", event.thread.id)
        message = data[0]
    except IndexError:
        message = """🥂 Witaj w grupie! Jeśli chcesz zobaczyć moje funkcje napisz !help 
    Jeśli chesz ustawić wiadomość powitalną użyj komendy !powitanie"""
    return message
