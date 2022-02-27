import aiofiles


class BotActions:
    def __init__(self, loop, bot_id, client):
        self.loop = loop
        self.bot_id = bot_id
        self.client = client

    @staticmethod
    async def send_text_message(event, message_text):
        message_text += "\n🇺🇦 #StandWithUkraine (komenda !ukraina)"
        await event.thread.send_text(message_text)

    @staticmethod
    async def send_text_message_with_mentions(event, message_text, mentions):
        message_text += "\n🇺🇦 #StandWithUkraine (komenda !ukraina)"
        await event.thread.send_text(message_text, mentions=mentions)

    @staticmethod
    async def send_message_with_reply(event, message_text):
        message_text += "\n🇺🇦 #StandWithUkraine (komenda !ukraina)"
        await event.thread.send_text(message_text, reply_to_id=event.message.id)

    async def send_file(self, event, file_path, filetype):
        async with aiofiles.open(file_path, "rb") as file:
            files = await self.client.upload([(file_path, file, filetype)])
        await event.thread.send_files(files)

    async def send_bytes_file(self, event, file, filetype):
        try:
            files = await self.client.upload([("image.jpeg", file.getvalue(), filetype)])
            await event.thread.send_files(files)
        except AttributeError:
            await self.send_message_with_reply(event, file)

    async def send_bytes_audio_file(self, event, file):
        try:
            files = await self.client.upload([("audio.pm3", file.getvalue(), "audio/mp3")], voice_clip=True)
            await event.thread.send_files(files)
        except AttributeError:
            await self.send_message_with_reply(event, file)

    async def get_thread_info(self, thread_id):
        return await self.client.fetch_thread_info([thread_id]).__anext__()
