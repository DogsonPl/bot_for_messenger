import functools
from ..sending_emails import smpt_connection


def logger(function):
    @functools.wraps(function)
    async def wrapper(self, event, *kwargs):
        try:
            return await function(self, event, *kwargs)
        except Exception as e:
            message = f"""<b>Traceback</b>: {e} <br>
<b>Event data</b>: {event} <br>
<b>Function</b>: {function.__name__}"""
            message = await smpt_connection.create_traceback_message(message)
            await smpt_connection.send_mail("dogsonkrul@gmail.com", message)
            await self.send_text_message(event, "☠ Wystąpił błąd po stronie serwera, został on zgłoszony do administratora")
    return wrapper
