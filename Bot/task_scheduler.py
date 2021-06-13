import asyncio
import io
import pexpect
import aioschedule
from .sql import handling_casino_sql
from .sql.database import loop
from .parse_config import get_database_config


BACKUP_PATH = "bot_database_backup.sql"
HOST, USER, PASSWORD, DATABASE_NAME, PORT = loop.run_until_complete(get_database_config())


class LastJackpotData:
    def __init__(self):
        self.last_winner = None
        self.last_prize = None

    async def get_last_jackpot_data(self):
        _last_jackpot_data = await handling_casino_sql.get_last_jackpot_results()
        self.last_winner = _last_jackpot_data[0] if _last_jackpot_data[0] else _last_jackpot_data[1]
        self.last_prize = _last_jackpot_data[2]


def make_db_backup():
    with io.open(BACKUP_PATH, 'w', encoding="UTF-8") as file:
        command = pexpect.spawn(f"mysqldump -h {HOST} -u {USER} -p '{DATABASE_NAME}'", encoding="UTF-8")
        command.expect("Enter password: ")
        command.sendline(PASSWORD)
        while not command.eof():
            chunk = command.readline()
            file.write(chunk)
        if command.exitstatus == 0:
            print("Database backup done\n")
        else:
            print(f"Error during creating the backup. Code: {command.exitstatus}\n")


async def run_db_backup():
    loop.run_in_executor(None, make_db_backup)


async def tasks_scheduler():
    aioschedule.every().day.at("4:00").do(run_db_backup)
    aioschedule.every().day.at("14:20").do(run_db_backup)
    aioschedule.every().day.at("0:01").do(last_jackpot_data.get_last_jackpot_data)
    aioschedule.every(4).minutes.do(handling_casino_sql.reset_old_confirmations_emails)
    while True:
        loop.create_task(aioschedule.run_pending())
        await asyncio.sleep(60)


async def init():
    loop.create_task(tasks_scheduler())

last_jackpot_data = LastJackpotData()
loop.create_task(last_jackpot_data.get_last_jackpot_data())
