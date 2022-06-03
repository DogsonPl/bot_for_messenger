import random as rd
import asyncio

import fbchat

from .logger import logger
from .bot_actions import BotActions
from ..sql import handling_group_sql


BOT_WELCOME_MESSAGE = """👋 Witajcie, jestem botem 🤖
❓ Jeśli chcesz zobaczyć moje komendy napisz !help"""


def check_admin_permission(function):
    async def wrapper(self, event: fbchat.MessageEvent, group_info: fbchat.GroupData):
        if event.author.id not in group_info.admins:
            return await self.send_text_message(event, "🚫 Tylko administartor grupy może używać tej funkcji",
                                                reply_to_id=event.message.id)
        return await function(self, event, group_info)
    return wrapper


def check_group_instance(function):
    async def wrapper(self, event: fbchat.MessageEvent):
        if not isinstance(event.thread, fbchat.Group):
            return await self.send_text_message(event, "🚫 To komenda tylko dla grup", reply_to_id=event.message.id)
        group_info = await self.get_thread_info(event.thread.id)
        return await function(self, event, group_info)
    return wrapper


class GroupCommands(BotActions):
    def __init__(self, client: fbchat.Client, bot_id: str, loop: asyncio.AbstractEventLoop):
        super().__init__(client, bot_id, loop)

    @logger
    @check_group_instance
    @check_admin_permission
    async def delete_random_person(self, event: fbchat.MessageEvent, group_info: fbchat.GroupData):
        member_to_kick = rd.choice(group_info.participants).id
        if member_to_kick in group_info.admins:
            await self.send_text_message(event, "🚫 Wylosowalo admina. Nie moge go usunąć", reply_to_id=event.message.id)
        elif member_to_kick == self.bot_id:
            await self.send_text_message(event, "🚫 Wylosowało mnie", reply_to_id=event.message.id)
        else:
            try:
                await event.thread.remove_participant(member_to_kick)
            except fbchat.InvalidParameters:
                await self.send_text_message(event, "🚫 Żeby działała ta funkcja na grupie, muszę mieć admina",
                                             reply_to_id=event.message.id)

    @logger
    @check_group_instance
    @check_admin_permission
    async def set_welcome_message(self, event: fbchat.MessageEvent, group_info: fbchat.GroupData):
        if event.message.text.lower() == "!powitanie":
            message = "🚫 Po !powitanie ustaw treść powitania"
        else:
            await handling_group_sql.set_welcome_message(event)
            message = "✅ Powitanie zostało zmienione :)"
        await self.send_text_message(event, message)

    @logger
    @check_group_instance
    @check_admin_permission
    async def set_new_group_regulations(self, event: fbchat.MessageEvent, group_info: fbchat.GroupData):
        if event.message.text.lower() == "!nowyregulamin":
            message = "🚫 Po !nowyregulamin ustaw treść regulaminu"
        else:
            await handling_group_sql.set_group_regulations(event)
            message = "✅ Regulamin został zmieniony :) Użyj komendy !regulamin by go zobaczyć"
        await self.send_text_message(event, message)

    @logger
    @check_group_instance
    async def get_group_regulations(self, event: fbchat.MessageEvent, group_info: fbchat.GroupData):
        group_regulations = await handling_group_sql.fetch_group_regulations(event)
        if group_regulations is None:
            group_regulations = "📜 Grupa nie ma regulaminu. Aby go ustawić użyj komendy\n!nowyregulamin 'treść'"
        await self.send_text_message(event, group_regulations)

    @logger
    @check_group_instance
    @check_admin_permission
    async def mention_everyone(self, event: fbchat.MessageEvent, group_info: fbchat.GroupData):
        mentions = [fbchat.Mention(thread_id=participant.id, offset=0, length=12) for participant in group_info.participants]
        await self.send_text_message(event, "💬 ELUWA ALL", mentions=mentions)

    @logger
    @check_group_instance
    async def send_message_with_random_mention(self, event: fbchat.MessageEvent, group_info: fbchat.GroupData):
        lucky_member = rd.choice(group_info.participants).id
        mention = [fbchat.Mention(thread_id=lucky_member, offset=0, length=12)]
        await self.send_text_message(event, "🎆 Zwycięzca", mentions=mention, reply_to_id=event.message.id)

    @logger
    @check_group_instance
    async def send_love_message(self, event: fbchat.MessageEvent, group_info: fbchat.GroupData):
        try:
            first_person, second_person = event.message.mentions
        except ValueError:
            await self.send_text_message(event, "💡 Po !kocha oznacz dwie osoby, np !kocha @nick1 @nick2")
        else:
            love_percent = rd.randint(0, 100)
            if love_percent <= 25:
                emoji = "💔"
            elif love_percent <= 50:
                emoji = "💛"
            elif love_percent <= 75:
                emoji = "❤"
            else:
                emoji = "💝💘"
            first_person_name = event.message.text[8:first_person.length+7]
            second_person_name = event.message.text[9+first_person.length:8+first_person.length+second_person.length]
            await self.send_text_message(event, f"{emoji} {first_person_name} kocha {second_person_name} w {love_percent} procentach")

    @logger
    async def reply_on_person_removed(self, event):
        if self.bot_id != event.removed.id:
            # if bot is removed from group, bot can`t send removed message
            await self.send_text_message(event, "🥂 Jakaś kurwa opusciła grupe")

    @logger
    async def send_message_on_person_added(self, event):
        for user in event.added:
            if user.id == self.bot_id:
                await self.send_text_message(event, BOT_WELCOME_MESSAGE)
                break
        else:
            message = await handling_group_sql.fetch_welcome_message(event)
            if message is None:
                message = """🥂 Witaj w grupie! Jeśli chcesz zobaczyć moje funkcje napisz !help 
Jeśli chesz ustawić wiadomość powitalną użyj komendy !powitanie"""
            await self.send_text_message(event, message)
