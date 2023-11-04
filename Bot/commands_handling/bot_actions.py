import asyncio

import aiofiles
import fbchat

ADD_TO_EVERY_MESSAGE: str = f"""\n🇺🇦 #StandWithUkraine"""


def check_sent_messages_in_thread(function):
    async def wrapper(self, event: fbchat.MessageEvent, *args, **kwargs):
        try:
            if self.sent_messages_in_thread[event.thread.id] < 20:
                self.sent_messages_in_thread[event.thread.id] += 1
            else:
                return
        except KeyError:
            self.sent_messages_in_thread[event.thread.id] = 1
        return await function(self, event, *args, **kwargs)
    return wrapper


class BotActions:
    client: fbchat.Client
    bot_id: str
    loop: asyncio.AbstractEventLoop

    def __init__(self, client: fbchat.Client, bot_id: str, loop: asyncio.AbstractEventLoop):
        self.client = client
        self.bot_id = bot_id
        self.loop = loop

    @check_sent_messages_in_thread
    async def send_text_message(self, event: fbchat.MessageEvent, message_text: str,
                                mentions=None, reply_to_id: str = None):
        message_text += ADD_TO_EVERY_MESSAGE
        if self.sent_messages_in_thread[event.thread.id] == 19:
            message_text += "\nWprowadzono limit na ilość wysyłanych wiadomości przez bota, jeśli nie odpowiada należy poczekać minute (nawet jak bot nie wyśle wiadomości, bety są wykonywane)"
        await event.thread.send_text(message_text, mentions=mentions, reply_to_id=reply_to_id)

    @check_sent_messages_in_thread
    async def send_file(self, event: fbchat.MessageEvent, file_path: str, filetype: str):
        async with aiofiles.open(file_path, "rb") as file:
            files = await self.client.upload([(file_path, file, filetype)])
        await event.thread.send_files(files)

    @check_sent_messages_in_thread
    async def send_bytes_file(self, event: fbchat.MessageEvent, file, filetype: str):
        try:
            if type(file) == list:
                files = await self.client.upload([("image.jpeg", i.getvalue(), filetype) for i in file])
            else:
                files = await self.client.upload([("image.jpeg", file.getvalue(), filetype)])
            await event.thread.send_files(files)
        except AttributeError:
            await self.send_text_message(event, file, reply_to_id=event.message.id)

    @check_sent_messages_in_thread
    async def send_bytes_audio_file(self, event: fbchat.MessageEvent, file):
        try:
            files = await self.client.upload([("audio.pm3", file.getvalue(), "audio/mp3")], voice_clip=True)
            await event.thread.send_files(files)
        except AttributeError:
            await self.send_text_message(event, file, reply_to_id=event.message.id)

    async def get_thread_info(self, thread_id: str):
        return await self.client.fetch_thread_info([thread_id]).__anext__()
