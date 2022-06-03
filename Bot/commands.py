import threading
import time

from .commands_handling.casino_commands import CasinoCommands
from .commands_handling.group_commands import GroupCommands
from .commands_handling.normal_commands import Commands


class BotCommands(CasinoCommands, GroupCommands, Commands):
    def __init__(self, loop, bot_id, client, threads):
        super().__init__(client, bot_id, loop)
        self.sent_messages_in_thread = {}
        for i in threads:
            self.sent_messages_in_thread[str(i)] = 0
        threading.Thread(target=self.reset_sent_messages_in_thread).start()

    def reset_sent_messages_in_thread(self):
        while True:
            for i in self.sent_messages_in_thread:
                self.sent_messages_in_thread[i] = 0
            time.sleep(60)
