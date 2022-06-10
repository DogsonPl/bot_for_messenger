import asyncio
import io
import pytz
from datetime import datetime

import pexpect
import aioschedule

from .sql import handling_casino_sql
from .sql.database import loop
from .parse_config import get_database_config


BACKUP_PATH = "bot_database_backup.sql"
db_config = loop.run_until_complete(get_database_config())


class LastJackpotData:
    def __init__(self):
        self.last_winner = None
        self.last_prize = None

    async def get_last_jackpot_data(self):
        _last_jackpot_data = await handling_casino_sql.get_last_jackpot_results()
        self.last_winner = _last_jackpot_data.username if _last_jackpot_data.username else _last_jackpot_data.fb_name
        self.last_prize = _last_jackpot_data.prize


def make_db_backup():
    with io.open(BACKUP_PATH, 'w', encoding="UTF-8") as file:
        command = pexpect.spawn(f"mysqldump -h {db_config.host} -u {db_config.user} -p '{db_config.database_name}'",
                                encoding="UTF-8")
        command.expect("Enter password: ")
        command.sendline(db_config.password)
        while not command.eof():
            chunk = command.readline()
            file.write(chunk)
        if command.exitstatus == 0:
            print("Database backup done\n")
        else:
            print(f"Error during creating the backup. Code: {command.exitstatus}\n")


async def run_db_backup():
    loop.run_in_executor(None, make_db_backup)


async def reset_duels():
    now = datetime.now(tz=pytz.timezone('Europe/Warsaw'))
    if now.day == 1:
        await handling_casino_sql.delete_duels_new_season()


async def tasks_scheduler():
    aioschedule.every().day.at("4:00").do(run_db_backup)
    aioschedule.every().day.at("14:20").do(run_db_backup)
    aioschedule.every().day.at("0:01").do(last_jackpot_data.get_last_jackpot_data)
    aioschedule.every().day.at("00:00").do(reset_duels)
    aioschedule.every(4).minutes.do(handling_casino_sql.reset_old_confirmations_emails)
    while True:
        loop.create_task(aioschedule.run_pending())
        await asyncio.sleep(60)


async def init():
    loop.create_task(tasks_scheduler())

last_jackpot_data = LastJackpotData()
loop.create_task(last_jackpot_data.get_last_jackpot_data())
