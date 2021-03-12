import fbchat
import random as rd
from Bot.bot_actions import BotActions
from Bot import handling_sql_actions


def check_group_admin_permission(function):
    async def wrapper(self, event):
        if not isinstance(event.thread, fbchat.Group):
            return await self.send_text_message(event, "To komenda tylko dla grup")
        group_info = await self.get_thread_info(event.thread.id)
        if event.author.id not in group_info.admins:
            return await self.send_text_message(event, "Tylko administartor grupy może używać tej funkcji")
        return await function(self, event, group_info)
    return wrapper


class GroupCommands(BotActions):
    def __init__(self, loop, bot_id, client):
        super().__init__(loop, bot_id, client)

    @check_group_admin_permission
    async def delete_random_person(self, event, group_info):
        member_to_kick = rd.choice(group_info.participants).id
        if member_to_kick in group_info.admins:
            await self.send_text_message(event, "Wylosowalo admina. Nie moge go usunąć")
        elif member_to_kick == self.bot_id:
            await self.send_text_message(event, "Wylosowało mnie")
        else:
            try:
                await event.thread.remove_participant(member_to_kick)
            except fbchat.InvalidParameters:
                await self.send_text_message(event, "Żeby działała ta funkcja na grupie, muszę mieć admina")

    @check_group_admin_permission
    async def set_welcome_message(self, event, group_info):
        if event.message.text == "!powitanie":
            message = "Po !powitanie ustaw treść powitania"
        else:
            await handling_sql_actions.set_welcome_message(event)
            message = "Powitanie zostało zmienione :)"
        await self.send_text_message(event, message)

    @check_group_admin_permission
    async def set_new_group_regulations(self, event, group_info):
        await handling_sql_actions.set_group_regulations(event)
        await self.send_text_message(event, "Regulamin został zmieniony :) Użyj komendy !regulamin by go zobaczyć")

    @check_group_admin_permission
    async def get_group_regulations(self, event, group_info):
        group_regulations = await handling_sql_actions.get_group_regulations(event)
        await self.send_text_message(event, group_regulations)

    @check_group_admin_permission
    async def mention_everyone(self, event, group_info):
        mentions = [fbchat.Mention(thread_id=participant.id, offset=0, length=9) for participant in group_info.participants]
        await self.send_text_message_with_mentions(event, "ELUWA ALL", mentions)

    async def reply_on_person_added(self, event):
        message = await handling_sql_actions.get_group_welcome_message(event)
        await self.send_text_message(event, message)

    async def reply_on_person_removed(self, event):
        await self.send_text_message(event, "Jakaś kurwa opusciła grupe")
