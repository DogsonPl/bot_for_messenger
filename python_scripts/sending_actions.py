import aiofiles
from fbchat import Group


def send_text_message(function):
    async def decorator(event, client):
        message = await function(event)
        await event.thread.send_text(message)
    return decorator


def send_text_message_with_mentions(function):
    async def decorator(event, client):
        message, mentions = await function(event)
        await event.thread.send_text(message, mentions=mentions)
    return decorator


def send_text_message_with_reply(function):
    async def decorator(event, client):
        message = await function(event)
        await event.thread.send_text(message, reply_to_id=event.message.id)
    return decorator


def send_file(function):
    async def decorator(event, client):
        path_to_file, filetype = await function()
        try:
            async with aiofiles.open(path_to_file, "rb") as file:
                files = await client.upload([(path_to_file, file, filetype)])
            await event.thread.send_files(files)
        except FileNotFoundError:
            await event.thread.send_text(path_to_file)
    return decorator


def send_bytes_file(function):
    async def decorator(event, client):
        file, filetype = await function(event)
        try:
            files = await client.upload([("image.jpeg", file.getvalue(), filetype)])
            await event.thread.send_files(files)
        except AttributeError:
            await event.thread.send_text(file)
    return decorator


def send_bytes_audio_file(function):
    async def decorator(event, client):
        file = await function(event)
        try:
            files = await client.upload([("audio.pm3", file.getvalue(), "audio/mp3")], voice_clip=True)
            await event.thread.send_files(files)
        except AttributeError:
            await event.thread.send_text(file)
    return decorator


def group_actions(function):
    async def decorator(event, client, admin_required=True, *args):
        if not isinstance(event.thread, Group):
            return await event.thread.send_text("To komenda tylko dla grup")
        group_info = await client.fetch_thread_info([event.thread.id]).__anext__()
        if admin_required:
            if event.author.id not in group_info.admins:
                return await event.thread.send_text("Tylko administartor grupy może używać tej funkcji")
        return await function(event, group_info, *args)
    return decorator


def run_in_executor(function):
    # todo pomysl czy lepsze jest to czy dekoratory
    async def decorator(event, client, loop, *args):
        return await loop.run_in_executor(None, function, *event)
