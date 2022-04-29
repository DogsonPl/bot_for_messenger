import threading
import time

import aiofiles


def check_sent_messages_in_thread(function):
    async def wrapper(self, event, *kwargs):
        if self.sent_messages_in_thread[event.thread.id] < 20:
            self.sent_messages_in_thread[event.thread.id] += 1
            return await function(self, event, *kwargs)
    return wrapper


class BotActions:
    def __init__(self, loop, bot_id, client, threads):
        self.loop = loop
        self.bot_id = bot_id
        self.client = client
        self.sent_messages_in_thread = {}
        for i in threads:
            self.sent_messages_in_thread[str(i)] = 0
        threading.Thread(target=self.reset_sent_messages_in_thread).start()

    def reset_sent_messages_in_thread(self):
        while True:
            for i in self.sent_messages_in_thread:
                self.sent_messages_in_thread[i] = 0
            time.sleep(60)

    @check_sent_messages_in_thread
    async def send_text_message(self, event, message_text):
        message_text += f"""\n🇺🇦 #StandWithUkraine (komenda !ukraina)
Wprowadzono limit na ilość wysyłanych wiadomości przez bota, jeśli nie odpowiada należy poczekać minute (nawet jak bot nie wyśle wiadomości, bety są wykonywane)"""
        await event.thread.send_text(message_text)

    @check_sent_messages_in_thread
    async def send_text_message_with_mentions(self, event, message_text, mentions):
        message_text += """\n🇺🇦 #StandWithUkraine (komenda !ukraina)
Wprowadzono limit na ilość wysyłanych wiadomości przez bota, jeśli nie odpowiada należy poczekać minute (nawet jak bot nie wyśle wiadomości, bety są wykonywane)"""
        await event.thread.send_text(message_text, mentions=mentions)

    @check_sent_messages_in_thread
    async def send_message_with_reply(self, event, message_text):
        message_text += """\n🇺🇦 #StandWithUkraine (komenda !ukraina)
Wprowadzono limit na ilość wysyłanych wiadomości przez bota, jeśli nie odpowiada należy poczekać minute (nawet jak bot nie wyśle wiadomości, bety są wykonywane)"""
        await event.thread.send_text(message_text, reply_to_id=event.message.id)

    @check_sent_messages_in_thread
    async def send_file(self, event, file_path, filetype):
        async with aiofiles.open(file_path, "rb") as file:
            files = await self.client.upload([(file_path, file, filetype)])
        await event.thread.send_files(files)

    @check_sent_messages_in_thread
    async def send_bytes_file(self, event, file, filetype):
        try:
            files = await self.client.upload([("image.jpeg", file.getvalue(), filetype)])
            await event.thread.send_files(files)
        except AttributeError:
            await self.send_message_with_reply(event, file)

    @check_sent_messages_in_thread
    async def send_bytes_audio_file(self, event, file):
        try:
            files = await self.client.upload([("audio.pm3", file.getvalue(), "audio/mp3")], voice_clip=True)
            await event.thread.send_files(files)
        except AttributeError:
            await self.send_message_with_reply(event, file)

    async def get_thread_info(self, thread_id):
        return await self.client.fetch_thread_info([thread_id]).__anext__()
