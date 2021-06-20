from .database import cursor


async def set_group_regulations(event):
    await cursor.execute("""INSERT INTO groups_information(group_id, regulations) 
                            VALUES(%s, %s) AS new_values
                            ON DUPLICATE KEY
                            UPDATE regulations = new_values.regulations;""", (event.thread.id, event.message.text[15:]))


async def set_welcome_message(event):
    await cursor.execute("""INSERT INTO groups_information(group_id, welcome_message) 
                            VALUES(%s, %s) AS new_values
                            ON DUPLICATE KEY
                            UPDATE welcome_message = new_values.welcome_message;""", (event.thread.id, event.message.text[10:]))


async def fetch_group_regulations(event):
    try:
        data = await cursor.fetch_data("""SELECT regulations FROM groups_information
                                          WHERE group_id = %s LIMIT 1;""", (event.thread.id, ))
        group_regulations = data[0][0]
    except IndexError:
        group_regulations = "📜 Grupa nie ma regulaminu. Aby go ustawić użyj komendy\n!nowyregulamin 'treść'"
    return group_regulations


async def fetch_welcome_message(event):
    data = await cursor.fetch_data("""SELECT welcome_message FROM groups_information
                                      WHERE group_id = %s LIMIT 1;""", (event.thread.id, ))
    try:
        message = data[0][0]
    except IndexError:
        message = """🥂 Witaj w grupie! Jeśli chcesz zobaczyć moje funkcje napisz !help 
Jeśli chesz ustawić wiadomość powitalną użyj komendy !powitanie"""
    return message
