import fbchat
import random as rd
from ..bot_actions import BotActions
from ..sql import handling_group_sql


def check_admin_permission(function):
    async def wrapper(self, event, group_info):
        if event.author.id not in group_info.admins:
            return await self.send_text_message(event, "🚫 Tylko administartor grupy może używać tej funkcji")
        return await function(self, event, group_info)
    return wrapper


def check_group_instance(function):
    async def wrapper(self, event):
        if not isinstance(event.thread, fbchat.Group):
            return await self.send_text_message(event, "🚫 To komenda tylko dla grup")
        group_info = await self.get_thread_info(event.thread.id)
        return await function(self, event, group_info)
    return wrapper


class GroupCommands(BotActions):
    def __init__(self, loop, bot_id, client):
        super().__init__(loop, bot_id, client)

    @check_group_instance
    @check_admin_permission
    async def delete_random_person(self, event, group_info):
        member_to_kick = rd.choice(group_info.participants).id
        if member_to_kick in group_info.admins:
            await self.send_text_message(event, "🚫 Wylosowalo admina. Nie moge go usunąć")
        elif member_to_kick == self.bot_id:
            await self.send_text_message(event, "🚫 Wylosowało mnie")
        else:
            try:
                await event.thread.remove_participant(member_to_kick)
            except fbchat.InvalidParameters:
                await self.send_text_message(event, "🚫 Żeby działała ta funkcja na grupie, muszę mieć admina")

    @check_group_instance
    @check_admin_permission
    async def set_welcome_message(self, event, group_info):
        if event.message.text == "!powitanie":
            message = "🚫 Po !powitanie ustaw treść powitania"
        else:
            await handling_group_sql.set_welcome_message(event)
            message = "✅ Powitanie zostało zmienione :)"
        await self.send_text_message(event, message)

    @check_group_instance
    @check_admin_permission
    async def set_new_group_regulations(self, event, group_info):
        await handling_group_sql.set_group_regulations(event)
        await self.send_text_message(event, "✅ Regulamin został zmieniony :) Użyj komendy !regulamin by go zobaczyć")

    @check_group_instance
    async def get_group_regulations(self, event, group_info):
        group_regulations = await handling_group_sql.fetch_group_regulations(event)
        await self.send_text_message(event, group_regulations)

    @check_group_instance
    @check_admin_permission
    async def mention_everyone(self, event, group_info):
        mentions = [fbchat.Mention(thread_id=participant.id, offset=0, length=12) for participant in group_info.participants]
        await self.send_text_message_with_mentions(event, "💬 ELUWA ALL", mentions)

    @check_group_instance
    async def send_message_with_random_mention(self, event, group_info):
        group_info = await self.get_thread_info(event.thread.id)
        mention = await get_random_mention(group_info)
        await self.send_text_message_with_mentions(event, "🎆 Zwycięzca", mention)

    async def reply_on_person_added(self, event):
        message = await handling_group_sql.fetch_welcome_message(event)
        await self.send_text_message(event, message)

    async def reply_on_person_removed(self, event):
        await self.send_text_message(event, "🥂 Jakaś kurwa opusciła grupe")


async def get_random_mention(group_info):
    lucky_member = rd.choice(group_info.participants).id
    mention = [fbchat.Mention(thread_id=lucky_member, offset=0, length=12)]
    return mention
